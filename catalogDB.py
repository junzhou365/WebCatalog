from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import urllib2
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging

Base = declarative_base()
RELATIVE_FOLDER_PATH = "static/images/"
#LOCAL_PATH = "http://localhost:5000/catalog/"


# return file path
def download_file(url):
    baseFile = os.path.basename(url)
    #baseFile = baseFile.encode('ascii')
    file_path = os.path.join(RELATIVE_FOLDER_PATH, baseFile)
    req = urllib2.urlopen(url)
    f = open(file_path, 'wb')
    #meta = u.info()
    #file_size = int(meta.getheaders("Content-Length")[0])

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = req.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
    f.close()
    return '/' + file_path

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def get_by_id(cls, category_id):
        return session.query(Category).filter_by(id = category_id).one()

    @classmethod
    def get_by_name(cls, name):
        return session.query(Category).filter_by(name = name).first()

    @classmethod
    def get_all(cls):
        return list(session.query(Category).all())

    @classmethod
    def store(cls, name):
        newCategory = Category(name = name)
        session.add(newCategory)
        session.commit()
        return newCategory

    @classmethod
    def delete_by_id(cls, category_id):
        itemsToDelete = Item.get_all_by_category(category_id)
        for itemToDelete in itemsToDelete:
            session.delete(itemToDelete)
        categoryToDelete = Category.get_by_id(category_id)
        session.delete(categoryToDelete)
        session.commit()

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'datetime'   : self.datetime,
           'name'         : self.name,
           'id'         : self.id,
       }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    desc = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    img_id = Column(Integer, nullable=True)
    datetime = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def get_by_id(cls, item_id):
        return session.query(Item).filter_by(id = item_id).one()

    @classmethod
    def get_by_title(cls, title):
        return session.query(Item).filter_by(title = title).first()

    @classmethod
    def get_all_by_category(cls, category_id):
        return list(session.query(Item).filter_by(category_id = category_id).all())

    @classmethod
    def store(cls, title, desc, category_id, img_id):
        newItem = Item(title = title, desc = desc, category_id = category_id, img_id = img_id)
        session.add(newItem)
        session.commit()

    def update(self, title, desc, category_id, img_id):
        self.title = title
        self.desc = desc
        self.category_id = category_id
        self.img_id = self.img_id
        self.datetime = datetime.datetime.now()
        session.commit()

    @classmethod
    def delete_by_id(cls, item_id):
        itemToDelete = Item.get_by_id(item_id)
        session.delete(itemToDelete)
        session.commit()

    @classmethod
    def get_latest_10_items(cls):
        result = session.query(Item).order_by(cls.datetime.desc()).all()
        return result

    def get_img(self):
        return session.query(Image).filter_by(id = self.img_id).one()

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'datetime'   : self.datetime,
           'image_url'  : Image.get_by_id(self.img_id).img_url,
           'category'   : Category.get_by_id(self.category_id).name,
           'description'    : self.desc,
           'title'         : self.title,
           'id'         : self.id,
       }

class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    img_title = Column(String(250))
    img_path = Column(String)
    img_url = Column(String)
    img_src = Column(String)
    datetime = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def store(cls, img_title, img_path, img_url):
        # always store local image
        if img_url:
            img_path = download_file(img_url)
        img_src = img_path
             
        newImg = Image(img_title = img_title, img_path = img_path, img_url = img_url, img_src = img_src)
        session.add(newImg)
        session.commit()
        return newImg

    @classmethod
    def get_by_id(cls, img_id):
        return session.query(Image).filter_by(id = img_id).one()

    def update(self, img_title, img_path, img_url):
        # always store local image
        if img_path and img_url:
            img_url = None
        self.img_title = img_title
        self.img_path = img_path
        self.img_url = img_url
        self.datetime = datetime.datetime.now()
        session.commit()
        

engine = create_engine('postgresql+psycopg2:///catalog')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
