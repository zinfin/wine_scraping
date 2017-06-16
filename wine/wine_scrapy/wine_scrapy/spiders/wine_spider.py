# Wine scraper
import scrapy
from bs4 import BeautifulSoup
import re
import json


class QuotesSpider(scrapy.Spider):
    name = "wine"

    def start_requests(self):
        urls = self.load_urls()

        for url in urls[:50]:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        wines = None
        grapes = self.loadVarietals()
        winery = response.url.split("/")[2]

        if winery[:3] != 'www':
            wine_split = winery.split(".")
            if len(wine_split) > 0:
                winery = wine_split[0]

        filename = '%s.html' % winery
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        soup = BeautifulSoup(response.text, 'lxml')
        for wine in grapes:
            results = soup.find_all(string=re.compile
                                    (r'\b20[0-9]{2}\b[\w\s\.\W]+%s' % wine, re.IGNORECASE))
            if len(results) > 0:
                for res in results:
                   # print winery, res
                    yield{
                        'winery' : winery,
                        'wine': res,
                        'grape': wine,
                    }

            else:
                yield{
                    'winery':winery,
                    'wine' : 'None found',
                    'grape': wine,
                }



    def find_highest_count_string(self, dict):
        highestCountStr = None
        count = 0
        for key, values in dict.items():
            itemCount = len(values)
            if itemCount > count:
                count = itemCount
                highestCountStr = key
        return  highestCountStr

    def find_parent_classname(self, element):
        # We're looking for a parent having a class attribute
        className = None
        for parent in element.parents:

            attrDict = parent.attrs
            if "class" in attrDict:
                className= attrDict["class"][0]
                if len(className) > 1:
                    break

        return className

    # Group the attribute keys we run across
    def group_attr(self, results):
        dict = {}
        for element in results:
            for parent in element.parents:
                attrDict = parent.attrs
                for key, value in attrDict.items():
                    if key in dict:
                        valueList = dict[key]
                        if type(value) is list:
                            for val in value:
                                valueList.append(val)
                        else:
                            valueList.append(value)
                    else:
                        if type(value) is list:
                            valueList = []
                            for val in value:
                                valueList.append(val)
                            dict[key] = valueList
                        else:
                            dict[key] = [value]
        return dict

    # Find the class name of the div for a found wine
    def getParentDivClassName(self, result):
        classname = None
        parentDiv = result.find_parent("div")
        attributeDict = parentDiv.attrs
        # Grab the first value in the dictionary for the class key
        if(attributeDict["class"] is not None):
            classNames = attributeDict["class"]
            classname = classNames[0]
        return classname

    # Get all the divs with the class name
    def get_wine_with_classname(self, soup, classname):
        self.log("divs with class name %s" % classname)
        wines = soup.find_all(attrs={"class": '%s' % classname})
        if len(wines) > 0:
            self.log("******* Found %d wines ********" % len(wines))
            for wine in wines:
                print wine.string

        else:
            print " NO WINES FOUND"
        return wines

    # Load the file of grape varietals, returning a list
    def loadVarietals(self):
        wineFile = "wine_scrapy/spiders/grape_varietals"
        file = open(wineFile, "r'")
        lines = file.readlines()
        file.close()
        grapes = []
        for wine in lines:
            grapes.append(wine.split("\n")[0])

        return grapes

    def load_urls(self):
        #Load json bookmarks
        urls = []
        fh = open('wine_scrapy/spiders/jsonbookmarks')
        jsondata = fh.read();
        fh.close();
        jsondict = json.loads(jsondata)
        rootdict = jsondict['roots']
        bookmarkdict = rootdict['bookmark_bar']
        childlist = bookmarkdict['children']
        for child in childlist:
            name = child['name']
            if name == 'Wineries':
                grandchildren = child['children']
                for grandchild in grandchildren:
                    if grandchild['url'] is not None:
                        urls.append(grandchild['url'])
        return urls