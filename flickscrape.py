#!/usr/bin/python3

import os, sys, re, math, csv, requests 
import lxml
from bs4 import BeautifulSoup

sovietMovies = []
skippedFlicks = []
base = "https://sovietmoviesonline.com/"
link = base + "all_movies.html"

class Flick:
    badFile = True
    badSrt = True
    fileSize = 0.0
    srtSize = 0.0
    title = ""
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
            "Title: " + self.title + "\n" +
            "Download Url: " + self.downloadUrl + "\n" +
            "Sub Url: " + self.srtUrl + "\n" +
            "File Size: " + str(self.fileSize / 1000000000) + " gb\n" +
            "SRT Size: " + str(self.fileSize / 1000) + " mb\n" +
            "Bad File: " + str(self.badFile) + "\n" +
            "Bad SRT: " + str(self.badSrt) + "\n" +
            "Original Name: " + self.og + "\n" +
            "Year: " + self.year + "\n" +
            "IMDB: " + self.imdb + "\n" +
            "Director: " + self.director
            )
        return string

def csvOut(flick):
    csvString = ""
    csvString += flick.title + "|"
    csvString += flick.year + "|"
    csvString += flick.director + "|"
    csvString += flick.imdb + "|"
    csvString += flick.og + "|"
    csvString += str(flick.fileSize / 1000000000) + "|"
    csvString += str(flick.srtSize / 1000) + "|"
    csvString += flick.url + "|"
    csvString += flick.downloadUrl + "|"
    csvString += flick.srtUrl + "|"
    csvString += str(flick.badFile) + "|"
    csvString += str(flick.badSrt) + "\n"
    return csvString

def errMsg(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

#Try and download flick and english subtitles
def downloadFlicks(flick):
    d = os.path.realpath(__file__)
    baseDir = d.rsplit('/', 1)
    download = flick.downloadUrl
    chunkSize = 1024 * 1024
    h = requests.head(flick.downloadUrl, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        print("Not downloadable")
    elif 'html' in content_type.lower():
        print("Not downloadable")
    else:
        if flick.badFile == 1:
            print("Bad Movie File Set, skipping...")
        else:
            titleNoSpace = flick.title.replace(' ', '_')
            newDir = baseDir[0] + "/" + titleNoSpace
            if not os.path.isdir(newDir):
                os.mkdir(newDir)
            print("Downloading: " + flick.downloadUrl)
            r = requests.get(flick.downloadUrl, stream=True)
            with open((newDir + "/" + titleNoSpace  + '.mp4'), 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunkSize):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            if flick.badSrt == 1:
                print("Bad Srt set, skipping...")
            else:
                r = requests.get(flick.srtUrl, stream=True)
                with open((newDir + "/" + titleNoSpace  + '.srt'), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)

#Creates CSV file containg film information
#Defaults to this script's directory
def writeCsv():
    d = os.path.realpath(__file__)
    scriptDir = d.rsplit('/', 1)
    scriptDir = scriptDir[0]
    csvName = scriptDir + "/flickscrape-output"
    x = 1
    csvPath = csvName + ".csv"
    while True:
        if os.path.exists(csvPath):
            csvPath = csvName + "_" + str(x) + ".csv"
            x += 1
        else:
            break
    f = open(csvPath, "w")
    startLine = "Title|Year|Director|IMDb Score|Russian Title|Flick Size (in GB)|SRT Size (KB)|Flick URL|Download url|SRT url|Bad File|Bad Subtitles\n"
    f.write(startLine)
    for flick in sovietMovies:
        print(csvOut(flick))
        f.write(csvOut(flick))
    for flick in skippedFlicks:
        flick.fileSize = 0
        flick.srtSize = 0
        f.write(csvOut(flick))

#Flicks are initialized to not download.
#Cuts redundancy setting Flick
def downloadInit(flick):
    flickHead = requests.head(flick.downloadUrl)
    srtHead = requests.head(flick.srtUrl)
    try:
        flick.srtSize = int(srtHead.headers['content-length'])
        flick.badSrt = False
    except KeyError:
        errMsg("Key Error: " + flick.srtUrl)
    try:
        flick.fileSize = int(flickHead.headers['content-length'])
        flick.badFile = False 
    except KeyError:
        errMsg("Key Error: " + flick.downloadUrl)

#Scrape info from html page and create flick object
#Any content not found is simply skipped
#Assumptions: 
#   First Table Found Contains: Original Title, IMDB, Views, Year
#   first <div class="director">...</div> contains films director
#   There is <div id="error404">...</div> on 404 pages
def processFilm(flick):
    global link
    global base
    
    #Segmenting these strings more because I know these links aren't always perfect
    #ie if film has two parts it may be <num>-1.mp4 and <num>-2.mp4
    downloadBase = base + "movies/" + str(flick.num)
    flick.downloadUrl = downloadBase + ".mp4"
    flick.srtUrl = downloadBase + ".srt"
    downloadInit(flick)

    flickUrl = flick.url
    num = flick.num
    filmReq = requests.get(flickUrl)
    filmSource = filmReq.text
    soup = BeautifulSoup(filmSource, "lxml")
    for i in soup.find_all('div'):
        if i.id == "error404":
            skippedFlicks.append(flick)
            return

    try:
        flickTitle = soup.find_all('h1')
        flick.title = flickTitle[0].contents[0]
    except IndexError:
        errMsg("Flick Title not found: " + flickUrl)
        skippedFlicks.append(flick)
        return
    if filmReq.status_code == requests.codes.ok:
        try:
            #May be able to pull director data from Flick text on page
            #<div class="movie-description">...</div>
            director = soup.find('div', {'class': ['director']}).contents[0].contents[0]
            flick.director = director
        except (IndexError, AttributeError):
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
    else:
        errMsg("Bad request code on flick page, skipping: " + flickUrl)
        skippedFlicks.append(flick)
        return



    if flick.badFile == True:
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
    #for i in range(0, 2, 1):
    #    tempFlick = Flick(links[i]["url"], links[i]["num"])
    #    processFilm(tempFlick)

    for movie in links:
        tempFlick = Flick(movie["url"], movie["num"])
        processFilm(tempFlick)
    
    #print("--- Flicks to Download ---")
    #for i in sovietMovies:
    #    print(i)
    #print("--- Flicks to Skip ---")
    #for i in skippedFlicks:
    #    print(i)
    
    #CSV delimited by pipe "|" and nothing else.
    #Extra string delimiters will create an unruly CSV
    print("--- Generating CSV File ---")
    writeCsv()
    totalSize = 0.0
    print("--- Calculating Total Size ---")
    for i in sovietMovies:
        totalSize += i.fileSize
        totalSize += i.srtSize
    totalSize = totalSize / 1000000000
    inputString = "\nTotal Download Size: " + str(round(totalSize, 2)) + " gb" 
    inputString += "\nWould you like to download [y/n]? "
    downloadChoice = input(inputString)
    if downloadChoice != 'y':
        print("No Downloads Today")
        exit(1)
    print("--- Downloading Files ---")
    for i in sovietMovies:
        downloadFlicks(i)

if __name__ == "__main__":
    main()
