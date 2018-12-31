import scrapy
import pprint
import urllib.request
import os
import os.path
import subprocess
from datetime import datetime, timedelta
import dateutil.parser
import smtplib
pp = pprint.PrettyPrinter(indent=4)
visited = set()

spec = {'Today':datetime.today(), '1 day ago':datetime.today() - timedelta(days = 1), '2 days ago':datetime.today() - timedelta(days = 2)}
class ImagesSpider(scrapy.Spider):
    name = "images"
    email = "jzhaojieh@gmail.com"

    def start_requests(self):
        urls = [
            'https://readms.net/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
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
                # break
            else:
                d[chapter_name + chapter] = dateutil.parser.parse(days[i], ignoretz=True)
        pp.pprint(res)
        for k, v in res.items():
            chapter_link = response.url + v[1:]
            self.sendEmail(self.email, k + " has been downloaded", "")
            yield scrapy.Request(chapter_link, callback=self.parse_chapters)
    
    def parse_chapters(self, response):
        cwd = os.getcwd() 
        while not (response.url.endswith("end")):
            # avoid checking same urls more than once
            visited.add(response.url)
            url = response.url.split('/')
            # Handle redirect to url not found
            if ("error" in url): return 
            img = response.xpath('//*[@id="manga-page"]/@src').extract()
            # current working dir
            newcwd = cwd+ '/dl/' + url[-4] + url[-3] + '/'
            # dir to save the new image file
            img_url = newcwd + url[-4] + url[-1] + ".jpg"
            # make new dir to store chapter images if not found
            if not os.path.exists(cwd + '/dl/' + url[-4] + url[-3] + '/'):
                s = "mkdir " + url[-4] + url[-3]
                subprocess.call("mkdir dl/" + url[-4] + url[-3], shell=True)
            # download the images to local folder
            urllib.request.urlretrieve("https:" + img[0], img_url)
            # check for end of chapter
            try:
                url[-1] = str(int(url[-1]) + 1)
            except:
                return
            url = "/".join(url)
            # Recurse until url no longer ends in a number
            try:
                return scrapy.Request(url, callback=self.parse_chapters)
            except:
                return
        return
    def sendEmail(self, recipient, subject, body):
        user = "mangascrape"
        pwd = "badpassword123"

        FROM = user
        TO = recipient if isinstance(recipient, list) else [recipient]
        SUBJECT = subject
        TEXT = body

        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(user, pwd)
            server.sendmail(FROM, TO, message)
            server.close()
            print('successfully sent the mail')
        except:
            print("failed to send mail")