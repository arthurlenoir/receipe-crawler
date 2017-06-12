# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import logging
import re
import scrapy

number_people_pattern = re.compile("pour (\d+) ([^)]+)", flags=re.IGNORECASE)
ingredient_q1q2_pattern = re.compile(u'^(?P<q1>\d+([,.]\d+)?)[-àa ]+(?P<q2>\d+([,.]\d+)?) ?(?P<unity>[^(]+?)? ?(?P<sep>(de)|(d\'))(?P<name>.+)$', flags=re.IGNORECASE)
ingredient_quantity_pattern = re.compile("^(?P<quantity>\d+([,.]\d+)?) ?(?P<unity>[^(]+?)? ?(?P<sep>(de)|(d'))(?P<name>.+)$", flags=re.IGNORECASE)
quotient_ingredient_quantity_pattern = re.compile("^(?P<q1>\d+) ?/ ?(?P<q2>\d+) ?(?P<name>.+)$", flags=re.IGNORECASE)
simple_ingredient_quantity_pattern = re.compile("^(?P<quantity>\d+([,.]\d+)?) ?(?P<name>.+)$", flags=re.IGNORECASE)

unity_black_list = ('pomme', )

class MarmitonPage(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    ingredients = scrapy.Field()

    number = scrapy.Field()
    unity_number = scrapy.Field()


    def parse_ingredients(self, ingredients):
        people, ingredients = ingredients.split(':', 1)
        people_match = number_people_pattern.search(people)
        if people_match is not None:
            self['number'] = int(people_match.group(1))
            self['unity_number'] = people_match.group(2)
        else:
            logging.warning("Number not found: \"%s\"" % people)

        for ingredient in ingredients.split('\\-'):
            ingredient = self.parse_ingredient(' '.join(ingredient.strip().split('\n')))
            print ingredient

    def parse_ingredient(self, ingredient):
        if ingredient == "":
            return None

        ingredient_match = ingredient_q1q2_pattern.search(ingredient)
        if ingredient_match is not None:
            res = {
                'q1': float(ingredient_match.group('q1').replace(',', '.')),
                'q2': float(ingredient_match.group('q2').replace(',', '.')),
                'unity': ingredient_match.group('unity'),
                'separator': ingredient_match.group('sep').strip(),
                'name': ingredient_match.group('name').strip(),
            }
            if self.check_unity(res):
                return res

        ingredient_match = ingredient_quantity_pattern.search(ingredient)
        if ingredient_match is not None:
            res = {
                'q1': float(ingredient_match.group('quantity').replace(',', '.')),
                'unity': ingredient_match.group('unity'),
                'separator': ingredient_match.group('sep').strip(),
                'name': ingredient_match.group('name').strip(),
            }
            if self.check_unity(res):
                return res

        ingredient_match = simple_ingredient_quantity_pattern.search(ingredient)
        if ingredient_match is not None:
            return {
                'q1': float(ingredient_match.group('quantity').replace(',', '.')),
                'name': ingredient_match.group('name').strip(),
            }

        ingredient_match = quotient_ingredient_quantity_pattern.search(ingredient)
        if ingredient_match is not None:
            return {
                'q1': float(ingredient_match.group('q1'))/float(ingredient_match.group('q2')),
                'name': ingredient_match.group('name').strip(),
            }

        return {'name': ingredient}

    def check_unity(self, ingredient):
        if ingredient['unity'] is not None:
            for item in unity_black_list:
                if item in ingredient['unity']:
                    return False
        return True



