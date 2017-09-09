from sqlalchemy import create_engine, Column, Integer, String, DateTime, SmallInteger, Float, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

import math
import settings

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))


Base = declarative_base()



MealType = postgresql.ENUM('appetizers', 'main-course', 'dessert', 'breakfast', 'drinks', name='meal_type')
DifficultyType = postgresql.ENUM('very easy', 'easy', 'medium', 'difficult', name='difficulty_type')
CostType = postgresql.ENUM('cheap', 'average', 'expensive', name='cost_type')


class ScrapedRecipes(Base):
    __tablename__ = "scraped_recipes"

    id = Column(Integer, primary_key=True)
    url = Column('url', String)
    source = Column('source', String)
    source_id = Column('source_id', String)

    title = Column('title', String)

    number = Column('number', Integer)
    unity_number = Column('unity_number', String)

    raw_ingredients = Column('raw_ingredients', postgresql.ARRAY(String, dimensions=1))
    raw_recipe = Column('raw_recipe', postgresql.ARRAY(String, dimensions=1))
    raw_difficulty = Column('raw_difficulty', String)
    raw_cost = Column('raw_cost', String)

    tags = Column('tags', postgresql.ARRAY(String, dimensions=1))

    type = Column('type', MealType, nullable=True)
    difficulty = Column('difficulty', DifficultyType, nullable=True)
    cost = Column('cost', CostType, nullable=True)
    preparation_time = Column('preparation_time', SmallInteger)
    cook_time = Column('cook_time', SmallInteger)

    user_rating = Column('user_rating', Float)
    ratings_count = Column('ratings_count', Integer)

    photos = Column('photos', postgresql.ARRAY(String, dimensions=1))

    ingredients = Column('ingredients', JSON)

    def to_json(self):
        return {
            'objectID': self.id,
            'title': self.title[2:],
            'ingredients': [ingredient['name'] for ingredient in self.ingredients],
            'preparation_time': self.preparation_time,
            'cook_time': self.cook_time,
            'total_time': self.cook_time + self.preparation_time,
            'no_cook': self.cook_time == 0,
            'user_rating': self.user_rating,
            'ratings_count': self.ratings_count,
            'rating': self.user_rating * math.log(self.ratings_count+1) if self.user_rating is not None else 0.5,
            'photos': self.photos,
            'url': self.url,
            'source': self.source,
        }