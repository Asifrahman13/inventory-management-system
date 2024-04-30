from flask import Blueprint, render_template, request, flash, redirect, url_for

from .models import User, Contact, Add_Productt, Cart, Supply

from werkzeug.security import generate_password_hash, check_password_hash

from . import db

from flask_login import login_user, login_required, logout_user, current_user

from sqlalchemy.sql import func

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        email = request.form.get('email')

        password = request.form.get('password')

        user = User.query.filter_by(email = email).first()

        if user:

            if check_password_hash(user.password, password):

                flash('Logged in succesfully!!', category='success')

                login_user(user, remember=True)


                return redirect(url_for('views.home'))

            else:

                flash('Incorrect Password', category='error')

        else:

            flash('No account exist with this email', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')

@login_required

def logout():

    logout_user()

    return redirect(url_for('auth.login'))

@auth.route('/registration', methods=['GET', 'POST'])

def registration():

    if request.method == 'POST':

        email = request.form.get('email')

        first_name = request.form.get('first_name')

        last_name = request.form.get('last_name')

        password1 = request.form.get('password1')

        password2 = request.form.get('password2')

        user = User.query.filter_by(email = email).first()

        if user:

            flash('Already exist account with this email', category='error')

        elif len(email) == 0 or len(first_name) == 0 or len(password1) == 0 or len(password2) == 0:

            flash('Information missing', category='error')

        elif len(email) < 4:

            flash('Email must be greater than 4 characters', category='error')

        elif len(first_name) < 2:

            flash('First Name must be greater than 1 character', category='error')

        elif password1 != password2:

            flash('The password doesn\'t match', category='error')

        elif len(password1) < 7:

            flash('The password must be at least 7 characters', category='error')

        else:

            try:

                new_user = User(email=email, first_name = first_name, password = generate_password_hash(password1, method='sha256'))

                db.session.add(new_user)

                db.session.commit()

                # login_user(new_user, remember=True)

                flash('Account Created', category='success')

            except:

                flash('Something is wrong. Try Again!!', category='error')

            return redirect(url_for('views.home'))

    return render_template("registration.html", user=current_user)
    

@auth.route('/cart', methods = ['GET', 'POST'])

@login_required

def cart():

    if request.method == 'POST':

        product_title = request.form.get('product_title')

        product_price = request.form.get('product_price')

        entry = Cart(title = product_title, price = product_price)

        db.session.add(entry)

        db.session.commit()

    products = Cart.query.all()

    xyz = db.session.query(func.sum(Cart.price)).all()

    xyz = xyz[0][0]

    if xyz == None:

        xyz = 0

    return render_template("cart.html", user=current_user, products=products, subtotal = xyz, grand_total = xyz+5)

@auth.route('/category')

def category():

    add_product = Add_Productt.query.all()

    return render_template("category.html", user=current_user, add_product = add_product)

# @auth.route('/checkout')

# def checkout():

#     cart = Cart.query.all()

#     return render_template("checkout.html", user=current_user, cart = cart)

# @auth.route('/confirmation')

# def confirmation():

#     return render_template("confirmation.html")

@auth.route('/contact', methods = ['GET', 'POST'])

def contact():

    if request.method == 'POST':

        message = request.form.get('message')

        name = request.form.get('name')

        email = request.form.get('email')

        subject = request.form.get('subject')

        entry = Contact(message=message, name = name, email = email, subject = subject)

        db.session.add(entry)

        db.session.commit()

        flash('The Message has been sent. We will contact with you soon', category='success')

        return redirect(url_for('auth.contact'))

    return render_template("contact.html", user=current_user)

# @auth.route('/elements')

# def elements():

#     return render_template("elements.html")

@auth.route('/single_product/<int:idd>', methods = ['GET', 'POST'])

def single_product(idd):

    product = Add_Productt.query.get_or_404(idd)

    return render_template("single_product.html", user=current_user, product = product)

# @auth.route('/tracking')

# def tracking():

#     return render_template("tracking.html", user=current_user)

@auth.route('/admin')

@login_required

def admin():

    id = current_user.id

    if id == 9:

        return render_template("admin.html", user=current_user)

    else:

        flash("You've no permission to access!!")

        return redirect(url_for('auth.login'))

@auth.route('/contact_messages', methods = ['GET'])

def retriveList():

    contact = Contact.query.all()

    return render_template("contact_messages.html", user = current_user, contact = contact)


@auth.route('/add_product', methods = ['GET', 'POST'])

@login_required

def add_product():

    if request.method == 'POST':

        title = request.form.get('title')

        price = request.form.get('price')

        description = request.form.get('description')

        quantity = request.form.get('quantity')

        entry = Add_Productt(title=title, price = price, description = description, quantity = quantity)

        db.session.add(entry)

        db.session.commit()

        flash('Product Added', category='success')

        return redirect(url_for('auth.add_product'))

    return render_template("add_product.html", user=current_user)


@auth.route('/product_list')

@login_required

def product_list():

    add_product = Add_Productt.query.all()

    return render_template("product_list.html", user=current_user, add_product = add_product)


@auth.route('/<int:idd>/edit',methods = ['GET','POST'])

@login_required

def update(idd):

    product = Add_Productt.query.filter_by(idd=idd).first()

    if request.method == 'POST':

        if product:

            db.session.delete(product)
            
            db.session.commit()

        title = request.form['title']

        price = request.form['price']

        description = request.form['description']

        quantity = request.form['quantity']

        product = Add_Productt(
            
            title = title,
            
            price = price,

            description = description,

            quantity = quantity,


        )

        db.session.add(product)
        
        db.session.commit()
        
        return redirect(url_for('auth.product_list'))     
        
    return render_template('add_product.html', product = product, user=current_user)

@auth.route('/<int:idd>/delete', methods=['GET','POST'])

@login_required

def delete(idd):

    product = Add_Productt.query.filter_by(idd=idd).first()

    if request.method == 'POST':

        if product:

            db.session.delete(product)

            db.session.commit()

            return redirect(url_for('auth.product_list'))

    return render_template('delete.html', user=current_user)

@auth.route('/<int:id>/delete_user', methods=['GET','POST'])

@login_required

def delete_user(id):

    userr = User.query.filter_by(id=id).first()

    if request.method == 'POST':

        if userr:

            db.session.delete(userr)

            db.session.commit()

            return redirect(url_for('auth.user_list'))

    return render_template('delete_user.html', user=current_user)

@auth.route('/user_list')

@login_required

def user_list():

    userr = User.query.all()

    return render_template("user_list.html", user=current_user, userr = userr)

@auth.route('/<int:serial>/delete_cart', methods=['GET','POST'])

@login_required

def delete_cart(serial):

    product = Cart.query.filter_by(serial=serial).first()

    if request.method == 'POST':

        if product:

            db.session.delete(product)

            db.session.commit()

            return redirect(url_for('auth.cart'))

    return render_template('delete_cart.html', user=current_user)

@auth.route('/search', methods=['GET', 'POST'])

def search():

    if request.method == 'POST':

        searched = request.form.get('searched')

        add_product = Add_Productt.query.all()

        return render_template("search.html", user=current_user, add_product = add_product, searched = searched)  


@auth.route('/shop_manager')

@login_required

def shop_manager():

    id = current_user.id

    if id != 9:

        return render_template("shop_manager.html", user=current_user)

    else:

        flash("You've no permission to access!!")

        return redirect(url_for('auth.login'))
    


@auth.route('/<int:srl>/delete_message', methods=['GET','POST'])

@login_required

def delete_message(srl):

    msg = Contact.query.filter_by(srl=srl).first()

    if request.method == 'POST':

        if msg:

            db.session.delete(msg)

            db.session.commit()

            return redirect(url_for('auth.retriveList'))

    return render_template('delete_message.html', user=current_user)















@auth.route('/supply_product', methods = ['GET', 'POST'])

@login_required

def supply():

    if request.method == 'POST':

        title = request.form.get('title')

        price = request.form.get('price')

        description = request.form.get('description')

        quantity = request.form.get('quantity')

        entry = Supply(title=title, price = price, description = description, quantity = quantity)

        db.session.add(entry)

        db.session.commit()

        flash('Product Added', category='success')

        return redirect(url_for('auth.supply'))

    return render_template("supply_product.html", user=current_user)




@auth.route('/supplier')

@login_required

def supplier():

    id = current_user.id

    if id == 19:

        return render_template("supplier.html", user=current_user)

    else:

        flash("You've no permission to access!!")

        return redirect(url_for('views.home'))
    


@auth.route('/supply_list')

@login_required

def supply_list():

    supply = Supply.query.all()

    return render_template("supply_list.html", user=current_user, supply = supply)



@auth.route('/supply_category')

def supply_category():

    supply = Supply.query.all()

    return render_template("supply_category.html", user=current_user, supply = supply)



@auth.route('/supply_single_product/<int:sp_id>', methods = ['GET', 'POST'])

def supply_single_product(sp_id):

    supply = Supply.query.get_or_404(sp_id)

    return render_template("supply_single_product.html", user=current_user, supply = supply)
