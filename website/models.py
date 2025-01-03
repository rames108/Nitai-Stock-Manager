from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Numeric
from sqlalchemy.types import LargeBinary

#https://inloop.github.io/sqlite-viewer/ database viewer

class User(db.Model, UserMixin):  # Define the User model, inheriting from db.Model and UserMixin
    id = db.Column(db.Integer, primary_key=True)  # Primary key to uniquely identify each user
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's email; max length 150, must be unique and not null
    password = db.Column(db.String(150), nullable=False)  # User's password; max length 150, must not be empty
    name = db.Column(db.String(150), nullable=False)  # User's name; max length 150, must not be empty
    is_admin = db.Column(db.String(5))  # String to indicate if the user is an admin (e.g., "True" or "False")

    def __repr__(self):
        return f'<User  {self.email}>'  # String representation of the User object, showing the email

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150)) # Customer's email maximum length of 150 characters, can't be empty, must be unique
    email = db.Column(db.String(150), unique=True, nullable=False) # Customer's email maximum length of 150 characters, can't be empty, must be unique
    firstreg = db.Column(db.DateTime(timezone=True), default=func.now()) # Time of customer's first registration
    outpay = db.Column(Numeric(4,2)) # Customer's outstanding payments, must follow the following format xxxx.xx
    logs = db.Column(db.String) # Customer's buying logs

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150)) # Supplier's email maximum length of 150 characters, can't be empty, must be unique
    email = db.Column(db.String(150), unique=True, nullable=False) # Supplier's email maximum length of 150 characters, can't be empty, must be unique
    description = db.Column(db.String(200)) # Can be used to provide information about the supplier
    location = db.Column(db.String(200)) # Supplier's location
    #items = db.relationship('Item', backref='supplier') # To show what items the supplier supplies to the temple

class Item(db.Model):
    # Define the primary key for the Item model
    id = db.Column(db.Integer, primary_key=True)
    # The name of the item, cannot be null and has a maximum length of 100 characters
    txtItemName = db.Column(db.String(100), nullable=False)
    # The price of the item, cannot be null and is stored as a float
    txtItemPrice = db.Column(db.Float, nullable=False)
    # A description of the item, which is optional and can be of variable length
    txtItemDesc = db.Column(db.Text, nullable=True)
    # The stock quantity of the item, cannot be null
    intItemStock = db.Column(db.Integer, nullable=False)
    # The minimum stock level for the item, cannot be null
    intItemMin = db.Column(db.Integer, nullable=False)
    
    # Store the image as binary data, optional field
    image = db.Column(LargeBinary, nullable=True)
    # Optional: store the original filename of the image for reference
    image_filename = db.Column(db.String(255), nullable=True)
    # Optional: store the MIME type of the image for reference
    image_mimetype = db.Column(db.String(255), nullable=True)

    # String representation of the Item object for easy debugging
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, txtItemName={self.txtItemName!r}, txtItemPrice={self.txtItemPrice!r}, txtItemDesc={self.txtItemDesc!r}, intItemStock={self.intItemStock!r}, intItemMin={self.intItemMin!r})"
        #return f"Item('{self.txtItemName}', '{self.txtItemPrice}', '{self.txtItemDesc}', '{self.txtItemStock}', '{self.txtItemMin}')

    # Additional fields related to supplier or item categories can be added here
    # supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    # ItemCategory
    # ItemPic
    # ItemBC
    # supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    # txtLogs = db.Column(db.String)


class Checkout(db.Model):
    # Define the primary key for the Checkout model
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key linking to the user who made the checkout
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # The name of the customer associated with the checkout
    customer_name = db.Column(db.String(150))
    # Relationship to CheckoutItem, allowing access to items in this checkout
    items = db.relationship('CheckoutItem', backref='checkout', lazy=True)
    # Total price of all items in the checkout, default is 0.0
    total_price = db.Column(db.Float, default=0.0)
    # Payment method used for the checkout
    payment_method = db.Column(db.String(50))
    # Amount of payment that is still outstanding
    outstanding_payment = db.Column(db.Float, default=0.0)
    # Flag indicating whether the order has been shipped
    is_shipped = db.Column(db.Boolean, default=False)
    # Flag indicating whether the order is for book distribution
    is_book_distribution = db.Column(db.Boolean, default=False)


class CheckoutItem(db.Model):
    # Define the primary key for the CheckoutItem model
    id = db.Column(db.Integer, primary_key=True)
    # Foreign key linking to the associated checkout
    checkout_id = db.Column(db.Integer, db.ForeignKey('checkout.id'))
    # Foreign key linking to the associated item
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    # Quantity of the item in this checkout, default is 1
    quantity = db.Column(db.Integer, default=1)
    # Price of the item at the time of checkout
    item_price = db.Column(db.Float)

    # Relationship to Item, allowing access to the item details from the CheckoutItem
    item = db.relationship('Item', backref='checkout_items')