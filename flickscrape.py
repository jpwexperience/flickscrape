import os, sys, re, csv, requests, lxml, urllib3
from bs4 import BeautifulSoup

sovietMovies = []
skippedFlicks = []
base = "https://sovietmoviesonline.com/"
link = base + "all_movies.html"

class Flick():
    badFile = 1
    badSrt = 1
    fileSize = 0.01
    srtSize = 0.01
    downloadUrl = ""
    srtUrl = ""
    name = ""
    year = ""
    imdb = ""
    og = ""
    director = ""

    def __init__(self, url, num):
        self.url = url
        self.num = num

    def __str__(self):
        string = (
            "URL: " + self.url + "\n" + 
            "Download Url: " + self.downloadUrl + "\n" +
            "Sub Url: " + self.srtUrl + "\n" +
            "File Size: " + str(self.fileSize / 1000000000) + " gb\n" +
            "SRT Size: " + str(self.fileSize) + "\n" +
            "Original Name: " + self.og + "\n" +
            "Year: " + self.year + "\n" +
            "IMDB: " + self.imdb + "\n" +
            "Director: " + self.director
            )
        return string

def errMsg(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

def writeCsv():
    print("not yet")

#Flicks are initialized to not download.
#Cuts redundancy setting Flick
def downloadInit(flick):
    r = requests.get(flick.downloadUrl)
    if r.status_code == requests.codes.ok:
        flickHead = requests.head(flick.downloadUrl)
        srtHead = requests.head(flick.srtUrl)
        try:
            flick.srtSize = int(srtHead.headers['content-length'])
            flick.badSrt = 0
        except KeyError:
            errMsg("Key Error: " + flick.srtUrl)
        try:
            flick.fileSize = int(flickHead.headers['content-length'])
            flick.badFile = 0 
        except KeyError:
            errMsg("Key Error: " + flick.downloadUrl)
    else:
        errMsg("Bad Request Code (ie 404): " + flick.downloadUrl)

#Scrape info from html page and create flick object
#Any content not found is simply skipped
#Assumptions: 
#   First Table Found Contains: Original Title, IMDB, Views, Year
#   first <div class="director">...</div> contains films director
#   There is <div id="error404">...</div> of 404 pages
def processFilm(flick):
    global link
    global base
    flickUrl = flick.url
    num = flick.num
    filmReq = requests.get(flickUrl)
    filmSource = filmReq.text
    soup = BeautifulSoup(filmSource, "lxml")

    for i in soup.find_all('div'):
        if i.id == "error404":
            skippedFlicks.append(flick)
            return
    if filmReq.status_code == requests.codes.ok:
        try:
            director = soup.find_all('div', {'class': ['director']})
            try:
                flick.director = director[0].a.contents[0]
            except IndexError:
                errMsg("Director not found: " + flickUrl)

            table = soup.find_all('table')
            try:
                td = table[0].find_all('td')
                try:
                    flick.og = td[0].contents[1].strip()
                except IndexError:
                    errMsg("Original Title not found.")
                try:
                    flick.imdb = td[1].contents[1].strip()
                except IndexError:
                    errMsg("IMDB rating not found.")
                #Number of views is td[2].contents[1] hence the jump
                try:
                    flick.year = td[3].contents[1].strip()
                except IndexError:
                    errMsg("Release Year not found.")
                    return
            except IndexError:
                errMsg("Error finding <td>'s, skipping: " + flickUrl)
                skippedFlicks.append(flick)

        except AttributeError:
            errMsg("Attribute Error, skipping: " + flickUrl)
            skippedFlicks.append(flick)
            return

    else:
        errMsg("Bad request code on flick page, skipping: " + flickUrl)
        skippedFlicks.append(flick)
        return

    #Segmenting these strings more because I know these links aren't always perfect
    #ie if film has two parts it may be <num>-1.mp4 and <num>-2.mp4
    downloadBase = base + "movies/" + str(flick.num)
    flick.downloadUrl = downloadBase + ".mp4"
    flick.srtUrl = downloadBase + ".srt"
    downloadInit(flick)

    if flick.badFile == 1:
        skippedFlicks.append(flick)
    else:
        sovietMovies.append(flick)

def main():
    print("--- Extracting Film Links ---")
    global link
    #global sovietMovies
    sovietRequest = requests.get(link)
    data = sovietRequest.text
    soup = BeautifulSoup(data, "lxml")
    allLinks = [] #links before removing dupes
    links = [] #links after remove dupes
    tempDict = {
            "url": "",
            "num": 1,
    }
    for link in soup.find_all('a'):
        tempUrl = link.get('href')
        #make sure it's a proper film link and not blog
        movieRegex = re.escape(base) + r"(?!blog).*\.html"
        match = re.match(movieRegex, tempUrl)
        if match:
            tempSplit = tempUrl.split('/')
            movieBase = tempSplit[len(tempSplit) - 1] 
            baseSplit = movieBase.split('-')
            num = baseSplit[0]
            linkInfo = tempDict.copy()
            linkInfo["url"] = tempUrl
            linkInfo["num"] = int(num)
            allLinks.append(linkInfo)

    #Check for duplicate links
    seen = set()
    for x in allLinks:
        if x["num"] not in seen:
            links.append(x)
            seen.add(x["num"])

    print("--- Processing Flicks ---")
    for i in range(0, 1, 1):
        tempFlick = Flick(links[i]["url"], links[i]["num"])
        processFilm(tempFlick)

    #for movie in links:
    #    tempFlick = Flick(movie["url"], movie["num"])
    #    processFilm(tempFlick)
    
    print("--- Flicks to Download ---")
    for i in sovietMovies:
        print(i)
    print("--- Flicks to Skip ---")
    for i in skippedFlicks:
        print(i)

if __name__ == "__main__":
    main()
