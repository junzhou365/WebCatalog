import datetime
import urllib2
import os
import logging

from factory import db

IMAGES_PATH = "static/images/"
PARENT_FOLDER_PATH = "junzhou365/catalog/"

def download_file(url):
    """Download file from url to "static/images"

    Download file. Filename is automatically given by the url last part.
    Args:
        url: string
    Returns:
        file path: string, relative path like "static/images/120938120.jpg"
    """
    baseFile = os.path.basename(url) # base file name
    file_path = os.path.join(IMAGES_PATH, baseFile)
    req = urllib2.urlopen(url)
    dirname = os.path.dirname(PARENT_FOLDER_PATH + IMAGES_PATH)

    if not os.path.exists(dirname):
        os.makedirs(dirname)
    f = open(os.path.join(PARENT_FOLDER_PATH, file_path), 'wb') # 'wb': write binary

    file_size_dl = 0 # downloaded file size
    block_sz = 8192
    while True:
        buffer = req.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
    f.close()
    return '/' + file_path

class Category(db.Model):
    """Category table
        
    Columns: Id, Name, datetime(automatically updated after edited)

    Methods which interact Category table are classmethods.
    Methods which interact row are instance methods.
    """
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def get_by_id(cls, category_id):
        return db.session.query(Category).filter_by(id = category_id).one()

    @classmethod
    def get_by_name(cls, name):
        return db.session.query(Category).filter_by(name = name).first()

    @classmethod
    def get_all(cls):
        return list(db.session.query(Category).all())

    @classmethod
    def store(cls, name):
        newCategory = Category(name = name)
        db.session.add(newCategory)
        db.session.commit()
        return newCategory

    def update(self, name):
        """update name"""
        self.name = name
        self.datetime = datetime.datetime.now()
        db.session.commit()

    @classmethod
    def delete_by_id(cls, category_id):
        """Remove all items in this category"""
        itemsToDelete = Item.get_all_by_category(category_id)
        for itemToDelete in itemsToDelete:
            db.session.delete(itemToDelete)
        categoryToDelete = Category.get_by_id(category_id)
        db.session.delete(categoryToDelete)
        db.session.commit()

    def get_all_items(self):
        """get all items in this category"""
        return Item.get_all_by_category(self.id)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'datetime'   : self.datetime,
           'name'         : self.name,
           'id'         : self.id,
       }

class Item(db.Model):
    """Item table
        
    Columns: 
        id: Int
        title: String 
        desc: Text
        category_id: Foreign Key
        img_id: Int
        datetime(automatically updated after edited)

    Methods which interact Category table are classmethods.
    Methods which interact row are instance methods.
    """
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    desc = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(Category)
    img_id = db.Column(db.Integer, nullable=True)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def get_by_id(cls, item_id):
        return db.session.query(Item).filter_by(id = item_id).one()

    @classmethod
    def get_by_title(cls, title):
        return db.session.query(Item).filter_by(title = title).first()

    @classmethod
    def get_all_by_category(cls, category_id):
        return list(db.session.query(Item).filter_by(category_id = category_id).all())

    @classmethod
    def store(cls, title, desc, category_id, img_id):
        newItem = Item(title = title, desc = desc, category_id = category_id, img_id = img_id)
        db.session.add(newItem)
        db.session.commit()
        return newItem

    def update(self, title = None, desc = None, category_id = None, img_id = None):
        """Update row data"""
        if title:
            self.title = title
        if desc:
            self.desc = desc
        if category_id:
            self.category_id = category_id
        if img_id:
            self.img_id = self.img_id
        if title or desc or category_id or img_id:
            self.datetime = datetime.datetime.now()
            db.session.commit()

    @classmethod
    def delete_by_id(cls, item_id):
        itemToDelete = Item.get_by_id(item_id)
        db.session.delete(itemToDelete)
        db.session.commit()

    @classmethod
    def get_latest_10_items(cls):
        result = db.session.query(Item).order_by(cls.datetime.desc()).all()
        return result

    def get_img(self):
        """get image object"""
        return db.session.query(Image).filter_by(id = self.img_id).one()

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

class Image(db.Model):
    """Image table
        
    Columns: 
        id: Int
        title: String 
        path: String
        url: String
        src: String (Used for html src)
        datetime(automatically updated after edited)

    Methods which interact Category table are classmethods.
    Methods which interact row are instance methods.
    """
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    img_title = db.Column(db.String(250))
    img_path = db.Column(db.String)
    img_url = db.Column(db.String)
    img_src = db.Column(db.String)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def store(cls, img_title, img_path, img_url, url_prefix=""):
        """Download image if possible and store its local path"""
        if img_url:
            img_path = download_file(img_url)
        img_src = url_prefix + img_path
             
        newImg = Image(img_title = img_title, img_path = img_path, img_url = img_url, img_src = img_src)
        db.session.add(newImg)
        db.session.commit()
        return newImg

    @classmethod
    def get_by_id(cls, img_id):
        return db.session.query(Image).filter_by(id = img_id).one()

    def update(self, img_title, img_path, img_url):
        if img_path and img_url:
            img_url = None
        self.img_title = img_title
        self.img_path = img_path
        self.img_url = img_url
        self.datetime = datetime.datetime.now()
        db.session.commit()
