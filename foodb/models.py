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
    return create_engine(URL(**settings.FOOD_DATABASE))


Base = declarative_base()

class Foods(Base):
    __tablename__ = "foods"


    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_scientific = Column(String)
    description = Column(String)
    itis_id = Column(String)
    wikipedia_id = Column(String)
    picture_file_name = Column(String)
    picture_content_type = Column(String)
    picture_file_size = Column(Integer)
    picture_updated_at = Column(DateTime)
    legacy_id = Column(Integer)
    food_group = Column(String)
    food_subgroup = Column(String)
    food_type = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    creator_id = Column(Integer)
    updater_id = Column(Integer)
    export_to_afcdb = Column(SmallInteger)
    category = Column(String)
    ncbi_taxonomy_id = Column(Integer)
    export_to_foodb = Column(SmallInteger)

    # french_wikipedia_id = None
    # commons_wikipedia_id = None
    # french_translations = []

    def __init__(self, *args, **kwargs):
        self.french_translations = []
        self.french_wikipedia_id = None
        self.commons_wikipedia_id = None
        return super(Foods, self).__init__(*args, **kwargs)