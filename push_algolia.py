# -*- coding: utf-8 -*-

from algoliasearch import algoliasearch

from sqlalchemy.orm import sessionmaker
from crawler.models import ScrapedRecipes, db_connect


client = algoliasearch.Client("P0Y1SRPNG9", "f5db240398a9131e58d29687a96a88c1")
index = client.init_index('recipes')


engine = db_connect()
Session = sessionmaker(bind=engine)
session = Session()

q = session.query(ScrapedRecipes)

index.set_settings({
        "searchableAttributes": ["title", "ingredients"],
        "attributesForFaceting": ["ingredients", "no_cook", "total_time", "source"],
        "customRanking": ["desc(rating)"]
    }, True)


for r in q:
    res = index.save_object(r.to_json())
