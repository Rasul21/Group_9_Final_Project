# Data Visualisation Assignment
# Group Members: Advait Jayant, Rasul Rasulov, Lexin Xu, Joseph Perrin, Ozlem Cuhaci

import pandas as pd
import numpy as np
import datetime
from datetime import date
import re
import math
import scrapy
import json
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from timeit import default_timer as timer

# Here is our JSON writer pipeline

class JsonWriterPipeline(object):

    # When the spider is open, it writes itself to the gamesresult to a julia file
    def open_spider(self, spider):
        self.file = open('gamesresult.jl', 'w')

    # When the spider closes, it closes that file as it is done writing to it
    def close_spider(self, spider):
        self.file.close()

    # This function dictates how the spider writes to the .jl file
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

# Creating a string for today's date to append to the end of the names of the files we create
today_date_string = str(date.today().month) + "_" + str(date.today().day) + "_" + str(date.today().year)

page = 2 # Jumping to Page Number 2
genre = 0 # Starting at the first genre

# Specifying the genre names 
genre_list = ["Action",
             "Adventure",
             "Action-Adventure",
             "Board+Game",
             "Education",
             "Fighting",
             "Misc",
             "MMO",
             "Music",
             "Party",
             "Platform",
             "Puzzle",
             "Racing",
             "Role-Playing",
             "Sandbox",
             "Shooter",
             "Simulation",
             "Sports",
             "Strategy",
             "Visual+Novel"]

