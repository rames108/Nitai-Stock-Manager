# Import necessary modules and classes
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify, send_file
from flask_mail import Message #Mail,
from .models import User, Item, Checkout, CheckoutItem, Supplier, Customer # Import desired model from models.py
from werkzeug.security import generate_password_hash, check_password_hash  # Import password hashing functions
from. import db, mail  # Import database instance from __init__.py
from flask_login import login_user, login_required, logout_user, current_user  # Import Flask-Login functions
from flask_wtf import FlaskForm  # Import Flask-WTF form class
from wtforms import StringField, SubmitField  # Import WTForms fields
from wtforms.validators import DataRequired, Email  # Import WTForms validators
from io import BytesIO
import random
#import base64

# Create an instance of Blueprint for authentication routes
auth = Blueprint('auth', __name__)


#---------------------------------------------------------------Login page-----------------------------------------------------------------



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
        name = request.form.get('firstName')
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
        elif len(name) < 2:
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
            new_user = User(email=email, name=name, password=generate_password_hash(
                password1, method='scrypt'))
            # Add user to database
            db.session.add(new_user)
            db.session.commit()
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
            return redirect(url_for('auth.otp', user=current_user))
        else:
            flash('Email does not exist in our records.', category='error')
    return render_template('forpass.html', user=current_user)

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
    return render_template('otp.html', user=current_user)



#---------------------------------------------------------------Selling page-----------------------------------------------------------------
@auth.route('/btnSelling')  # Define a route for the selling page
@login_required  # Ensure that the user is logged in before accessing this route
def btnSelling():
    items = Item.query.all()  # Get all items from the database
    return render_template('selling.html', user=current_user, items=items)  # Render the selling page with the current user and items

# @auth.route('/btnAddItem', methods=['POST'])  # This route is commented out, possibly for future use
@auth.route('/btnAddItemPage')  # Define a route for the add item page
@login_required  # Ensure that the user is logged in before accessing this route
def btnAddItemPage():
    if current_user.is_admin == "True":
        return render_template('additem.html', user=current_user)  # Render the add item page with the current user
    else:
        flash('Admin users only', category='error')
        return redirect(url_for('auth.btnSelling'))

@auth.route('/btnAddItem', methods=["POST"])  # Define a route for adding an item, accepting POST requests
@login_required  # Ensure that the user is logged in before accessing this route
def btnAddItem():
    if request.method == "POST":  # Check if the request method is POST
        # Get form data from the request
        item_name = request.form.get('item_name')  # Retrieve the item name
        price = request.form.get('price')  # Retrieve the item price
        item_desc = request.form.get('item_desc')  # Retrieve the item description
        stock = request.form.get('stock')  # Retrieve the stock quantity
        min_stock = request.form.get('min_stock')  # Retrieve the minimum stock level
        
        # Handle image upload
        image = request.files.get('image')  # Get the uploaded image file
        image_data = None  # Initialize variable to hold image data
        image_filename = None  # Initialize variable to hold image filename
        image_mimetype = None  # Initialize variable to hold image MIME type
        
        if image and image.filename:  # Check if an image was uploaded
            # Read the image file
            image_data = image.read()  # Read the content of the image file
            image_filename = image.filename  # Store the filename of the image
            image_mimetype = image.mimetype  # Store the MIME type of the image

        # Validate inputs
        if not item_name or not price:  # Check if required fields are filled
            flash("Please fill in all required fields", category='error')  # Flash an error message
            return redirect(url_for('auth.btnAddItemPage'))  # Redirect back to the add item page
        
        # Check for existing item
        existing_item = Item.query.filter_by(txtItemName=item_name).first()  # Query the database for an existing item with the same name
        if existing_item:  # If an existing item is found
            flash("Item already exists", category='error')  # Flash an error message
            return redirect(url_for('auth.btnAddItemPage'))  # Redirect back to the add item page

        # Create new item with image
        new_item = Item(
            txtItemName=item_name,  # Set the item name
            txtItemPrice=price,  # Set the item price
            txtItemDesc=item_desc,  # Set the item description
            intItemStock=stock,  # Set the stock quantity
            intItemMin=min_stock,  # Set the minimum stock level
            image=image_data,  # Set the image data
            image_filename=image_filename,  # Set the image filename
            image_mimetype=image_mimetype  # Set the image MIME type
        )

        db.session.add(new_item)  # Add the new item to the database session
        db.session.commit()  # Commit the session to save changes to the database
        
        flash("Item added successfully", category='success')  # Flash a success message
        return redirect(url_for('auth.btnSelling'))  # Redirect to the selling page

    return render_template('selling.html', user=current_user)  # If not a POST request, render the selling page with the current user

