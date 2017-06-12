from crawler.items import MarmitonPage

from scrapy import Spider, Selector
from scrapy.http import Request

from html2text import HTML2Text


class MarmitonSpider(Spider):
    name = "marmiton.org"
    allowed_domains = ['marmiton.org']
    start_urls = ['http://www.marmiton.org/wsitemap_index.xml']
    iterator = 'html'
    itertag = 'sitemap'
    namespaces = (
        ('sm', 'http://www.sitemaps.org/schemas/sitemap/0.9'),
    )

    def parse(self, response):
        xxs = Selector(response)
        for namespace, schema in self.namespaces:
            xxs.register_namespace(namespace, schema)
        for urlnode in xxs.xpath('//sm:loc/text()').extract():
            if urlnode.endswith(".xml"):
                yield Request(urlnode)
            else:
                if not urlnode.startswith("http://www.marmiton.org/forum/"):
                    yield Request(urlnode, callback=self.parse_receipe)

    def parse_receipe(self, response):
        title = response.css('h1.m_title').extract_first()

        if title is not None:
            item = MarmitonPage()

            converter = HTML2Text()
            converter.ignore_links = True
            item['title'] = converter.handle(title).strip()

            ingredients = response.css('.m_content_recette_ingredients').extract_first()
            if ingredients is not None:
                ingredients = converter.handle(ingredients).strip()
                item.parse_ingredients(ingredients)

            return item
