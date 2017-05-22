# Wine scraper
import scrapy
from bs4 import BeautifulSoup
import re

class QuotesSpider(scrapy.Spider):
    name = "wine"
    

    def start_requests(self):
        urls = [
            'http://www.owenroe.com/Our-Wine/White-Wines'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        grapes = self.loadVarietals()
        winery = response.url.split("/")[2]
        filename = '%s.html' % winery
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        soup = BeautifulSoup(response.text, 'lxml')
        for wine in grapes:
            results = soup.find_all(string=re.compile('%s' % wine, re.IGNORECASE))
            if (len(results) > 0):
                classDivName = self.getParentDivClassName(results[0])
                print classDivName
                self.getWineDivs(soup, classDivName)
                break
        if len(results)==0:
            print "No wines found"   

    # Find the class name of the div for a found wine
    def getParentDivClassName(self, result):
        classname = None
        parentDiv = result.find_parent("div")
        attributeDict = parentDiv.attrs
        # Grab the first value in the dictionary for the class key
        if(attributeDict["class"] != None):
            classNames = attributeDict["class"]
            classname = classNames[0]
        return classname;

    # Get all the divs with the class name
    def getWineDivs(self, soup, classname):
        wines = soup.find_all(attrs={"class":'%s' % classname})
        for wine in wines:
            print wine
    # Load the file of grape varietals, returning a list
    def loadVarietals(self):
        wineFile = "wine_scrapy/spiders/grape_varietals"
        file = open(wineFile, "r'")
        lines = file.readlines()
        file.close();
        grapes =[]
        for wine in lines:
            grapes.append(wine.split("\n")[0])

        return grapes;