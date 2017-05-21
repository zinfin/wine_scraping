# Wine scraper
import scrapy
from bs4 import BeautifulSoup
import re

class QuotesSpider(scrapy.Spider):
    name = "wine"
    

    def start_requests(self):
        urls = [
            'https://www.cakewines.com/collections/all'
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
                print results
                break
        if len(results)==0:
            print "No wines found"   

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