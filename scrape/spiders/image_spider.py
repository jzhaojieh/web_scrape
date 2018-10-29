import scrapy
import pprint
from datetime import datetime, timedelta
import dateutil.parser
pp = pprint.PrettyPrinter(indent=4)
spec = {'Today':datetime.today(), '1 day ago':datetime.today() - timedelta(days = 1), '2 days ago':datetime.today() - timedelta(days = 2)}
class ImagesSpider(scrapy.Spider):
    name = "images"

    def start_requests(self):
        urls = [
            'https://readms.net/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # pp.pprint(page)
        # pp.pprint(response.body)
        d = {}
        res = []
        releases = response.xpath('/html/body/div[3]/div[3]/div[2]/div/ul/li/a/text()').extract()
        chapters = response.xpath('/html/body/div[3]/div[2]/div[2]/div/ul/li/a/strong').extract()
        days = response.xpath('/html/body/div[3]/div[3]/div[2]/div/ul/li/a/span/text()').extract()
        print(len(releases), len(chapters))
        for i, r in enumerate(releases):
            if days[i] in spec.keys():
                d[r.rstrip().lstrip().lower() + chapters[i]] = spec[days[i]]
                # if days[i] == "Today":
                res.append(r.rstrip().lstrip().lower() + chapters[i])
            else:
                d[r.rstrip().lstrip().lower() + chapters[i]] = dateutil.parser.parse(days[i], ignoretz=True)
        # pp.pprint(d)
        print(res)