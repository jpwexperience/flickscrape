# FlickScrape

## Python 3 Web Scraper to download and pull information from [sovietmoviesonline.com](https://sovietmoviesonline.com)

### Usage: $ python3 flickscrape.py
The script uses the sovietmoviesonline.com/all\_movies.html link to pull all the film links. Each link's page is then scraped for relevant content which is exported to a CSV file delimited by a pipe "|". User is then prompted whethey want to download the files. If selected, the flick and corresponding subtitle will be downloaded to a newly created directory named using the flick's title. 

### Required Dependencies
* BeautifulSoup  
* LXML

This is a rework of an older project ([sovietmoviesonline-scrape](https://github.com/jpwexperience/sovietmoviesonline-scrape)) that incorporates Beautiful Soup rather than taking an external xml sitemap.

There is also more attenion towards building the csv file to give information about each flick.

### General Idea
On the site, each flicks has a number id in the it's url slug. The majority of these films use this number as the full flick's name. One can then simply pull out the number and rebuild the url to download the flick and corresponding subtitles.

### Assumptions
* First Table Found Contains: Original Title, IMDB, Views, Year
* First \<div class="director">...\</div> contains films director
* There is \<div id="error404">...\</div> on 404 pages

### Bugs and Issues
* Some of the flicks are hosted through vimeo and aren't accessible without an account.
* Some flicks are broken into pieces and thus having a slightly different naming scheme.
	* ex. \<flick num>-1.mp4 and \<flick num>-2.mp4
* Some flick's html page results in a 404 yet the video is still hosted. They are available to download but are skipped since no information about the film can be scraped. 
