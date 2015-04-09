from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @classmethod
    def filter_by_id(cls, category_id):
        return session.query(Category).filter_by(id = category_id).one()

    @classmethod
    def filter_by_name(cls, name):
        return session.query(Category).filter_by(name = name).first()

    @classmethod
    def get_all(cls):
        return list(session.query(Category).all())

    @classmethod
    def store(cls, name):
        newCategory = Category(name = name)
        session.add(newCategory)
        session.commit()

    @classmethod
    def delete_by_id(cls, category_id):
        itemsToDelete = Item.get_all_by_category(category_id)
        for itemToDelete in itemsToDelete:
            session.delete(itemToDelete)
        categoryToDelete = Category.filter_by_id(category_id)
        session.delete(categoryToDelete)
        session.commit()

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    desc = Column(Text)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    img_id = Column(Integer, nullable=True)

    @classmethod
    def filter_by_id(cls, item_id):
        return session.query(Item).filter_by(id = item_id).one()

    @classmethod
    def filter_by_title(cls, title):
        return session.query(Item).filter_by(title = title).first()

    @classmethod
    def get_all_by_category(cls, category_id):
        return list(session.query(Item).filter_by(category_id = category_id).all())

    @classmethod
    def store(cls, title, desc, category_id, img_id):
        newItem = Item(title = title, desc = desc, category_id = category_id, img_id = img_id)
        session.add(newItem)
        session.commit()

    @classmethod
    def delete_by_id(cls, item_id):
        itemToDelete = Item.filter_by_id(item_id)
        session.delete(itemToDelete)
        session.commit()

    def get_img(self):
        return session.query(Image).filter_by(id = self.img_id).one()

class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    img_title = Column(String(250))
    img_path = Column(String)
    img_url = Column(String)

    @classmethod
    def store(cls, img_title, img_path, img_url):
        # always store local image
        if img_path and img_url:
            img_url = None
        newImg = Image(img_title = img_title, img_path = img_path, img_url = img_url)
        session.add(newImg)
        session.commit()
        return newImg

    @classmethod
    def filter_by_id(cls, img_id):
        return session.query(Image).filter_by(id = img_id).one()
        

engine = create_engine('postgresql+psycopg2:///catalog')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