# Add a route to serve images
@auth.route('/image/<int:item_id>')  # Define a route to serve images based on item ID
def serve_image(item_id):
    item = Item.query.get_or_404(item_id)  # Retrieve the item from the database or return a 404 if not found
    
    if item.image:  # Check if the item has an associated image
        return send_file(  # Send the image file to the client
            BytesIO(item.image),  # Convert image data to a BytesIO object
            mimetype=item.image_mimetype,  # Set the MIME type for the image
            as_attachment=False  # Serve the image inline, not as an attachment
        )
    
    return '', 404  # Return a 404 error if no image is found


@auth.route('/remove_item/<int:item_id>', methods=['POST'])  # Define a route to remove an item based on item ID
@login_required  # Ensure that the user is logged in before accessing this route
def remove_item(item_id):
    try:
        # Find the item in the database
        item = Item.query.get(item_id)  # Retrieve the item by ID
        if current_user.is_admin == "True":# Checks whether the user removing the item is an admin
            if item:  # If the item exists
                # Remove the item from the database
                db.session.delete(item)  # Mark the item for deletion
                db.session.commit()  # Commit the changes to the database
                # Return a JSON response indicating success
                return jsonify({'success': True, 'message': 'Item removed successfully'})
            else:
                # Item not found
                return jsonify({'success': False, 'message': 'Item not found'}), 404  # Return a 404 error if item not found
        else:
            flash('Admin users only', category='error')
    
    except Exception as e:
        # Log the error and return an error response
        print(f"Error removing item: {str(e)}")  # Print the error message to the console
        return jsonify({'success': False, 'message': 'An error occurred while removing the item'}), 500  # Return a 500 error


@auth.route('/item_info/<int:item_id>')  # Define a route to retrieve item information based on item ID
@login_required  # Ensure that the user is logged in before accessing this route
def item_info(item_id):
    item = Item.query.get(item_id)  # Retrieve the item from the database
    if item:  # If the item exists
        return render_template('item_info.html', item=item, user=current_user)  # Render the item information page
    else:
        flash('Item not found', category='error')  # Flash an error message if the item is not found
        return redirect(url_for('btnSelling'))  # Redirect to the selling page


# Route to add item to checkout
@auth.route('/add_to_checkout/<int:item_id>', methods=['POST'])  # Define a route to add an item to the checkout
@login_required  # Ensure that the user is logged in before accessing this route
def add_to_checkout(item_id):
    item = Item.query.get_or_404(item_id)  # Retrieve the item or return a 404 if not found
    checkout = Checkout.query.filter_by(user_id=current_user.id).first()  # Get the user's checkout session
    
    if checkout is None:  # If the user does not have an existing checkout
        checkout = Checkout(user_id=current_user.id)  # Create a new checkout session
        db.session.add(checkout)  # Add the new checkout session to the database
    
    # Check if item is already in checkout
    checkout_item = CheckoutItem.query.filter_by(checkout=checkout, item_id=item.id).first()  # Check if the item is already in the checkout
    if checkout_item:  # If the item is already in the checkout
        checkout_item.quantity += 1  # Increase the quantity of the item
    else:
        # If the item is not in the checkout, create a new checkout item
        checkout_item = CheckoutItem(checkout=checkout, item_id=item.id, item_price=item.txtItemPrice)
        db.session.add(checkout_item)  # Add the new checkout item to the database

    db.session.commit()  # Commit the changes to the database
    return jsonify({'success': True})  # Return a success response


# Route to view checkout
@auth.route('/checkout')  # Define a route to view the checkout
@login_required  # Ensure that the user is logged in before accessing this route
def view_checkout():
    checkout = Checkout.query.filter_by(user_id=current_user.id).first()  # Retrieve the user's checkout session
    customers = Customer.query.all()  
    return render_template('checkout.html', customers=customers, checkout=checkout, user=current_user)  # Render the checkout page


# Route to update item quantity in checkout
@ auth.route('/update_checkout_item/<int:item_id>', methods=['POST'])  # Define a route to update the quantity of an item in the checkout
@login_required  # Ensure that the user is logged in before accessing this route
def update_checkout_item(item_id):
    quantity = request.form.get('quantity')  # Get the new quantity from the form data
    checkout_item = CheckoutItem.query.get(item_id)  # Retrieve the checkout item by ID
    if checkout_item:  # If the checkout item exists
        checkout_item.quantity = quantity  # Update the quantity of the checkout item
        db.session.commit()  # Commit the changes to the database
        return jsonify({'success': True})  # Return a success response
    return jsonify({'success': False, 'message': 'Item not found'})  # Return an error response if the item is not found


