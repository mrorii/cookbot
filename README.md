# cookbot

Minimal crawlers for various recipe websites. It can be used for crawling:

* [cookpad](http://cookpad.com/)
* [allrecipes.com](http://allrecipes.com/)

TODO:

* [epicurious](http://www.epicurious.com/)
* [food network](http://www.foodnetwork.com/)

## Usage

    scrapy crawl cookpad --output=cookpad.json
    scrapy crawl allrecipes --output=allrecipes.json

If you want to pause and resume crawls, run it like this:

    scrapy crawl cookpad -s JOBDIR=cpad-crawl --output=cookpad.json

You can stop the spider safely any time (by pressing Ctrl-C), and resume it later by issuing the same command.
