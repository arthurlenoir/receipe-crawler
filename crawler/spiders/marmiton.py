from crawler.items import MarmitonPage

from scrapy import Spider, Selector
from scrapy.http import Request

from html2text import HTML2Text


def process_time(str_time):
    splitted_time = str_time.split('h')
    minutes = 0
    hours = 0
    if len(splitted_time) > 1:
        hour = int(splitted_time[0])
        if len(splitted_time[1]) > 0:
            minutes = int(splitted_time[1])
    else:
        splitted_time = str_time.split('min')
        if len(splitted_time) > 1:
            minutes = int(splitted_time[0])
    return hours*60 + minutes


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
                if not urlnode.startswith("http://www.marmiton.org/forum/") and not urlnode.startswith("http://www.marmiton.org/magazine/"):
                    yield Request(urlnode, callback=self.parse_recipe)

    def parse_recipe(self, response):
        title = response.css('h1.main-title').extract_first()

        if title is not None:
            item = MarmitonPage()
            item['url'] = response.url
            print response.url
            print "============================"

            converter = HTML2Text()


            converter.ignore_links = True
            item['title'] = converter.handle(title).strip()

            item['ingredients'] = []
            item['raw_ingredients'] = []
            item['raw_recipe'] = []

            item['tags'] = response.css('.mrtn-tags-list .mrtn-tag::text').extract()
            item['type'] = None
            item['raw_difficulty'] = ' '.join(response.css('.recipe-infos__level .recipe-infos__item-title::text').extract()).replace(u'\xa0', u' ').strip()
            item['raw_cost'] = ' '.join(response.css('.recipe-infos__budget .recipe-infos__item-title::text').extract()).replace(u'\xa0', u' ').strip()
            item['preparation_time'] = process_time(' '.join(response.css('.recipe-infos__timmings__preparation .recipe-infos__timmings__value::text').extract()).replace(u'\xa0', u' ').strip())
            item['cook_time'] = process_time(' '.join(response.css('.recipe-infos__timmings__cooking .recipe-infos__timmings__value::text').extract()).replace(u'\xa0', u' ').strip())

            item['user_rating'] = response.css('.recipe-reviews-list__review__head__infos__rating__value::text').extract_first(default='').replace(u'\xa0', u' ').strip()
            if item['user_rating'] != '':
                try:
                    item['user_rating'] = float(item['user_rating']) / 5.0
                except:
                    item['user_rating'] = None
            else:
                item['user_rating'] = None
            print "NB REVIEWS", response.css('.nb-reviews::text').extract_first()

            reviews = response.css('.nb-reviews::text').re_first(r'Avec (\d+) note', 0)
            print "REVIEWS", reviews
            item['ratings_count'] = int(reviews)

            item['photos'] = response.css('#af-diapo-desktop-0_img::attr(src)').extract()



            for ingredients in response.css('.recipe-ingredients-tab'):
                for quantitizer_container in ingredients.css('.recipe-ingredients__header'):
                    quantitizer_label = ' '.join(quantitizer_container.css('.recipe-ingredients__qt-title::text').extract()).replace(u'\xa0', u' ').strip()
                    count = quantitizer_container.css('.recipe-ingredients__qt-counter__value::attr(value)').extract_first()
                    if quantitizer_label is not None and count is not None:
                        try:
                            item['number'] = int(count)
                            item['unity_number'] = quantitizer_label
                        except:
                            pass

                for ingredient in ingredients.css('.recipe-ingredients__list__item'):
                    image = ingredient.css('.ingredients-list__item__icon::attr(src)').extract_first()
                    raw_ingredient = ' '.join(ingredient.css('::text').extract()).replace(u'\xa0', u' ').strip()
                    item['raw_ingredients'].append(raw_ingredient)
                    ing = item.parse_ingredient(raw_ingredient)
                    if ing is not None:
                        ing['uid'] = image
                    item['ingredients'].append(ing)


            for recipe_elem in response.css('.recipe-preparation__list__item'):
                elem = ' '.join(recipe_elem.css('::text').extract()).replace(u'\xa0', u' ').strip()
                item['raw_recipe'].append(elem)

            return item
