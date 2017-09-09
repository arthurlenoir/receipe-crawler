# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from sqlalchemy.orm import sessionmaker
from models import ScrapedRecipes, db_connect


class ReceipecrawlerPipeline(object):
    def __init__(self):
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()

        recipe = ScrapedRecipes(**item)
        recipe.source = item.source
        recipe.source_id = item.source_id
        print "-------------------------------"
        print recipe.url
        print "###############################"

        try:
            session.add(recipe)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item