# Route to remove item from checkout
@auth.route('/remove_checkout_item/<int:item_id>', methods=['POST'])  # Define a route to remove an item from the checkout
@login_required  # Ensure that the user is logged in before accessing this route
def remove_checkout_item(item_id):
    checkout_item = CheckoutItem.query.get(item_id)  # Retrieve the checkout item by ID
    if checkout_item:  # If the checkout item exists
        db.session.delete(checkout_item)  # Mark the checkout item for deletion
        db.session.commit()  # Commit the changes to the database
        return jsonify({'success': True})  # Return a success response
    return jsonify({'success': False, 'message': 'Item not found'})  # Return an error response if the item is not found


@auth.route('/submit_checkout', methods=['POST'])  # Define a route to submit the checkout
@login_required  # Ensure that the user is logged in before accessing this route
def submit_checkout():
    customer_name = request.form.get('customer_name')  # Get the customer's name from the form data
    payment_method = request.form.get('payment_method')  # Get the payment method from the form data
    amount_paid = request.form.get('amount_paid')  # Get the amount paid from the form data

    checkout = Checkout.query.filter_by(user_id=current_user.id).first()  # Retrieve the user's checkout session
    if checkout:  # If the checkout session exists
        checkout.customer_name = customer_name  # Set the customer's name in the checkout session
        checkout.payment_method = payment_method  # Set the payment method in the checkout session
        checkout.outstanding_payment = float(amount_paid) - checkout.total_price  # Calculate outstanding payment
        
        # Update stock for each item in the checkout
        for item in checkout.items:
            item_record = Item.query.get(item.item_id)  # Get the item record from the database
            if item_record:  # If the item exists
                item_record.intItemStock -= item.quantity  # Reduce the stock by the quantity purchased
                if item_record.intItemStock < 0:  # Check if stock goes negative
                    flash(f'Insufficient stock for {item_record.txtItemName}.', category='error')
                    return redirect(url_for('auth.view_checkout'))  # Redirect to the checkout view page

        db.session.commit()  # Commit the changes to the database

        db.session.delete(checkout)  # Delete the checkout session
        db.session.commit()  # Commit the deletion
        
        flash('Checkout completed successfully!', category='success')  # Flash a success message
        return redirect(url_for('auth.btnSelling'))  # Redirect to the selling page

    flash('Checkout failed. Please try again.', category='error')  # Flash an error message if checkout fails
    return redirect(url_for('auth.view_checkout'))  # Redirect to the checkout view page

@auth.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')  # Get the search query from the request
    if query:
        # Search for items that match the query in name or description
        items = Item.query.filter(
            (Item.txtItemName.ilike(f'%{query}%')) | 
            (Item.txtItemDesc.ilike(f'%{query}%'))
        ).all()
    else:
        items = Item.query.all()  # If no query, return all items

    return render_template('selling.html', user=current_user, items=items)  # Render the selling page with the filtered items

#---------------------------------------------------------------Customers page-----------------------------------------------------------------

@auth.route('/btnCustomers')
@login_required
def btnCustomers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers, user=current_user)

@auth.route('/customers_info/<int:customer_id>')
@login_required
def customers_info(customer_id):
    chosen_customer = Customer.query.get(customer_id)
    if chosen_customer:
        if current_user.is_admin == "True":
            return render_template('customers_info.html', chosen_customer=chosen_customer, user=current_user)
        else:
            flash('Admin users only', category='error')
            return redirect(url_for('auth.btnCustomers'))
    else:
        flash('User  not found', category='error')
        return redirect(url_for('auth.btnCustomers'))

@auth.route('/btnCreateCustomer', methods=['GET', 'POST'])
@login_required
def btnCreateCustomer():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
#        firstreg = request.form.get('firstreg')#set this to date the customer is made
#        outpay = request.form.get('outpay')
#        logs = request.form.get('logs')

        # Query database for user with matching email
        Customers = Customer.query.filter_by(email=email).first()
        if Customers:
            # Flash error message for existing email
            flash('Customer already exists.', category='error')
        elif len(email) < 4:
            # Flash error message for short email
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            # Flash error message for short first name
            flash('First name must be greater than 1 character.', category='error')
        else:
            # Create new user instance
            new_customer = Customer(email=email, name=name)#,  outpay=outpay, logs=logs)#firstreg=firstreg,)
            # Add user to database
            db.session.add(new_customer)
            db.session.commit()
            # Flash success message
            flash('New customer created!', category='success')
            # Redirect to home page
            return redirect(url_for('auth.btnCustomers'))
    return render_template('newcustomer.html', user=current_user)