class VGSpider(scrapy.Spider):
    global genre

    name = "game_spider"
    start_urls = ['https://www.vgchartz.com/games/games.php?name=&keyword=&console=&region=All&developer=&publisher=&goty_year=&genre=' + genre_list[0] + '&boxart=Both&banner=Both&ownership=Both&showmultiplat=No&results=200&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0&showpublisher=1&showvgchartzscore=0&showvgchartzscore=1&shownasales=0&shownasales=1&showdeveloper=0&showdeveloper=1&showcriticscore=0&showcriticscore=1&showpalsales=0&showpalsales=1&showreleasedate=0&showreleasedate=1&showuserscore=0&showuserscore=1&showjapansales=0&showjapansales=1&showlastupdate=0&showlastupdate=1&showothersales=0&showothersales=1&showshipped=0&showshipped=1']

    custom_settings = {
        'LOG_LEVEL': logging.WARNING,
        'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, 
        'FEED_FORMAT':'json',                                
        'FEED_URI': "gamesresult-" + today_date_string + ".json"
    }

    def parse(self, response):

        global genre
        global page

        # Selecting the elements we need
        IMAGE_SELECTOR = './/td[2]/div/a/div/img/@src'
        TITLE_SELECTOR = './/td[3]/a/text()'
        CONSOLE_SELECTOR = './/td[4]/img/@alt'
        PUBLISHER_SELECTOR = './/td[5]/text()'
        DEVELOPER_SELECTOR = './/td[6]/text()'
        VGSCORE_SELECTOR = './/td[7]/text()'
        CRITIC_SELECTOR = './/td[8]/text()'
        USER_SELECTOR = './/td[9]/text()'
        TOTALSHIPPED_SELECTOR = './/td[10]/text()'
        TOTALSALES_SELECTOR = './/td[11]/text()'
        NASALES_SELECTOR = './/td[12]/text()'
        PALSALES_SELECTOR = './/td[13]/text()'
        JPSALES_SELECTOR = './/td[14]/text()'
        OTHER_SELECTOR = './/td[15]/text()'
        RELEASEDATE_SELECTOR = './/td[16]/text()'
        UPDATE_SELECTOR = './/td[17]/text()'

        for row in response.xpath('//*[@id="generalBody"]/table[1]/tr'):
            yield {

                'img' : row.xpath(IMAGE_SELECTOR).extract(),
                'title' : row.xpath(TITLE_SELECTOR).extract(),
                'console' : row.xpath(CONSOLE_SELECTOR).extract(),
                'publisher' : row.xpath(PUBLISHER_SELECTOR).extract(),
                'developer' : row.xpath(DEVELOPER_SELECTOR).extract(),
                'vg_score' : row.xpath(VGSCORE_SELECTOR).extract(),
                'critic_score' : row.xpath(CRITIC_SELECTOR).extract(),
                'user_score' : row.xpath(USER_SELECTOR).extract(),
                'total_shipped' : row.xpath(TOTALSHIPPED_SELECTOR).extract(),
                'total_sales' : row.xpath(TOTALSALES_SELECTOR).extract(),
                'na_sales' : row.xpath(NASALES_SELECTOR).extract(),
                'pal_sales' : row.xpath(PALSALES_SELECTOR).extract(),
                'jp_sales' : row.xpath(JPSALES_SELECTOR).extract(),
                'other_sales' : row.xpath(OTHER_SELECTOR).extract(),
                'release_date' : row.xpath(RELEASEDATE_SELECTOR).extract(),
                'last_update' : row.xpath(UPDATE_SELECTOR).extract(),
                'genre' : genre_list[genre]
            }

        # Generating the URL for the next page
        next_page = "https://www.vgchartz.com/games/games.php?page=" + str(page) + "&results=200&name=&console=&keyword=&publisher=&genre="+ genre_list[genre] + "&order=Sales&ownership=Both&boxart=Both&banner=Both&showdeleted=&region=All&goty_year=&developer=&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1&showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1&alphasort=&showmultiplat=No"

        RESULTS_SELECTOR = '//*[@id="generalBody"]/table[1]/tr[1]/th[1]/text()'

        # Extracting the results using regex
        results = response.xpath(RESULTS_SELECTOR).extract_first()
        results_pat = r'([0-9]{1,9})'
        results = results.replace(",", "")

        # Assuming that each page has 200 search results
        last_page = math.ceil(int(re.search(results_pat, results).group(1)) / 200)

        # Checking whether we reached the last page
        if (page > last_page) & (genre_list[genre] == "Visual+Novel"):
            print(genre_list[genre])
            yield "All done!"
            return

        # Checking whether we reached the last genre
        elif (page > last_page) & (genre_list[genre] != "Visual+Novel"):
            print(genre_list[genre])
            page = 1
            genre += 1
            next_page = "https://www.vgchartz.com/games/games.php?page=" + str(page) + "&results=200&name=&console=&keyword=&publisher=&genre="+ genre_list[genre] + "&order=Sales&ownership=Both&boxart=Both&banner=Both&showdeleted=&region=All&goty_year=&developer=&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1&showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1&alphasort=&showmultiplat=No"
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
                )
            page += 1

        # Checking if we haven't reached the last page
        elif next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
                )
            page += 1

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    start = timer()
    process.crawl(VGSpider)
    process.start(stop_after_crawl=True) # Blocks here until the crawl is finished
    end = timer()
    print("It took " + str(end - start) + " seconds to retrieve this data.")

    # Reading the json file
    games = pd.read_json("gamesresult-" + today_date_string + ".json")

    # Cleaning up the dataframe
    games = games[~(games["title"].str.len() == 0)]

    # Converting single-element lists into a compiled list
    for column in ['console', 'critic_score', 'developer', 'img', 'jp_sales',
           'last_update', 'na_sales', 'other_sales', 'pal_sales', 'publisher',
           'release_date', 'title', 'total_sales', 'total_shipped', 'user_score',
           'vg_score']:
        games[column] = games[column].apply(lambda x : x[0])

    # Removing the trailing spaces in the columns
    games = games.apply(lambda x : x.str.strip())

    # Converting all NA strings into numpy NaN values
    games = games.replace("N/A", np.nan)

    # Cleaning the individual columns
    def clean_nums(column, dataframe):
        dataframe[column] = dataframe[column].str.strip("m") # This will strip the "m" off the end of each string 
        dataframe[column] = dataframe[column].apply(lambda x : float(x)) # This will turn all the values from strings to floats

    # Applying clean_nums to each column
    sales_columns = ["na_sales",
                     "jp_sales",
                     "pal_sales",
                     "other_sales",
                     "total_sales",
                     "total_shipped",
                     "vg_score",
                     "user_score",
                     "critic_score"]

    for column in sales_columns:
        clean_nums(column, games)

    # Cleaning up the dates 
    day_pat = r"([0-9]{2})(?=[a-z]{2})" 
    month_pat = r"([A-Z][a-z]{2})" 
    year_pat = r"([0-9]{2}(?![a-z]{2}))" 

    # Changing Month String to Month Integer
    month_to_num = {'Sep' : 9,
                    'Jul' : 7,
                    'Oct' : 10,
                    'Mar' : 3,
                    'Dec' : 12,
                    'Feb' : 2,
                    'Nov' : 11,
                    'Jun' : 6,
                    'Aug' : 8,
                    'May' : 5,
                    'Apr' : 4,
                    'Jan' : 1
                    }

    def clean_dates(text):
        global day_pat
        global month_pat
        global year_pat
        global month_to_num
        if text is np.nan:
            return text

        day = int((re.search(day_pat, text).group(1))) 
        month = month_to_num[(re.search(month_pat, text).group(1))] 
        year = (re.search(year_pat, text).group(1)) 

        if int(year[0]) >= 7:
            year = int("19" + year)
        else:
            year = int("20" + year)

        return(datetime.datetime(year, month, day))

    # We will apply the date cleanup function across our two date columns.

    for column in ["last_update", "release_date"]:
        games[column] = games[column].apply(lambda x : clean_dates(x))

    # A quick replacement of the +'s used in the url for genre to make our genre column more readable
    games["genre"] = games["genre"].str.replace("+", " ")

    # 1/1/1970 is used as a placeholder so we replace this by NaN values
    games.loc[games["release_date"].dt.year == 1970, "release_date"] = np.nan

    # Reordering the columns
    games = games[["img", "title", "console", "genre", "publisher", "developer", "vg_score", "critic_score", "user_score", "total_shipped", "total_sales", "na_sales", "jp_sales", "pal_sales", "other_sales", "release_date", "last_update"]]

    # Converting dataframe to CSV 
    games.to_csv("vgchartz-" + today_date_string +".csv", index=False)

    print(str(games["title"].count()) + " game records retrieved." )
    print("File saved as vgchartz-" + today_date_string + ".csv")
