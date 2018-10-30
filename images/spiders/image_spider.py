import scrapy
import pprint
import urllib.request
from datetime import datetime, timedelta
import dateutil.parser
pp = pprint.PrettyPrinter(indent=4)
visited = set()

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
        res = {}
        releases = response.xpath('/html/body/div[3]/div[3]/div[2]/div/ul/li/a/text()').extract()
        urls = response.xpath('/html/body/div[3]/div[3]/div[2]/div/ul/li/a/@href').extract()
        chapters = response.xpath('/html/body/div[3]/div[3]/div[2]/div/ul/li/a/strong').extract()
        days = response.xpath('/html/body/div[3]/div[3]/div[2]/div/ul/li/a/span/text()').extract()
        pp.pprint(urls)
        for i, r in enumerate(releases):
            if days[i] in spec.keys():
                chapter_name = r.rstrip().lstrip().lower()
                chapter = chapters[i].rstrip("</strong>").lstrip("<strong>")
                d[chapter_name + chapter] = spec[days[i]]
                # if days[i] == "Today":
                res[(chapter_name + chapter)] = urls[i]
                break
            else:
                d[chapter_name + chapter] = dateutil.parser.parse(days[i], ignoretz=True)
        # pp.pprint(d)
        for k, v in res.items():
            chapter_link = response.url + v[1:]
            print(chapter_link)
            yield scrapy.Request(chapter_link, callback=self.parse_chapters)
    
    def parse_chapters(self, response):
        while not (response.url.endswith("end")) :
            visited.add(response.url)
            url = response.url.split('/')
            img = response.xpath('//*[@id="manga-page"]/@src').extract()
            print("img = " + str(img))

            urllib.request.urlretrieve("https:" + img[0], url[-4] + url[-1] + ".jpg")

            try:
                url[-1] = str(int(url[-1]) + 1)
                
            except:
                return
            url = "/".join(url)
            print(url)
            print(visited)
            try:
                return scrapy.Request(url, callback=self.parse_chapters)
            except:
                return
        return