@auth.route('/searchCustomers', methods=['GET'])
@login_required
def searchCustomers():
    query = request.args.get('query')  # Get the search query from the request
    if query:
        # Search for items that match the query in name or description
        customers = Customer.query.filter(
            (Customer.name.ilike(f'%{query}%'))
        ).all()
    else:
        customers = customers.query.all()  # If no query, return all items

    return render_template('customers.html', user=current_user, customers=customers)  # Render the selling page with the filtered items



#---------------------------------------------------------------Suppliers page-----------------------------------------------------------------

@auth.route('/btnSuppliers')
@login_required
def btnSuppliers():
    suppliers = Supplier.query.all()  # Get all users from the database
    return render_template('suppliers.html', suppliers=suppliers, user=current_user)

@auth.route('/supplier_info/<int:supplier_id>')
@login_required
def supplier_info(supplier_id):
    chosen_supplier = Supplier.query.get(supplier_id)
    if chosen_supplier:
        if current_user.is_admin == "True":
            return render_template('supplier_info.html', chosen_supplier=chosen_supplier, user=current_user)
        else:
            flash('Admin users only', category='error')
            return redirect(url_for('auth.btnSuppliers'))
    else:
        flash('User  not found', category='error')
        return redirect(url_for('auth.btnSuppliers'))

@auth.route('/btnCreateSupplier', methods=['GET', 'POST'])
@login_required
def btnCreateSupplier():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        name = request.form.get('name')
        location = request.form.get('location')
        description = request.form.get('description')

        # Query database for user with matching email
        supplier = Supplier.query.filter_by(email=email).first()
        user = User.query.filter_by(email=email).first()
        if supplier:
            # Flash error message for existing email
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            # Flash error message for short email
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            # Flash error message for short first name
            flash('First name must be greater than 1 character.', category='error')
        else:
            # Create new user instance
            new_supplier = Supplier(email=email, name=name, location=location, description=description)
            # Add user to database
            db.session.add(new_supplier)
            db.session.commit()
            # Flash success message
            flash('New supplier created!', category='success')
            # Redirect to home page
            return redirect(url_for('auth.btnSuppliers'))
    return render_template('newsupplier.html', user=current_user)

@auth.route('/searchSuppliers', methods=['GET'])
@login_required
def searchSuppliers():
    query = request.args.get('query')  # Get the search query from the request
    if query:
        # Search for items that match the query in name or description
        suppliers = Supplier.query.filter(
            (Supplier.name.ilike(f'%{query}%'))
        ).all()
    else:
        suppliers = Supplier.query.all()  # If no query, return all items

    return render_template('suppliers.html', user=current_user, suppliers=suppliers)  # Render the selling page with the filtered items


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
    return render_template('users.html', users=users, user=current_user)

@auth.route('/user_info/<int:user_id>')
@login_required
def user_info(user_id):
    chosen_user = User.query.get(user_id)
    if chosen_user:
        if current_user.is_admin == "True":
            return render_template('user_info.html', chosen_user=chosen_user, user=current_user)
        else:
            flash('Admin users only', category='error')
            return redirect(url_for('auth.btnUsers'))
    else:
        flash('User  not found', category='error')
        return redirect(url_for('auth.btnUsers'))

@auth.route('/new_user')
@login_required
def new_user():
    return render_template('newuser.html', user=current_user)

@auth.route('/create_user', methods=['POST'])
@login_required
def create_user():
    # Check if request method is POST
    print("CHECKING FOR USER CREATION")
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin')

        # Query database for user with matching email
        user = User.query.filter_by(email=email).first()
        if user:
            # Flash error message for existing email
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            # Flash error message for short email
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            # Flash error message for short first name
            flash('First name must be greater than 1 character.', category='error')
        elif len(password) < 7:
            # Flash error message for short password
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Create new user instance
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt'), is_admin=is_admin)
            # Add user to database
            db.session.add(new_user)
            db.session.commit()
            # Log user in
            login_user(new_user, remember=True)
            # Flash success message
            flash('Account created!', category='success')
            # Redirect to home page
            return redirect(url_for('auth.btnUsers'))

    # Render sign-up template with current user
    return render_template("newuser.html", user=current_user)#need to change

@auth.route('/searchUsers', methods=['GET'])
@login_required
def searchUsers():
    query = request.args.get('query')  # Get the search query from the request
    if query:
        # Search for items that match the query in name or description
        users = User.query.filter(
            (User.name.ilike(f'%{query}%'))
        ).all()
    else:
        users = User.query.all()  # If no query, return all items

    return render_template('users.html', user=current_user, users=users)  # Render the selling page with the filtered items
