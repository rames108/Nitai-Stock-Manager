from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Numeric
from sqlalchemy.types import LargeBinary

#https://inloop.github.io/sqlite-viewer/ database viewer

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    firstreg = db.Column(db.DateTime(timezone=True), default=func.now())
    outpay = db.Column(Numeric(4,2))
    logs = db.Column(db.String)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(200))
    #items = db.relationship('Item', backref='supplier')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    txtItemName = db.Column(db.String(100), nullable=False)
    txtItemPrice = db.Column(db.Float, nullable=False)
    txtItemDesc = db.Column(db.Text, nullable=True)
    intItemStock = db.Column(db.Integer, nullable=False)
    intItemMin = db.Column(db.Integer, nullable=False)
    
    # Store the image as binary data
    image = db.Column(LargeBinary, nullable=True)
    # Optional: store the original filename and mimetype for reference
    image_filename = db.Column(db.String(255), nullable=True)
    image_mimetype = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, txtItemName={self.txtItemName!r}, txtItemPrice={self.txtItemPrice!r}, txtItemDesc={self.txtItemDesc!r}, intItemStock={self.intItemStock!r}, intItemMin={self.intItemMin!r})#, image={self.image!r})"
        #return f"Item('{self.txtItemName}', '{self.txtItemPrice}', '{self.txtItemDesc}', '{self.txtItemStock}', '{self.txtItemMin}')
    
    #supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    #ItemCategory

    #ItemPic
    #ItemBC
    #supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    #txtLogs = db.Column(db.String)