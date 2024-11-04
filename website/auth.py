# Import necessary modules and classes
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_mail import Mail, Message
from.models import User, Item  # Import desired model from models.py
from werkzeug.security import generate_password_hash, check_password_hash  # Import password hashing functions
from. import db, mail  # Import database instance from __init__.py
from flask_login import login_user, login_required, logout_user, current_user  # Import Flask-Login functions
from flask_wtf import FlaskForm  # Import Flask-WTF form class
from wtforms import StringField, SubmitField  # Import WTForms fields
from wtforms.validators import DataRequired, Email  # Import WTForms validators
import random

# Create an instance of Blueprint for authentication routes
auth = Blueprint('auth', __name__)

# Login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Check if request method is POST
    if request.method == 'POST':
        # Get email and password from form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Query database for user with matching email
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if password matches hashed password in database
            if check_password_hash(user.password, password):
                # Flash success message and log user in
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                # Redirect to home page
                return redirect(url_for('views.home'))
            else:
                # Flash error message for incorrect password
                flash('Incorrect password, try again.', category='error')
        else:
            # Flash error message for non-existent email
            flash('Email does not exist.', category='error')

    # Render login template with current user
    return render_template("login.html", user=current_user)

# Logout route
@auth.route('/logout')
@login_required
def logout():
    # Log user out
    logout_user()
    # Redirect to login page
    return redirect(url_for('auth.login'))

# Sign-up route
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Check if request method is POST
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Query database for user with matching email
        user = User.query.filter_by(email=email).first()
        if user:
            # Flash error message for existing email
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            # Flash error message for short email
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            # Flash error message for short first name
            flash('First name must be greater than 1 character.', category='error')
        elif password1!= password2:
            # Flash error message for mismatched passwords
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            # Flash error message for short password
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Create new user instance
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='scrypt'))
            # Add user to database
            db.session.add(new_user)
            db.session.commit()
            # Log user in
            login_user(new_user, remember=True)
            # Flash success message
            flash('Account created!', category='success')
            # Redirect to home page
            return redirect(url_for('views.home'))

    # Render sign-up template with current user
    return render_template("sign_up.html", user=current_user)



def generate_otp():
    return str(random.randint(100000, 999999))

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send OTP')

class OTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired()])
    submit = SubmitField('Verify')

def send_otp_email(email, otp):# sends email with the otp to the user trying to enter
    msg = Message("OTP Verification for Nitai Stock Manager", sender="your_email@gmail.com", recipients=[email])
    msg.body = f"Your OTP is: {otp}"# The important part of the email, that allows the user to enter the system
    mail.send(msg)# This function sends the email

@auth.route('/forpass', methods=['GET', 'POST'])
def forpass():
    if request.method == 'POST':
        email = request.form.get('email')# gets the form data directly from forpass.html
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate and store OTP in session
            otp = generate_otp()
            session['user_otp'] = otp
            session['email'] = email
            
            # Send OTP to user's email
            send_otp_email(email, otp)
            
            flash('OTP sent to your email address. Please check your email to verify.')
            return redirect(url_for('otp.html'), user=current_user)
        else:
            flash('Email does not exist in our records.', category='error')
    return render_template('forpass.html')

@auth.route('/otp', methods=['GET', 'POST'])
def otp():
    if request.method=="POST":
        entered_otp = request.form.get('otp')
        # Check if OTP is valid
        if 'user_otp' in session and entered_otp == session['user_otp']:
            # Get user associated with email and log them in
            user = User.query.filter_by(email=session['email']).first()
            if user:
                login_user(user)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.home'))  # Redirect to your protected route
            else:
                flash('User  not found', category='error')
        else:
            flash('Invalid OTP', category='error')
    return render_template('otp.html')



#---------------------------------------------------------------Selling page-----------------------------------------------------------------

@auth.route('/btnSelling')
@login_required
def btnSelling():
    items = Item.query.all()  # Get all items from the database
    return render_template('selling.html', user=current_user, items=items)

#@auth.route('/btnAddItem', methods=['POST'])
@auth.route('/btnAddItemPage')
@login_required
def btnAddItemPage():
    return render_template('additem.html', user=current_user)

@auth.route('/btnAddItem', methods=["POST"])
@login_required
def btnAddItem():
    if request.method == "POST":#submitting data
        item_name = request.form.get('item_name')#retrieving user submitted data
        price = request.form.get('price')
        item_desc = request.form.get('item_desc')
        stock = request.form.get('stock')
        min_stock = request.form.get('min_stock')
        #image = request.form.get('image')
        
        if not item_name or not price:
            flash("Please fill in all fields", category='error')
            return redirect(url_for('btnAddItemPage'))
        
        existing_item = Item.query.filter_by(txtItemName=item_name).first()# this algorithm is so that there is no duplicate records (with same name)
        if existing_item:
            flash("Item already exists", category='error')
            return redirect(url_for('auth.btnAddItemPage'))

        new_item = Item(txtItemName=item_name, txtItemPrice=price, txtItemDesc=item_desc, intItemStock=stock, intItemMin=min_stock)#, image=image)#assigning user submitted data to a record

        db.session.add(new_item)
        db.session.commit()#adding item to database
        flash("Item added", category='success')

    return render_template('selling.html', user=current_user)#, items=items)#if item is added

@auth.route('/item_info/<int:item_id>')#retrieves information from database then displays on rendered page
@login_required
def item_info(item_id):
    item = Item.query.get(item_id)
    if item:
        return render_template('item_info.html', item=item, user=current_user)
    else:
        flash('Item not found', category='error')
        return redirect(url_for('btnSelling'))

#@auth.route('/item/<int:item_id>')
#@login.required
#def item_info(item_id):
#    # Get the item from the database or wherever you store it
#    item = Item.query.get(item_id)
#    if item is None:
#        abort(404)
#    return render_template('item_info.html', item=item)


#----------------------

@auth.route('/btnDashboard')
@login_required
def btnDashboard():
    return render_template('dashboard.html', user=current_user)

@auth.route('/btnCustomers')
@login_required
def btnCustomers():
    return render_template('customers.html', user=current_user)


#---------------------------------------------------------------Suppliers page-----------------------------------------------------------------

@auth.route('/btnSuppliers')
@login_required
def btnSuppliers():
    suppliers = Supplier.query.all()  # Get all users from the database
    return render_template('suppliers.html', user=current_user)

#@auth.route('/item_info/<int:item_id>')#retrieves information from database then displays on rendered page
#@login_required
#def item_info(item_id):
#    item = Item.query.get(item_id)
#    if item:
#        return render_template('item_info.html', item=item, user=current_user)
#    else:
#        flash('Item not found', category='error')
#        return redirect(url_for('btnSelling'))



#---------------------------------------------------------------Users page-----------------------------------------------------------------

@auth.route('/btnUsers')
@login_required
def btnUsers():
    users = User.query.all()  # Get all users from the database
    return render_template('users.html',  users=users, user=current_user)

#establish clarity between current_user and chosen user to be displayed
#the int user_id has some issues, primary key for each record but doesnt pull the corresponding record for the id
@auth.route('/user_info/<int:user_id>')#retrieves information from database then displays on rendered page
@login_required
def user_info(user_id):
    chosen_user = User.query.get(user_id)
    if chosen_user:
        return render_template('user_info.html', chosen_user=chosen_user, user=current_user)
    else:
        flash('User not found', category='error')
        return redirect(url_for('btnUsers'))
