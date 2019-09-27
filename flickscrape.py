import os, sys, re, csv, requests, lxml, urllib3
from bs4 import BeautifulSoup

sovietMovies = []
base = "https://sovietmoviesonline.com/"
link = base + "all_movies.html"

class filmObj():
    badFile = 0
    badSrt = 0
    fileSize = 0
    srtSize = 0

    def __init__(self, num, flickUrl, downloadUrl, name, year, imdb, srtUrl):
        self.num = num
        self.flickUrl = flickUrl
        self.downloadUrl = downloadUrl
        self.name = name
        this.year = year
        this.imdb = imdb
        this.srtUrl = srtUrl

def processFilm(flickStuff):
    global link
    filmUrl = base + flickStuff 
    filmReq = requests.get(filmUrl)
    filmSource = filmReq.text
    filmSoup = BeautifulSoup(filmSource, "lxml")
    print(filmSoup.h1.contents[0])

def main():
    print("--- Extracting Film Links ---")
    global link
    sovietRequest = requests.get(link)
    data = sovietRequest.text
    soup = BeautifulSoup(data, "lxml")
    nums = []
    links = []
    for link in soup.find_all('a'):
        tempUrl = link.get('href')
        #make sure it's a proper film link and not blog
        movieRegex = re.escape(base) + r"(?!blog).*\.html"
        match = re.match(movieRegex, tempUrl)
        if match:
            print(tempUrl)
            tempSplit = tempUrl.split('/')
            movieBase = tempSplit[len(tempSplit) - 1] + tempSplit[len(tempSplit) - 1] 
            baseSplit = movieBase.split('-')
            num = baseSplit[0]
            found = 0
            for i in nums:
                if (i == num):
                    found = 1
                    break
            if found == 0:
                nums.append(num)
                links.append(movieBase)
    print("--- Processing Films ---")
    #for movie in links:
    processFilm(links[0])

if __name__ == "__main__":
    main()
