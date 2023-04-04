"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
from html import escape
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import flask
from flask import Flask, request, render_template, g, redirect, Response, session,url_for
from datetime import date
from collections import defaultdict
import flask
import click
import psycopg2
from datetime import date
from sqlalchemy import text
import json


session = defaultdict(str)
product_ids = []

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "yy3266"
DATABASE_PASSWRD = "8015"
DATABASE_HOST = "34.148.107.47"  # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
'''
with engine.connect() as conn:
    create_table_command = """
        CREATE TABLE IF NOT EXISTS test (
                id serial,
                name text
        )
        """
    res = conn.execute(text(create_table_command))
    insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
    res = conn.execute(text(insert_table_command))
    # you need to commit for create, insert, update queries to reflect
    conn.commit()
'''

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback;
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#


@app.route('/')

@app.route('/home', methods=['GET','POST'])
def home():
    session['url'] = request.url

    cursor = g.conn.execute("SELECT category_name FROM category")
    category_names = []
    for result in cursor:
        category_names.append({'name': result['category_name']})  # 使用正确的字段名
    cursor.close()

    context = dict(category_names=category_names)
    return render_template("home.html", **context)




@app.route('/', methods=['GET','POST'])
def home_post():
    session['url'] = request.url
    aid = request.form.get("account", "")
    print(aid)
    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if (request.method == 'POST'):
        first_name, last_name, email, age, address, phone_number, preferences, membership, password= request.form.get("first_name", ""), request.form.get(
            "last_name", ""), request.form.get("email", ""), request.form.get("age", ""), request.form.get("address",
                                                                                                           ""), request.form.get(
            "phone_number", ""), request.form.get("preferences", ""), request.form.get("membership", ""),request.form.get("password", "")
        cursor = g.conn.execute(text("SELECT email from Customer"))
        in_table = False
        for i in cursor:
            if email == i[0]:
                in_table = True
        if not in_table:
            cursor = g.conn.execute(text("SELECT MAX(customer_id) from Customer"))
            for res in cursor:
                res = res[0]
                number_part = int(res[1:])
                prefix = res[0]
                next_number = number_part + 1
                new_string = f"{prefix}{next_number:03}"
            cursor.close()
            try:
                membership = int(membership[0])
                print("metry")
                cursor = g.conn.execute(
                    text(
                        "INSERT INTO Customer VALUES (:customer_id, :first_name, :last_name, :age, :address, :email, :phone_number, :membership, :preferences, :password)"),
                    {
                        'customer_id': new_string,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'age': age,
                        'address': address,
                        'phone_number': phone_number,
                        'membership': membership,
                        'preferences': preferences,
                        'password': password
                    }
                )
                print("excuted")
                #g.conn.commit()
                print("g.conn")
                cursor.close()
                print("cursor.close")
            except:
                print("except")
                return render_template('/signup.html')
            return redirect('/login')
        else:
            print("Customer used a existed email address, register failed. Try again.")
            return render_template('/login.html')
        #print("last")
    return render_template('/signup.html')


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    query_string = text("SELECT customer_id, password FROM Customer where email = :email")
    cursor = g.conn.execute(query_string, **{'email': email})
    customer_ids = []
    stored_password = None

    for result in cursor:
        customer_ids.append(result['customer_id'])
        stored_password = result['password']
    cursor.close()

    if len(customer_ids) == 0 or stored_password is None or password != stored_password:
        return render_template("login.html")

    session['customer_id'] = customer_ids[0]

    if "url" in session.keys():
        return redirect(session['url'])
    else:
        return redirect("/home")



@app.route('/logout' ,methods=['POST'])
def logout():
    session.clear()
    return redirect('/home')




@app.route('/category/<category_id>')
def category(category_id):
    cursor = g.conn.execute("SELECT category_name FROM category WHERE category_id = %s", category_id)
    category_name = cursor.fetchone()['category_name']
    cursor.close()

    cursor = g.conn.execute("SELECT product_name, category_id FROM product WHERE category_id = %s", category_id)
    products = []
    for result in cursor:
        products.append({'name': result['product_name'], 'category_id': result['category_id']})
    cursor.close()

    context = dict(category_name=category_name, products=products)
    return render_template("category.html", **context)

#category1
@app.route('/electronics', methods=['GET', 'POST'])
def electronics():
    session['url'] = request.url

    products = []
    
    category_name = "Electronics"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    #print(id_result)
    
    for i in id_result:
        #print(i.category_id)
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        #print(row.keys())
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("electronics.html", **context)


#category2
@app.route('/clothing', methods=['GET', 'POST'])
def clothing():
    session['url'] = request.url

    products = []
    
    category_name = "Clothing"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("clothing.html", **context)




#category3
@app.route('/home_and_garden', methods=['GET', 'POST'])
def home_and_garden():
    session['url'] = request.url

    products = []
    
    category_name = "Home and Garden"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("home_and_garden.html", **context)

#category4
@app.route('/health_and_beauty', methods=['GET', 'POST'])
def health_and_beauty():
    session['url'] = request.url

    products = []
    
    category_name = "Health and Beauty"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    #print(id_result)
    
    for i in id_result:
        #print(i.category_id)
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        #print(row.keys())
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    
    
    return render_template("health_and_beauty.html", **context)

#category5
@app.route('/toys_and_games', methods=['GET', 'POST'])
def toys_and_games():
    session['url'] = request.url

    products = []
    
    category_name = "Toys and Games"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("toys_and_games.html", **context)

#category6
@app.route('/sports_and_outdoors', methods=['GET', 'POST'])
def sports_and_outdoors():
    session['url'] = request.url

    products = []
    
    category_name = "Sports and Outdoors"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("sports_and_outdoors.html", **context)


#category7
@app.route('/book_and_media', methods=['GET', 'POST'])
def book_and_media():
    session['url'] = request.url

    products = []
    
    category_name = "Book and Media"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("book_and_media.html", **context)



#category8
@app.route('/automotive', methods=['GET', 'POST'])
def automotive():
    session['url'] = request.url

    products = []
    
    category_name = "Automotive"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("automotive.html", **context)

#category9
@app.route('/pet_supplies', methods=['GET', 'POST'])
def pet_supplies():
    session['url'] = request.url

    products = []
    
    category_name = "Pet Supplies"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("pet_supplies.html", **context)

#category10
@app.route('/food_and_beverage', methods=['GET', 'POST'])
def food_and_beverage():
    session['url'] = request.url

    products = []
    
    category_name = "Food and Beverage"
    id_cursor = g.conn.execute("SELECT category_id FROM Category WHERE category_name = %s", (category_name,))
    id_result = id_cursor.fetchall()
    id_cursor.close()
    
    for i in id_result:
        category_id = i.category_id
        
    cursor = g.conn.execute("SELECT * FROM Product WHERE category_id = %s", (category_id,))
    result = cursor.fetchall()
    cursor.close()
    
    #print(result)
    
    for row in result:
        product_id = row.product_id
        cursor = g.conn.execute("SELECT * FROM seller WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        seller_id = result[0][0]
        seller_name = result[0][2]
        
        product = {
            'product_id': row.product_id,
            'name': row.name,
            'category_id': row.category_id,
            'product_unit_price': row.product_unit_price,
            'product_dimensions': row.product_dimensions,
            'item_weight': row.item_weight,
            'manufacturer': row.manufacturer,
            "seller_id": seller_id,
            "seller_name":seller_name
        }
        
        products.append(product)
            
    context = {"products": products}
    return render_template("food_and_beverage.html", **context)



@app.route('/cart', methods = ['GET','POST'])
def cart():

    product_id = request.form['product_id']
    product_ids.append(product_id)

    cart_items = []

    for product_id in product_ids:
        cursor = g.conn.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        cursor.close()

        for row in result:
            cart_item = {
                'product_id': row.product_id,
                'product_name': row.name,
                'product_unit_price': row.product_unit_price,
                'quantity': 1
            }
            cart_items.append(cart_item)

    context = {"cart_items": cart_items}

    return render_template("cart.html", **context)




@app.route('/payment', methods=['POST'])
def payment():
    global product_ids

    error_message = None
    customer_id = session.get("customer_id", None)

    if not customer_id:
        error_message = "Please Sign Up and Login."

    if not error_message:
        order_items = []

        cursor = g.conn.execute(text("SELECT MAX(order_id) from Order_info"))
        for res in cursor:
            res = res[0]
            number_part = int(res[1:])
            prefix = res[0]
            next_number = number_part + 1
            new_order_id = f"{prefix}{next_number:03}"
        cursor.close()

        for product_id in product_ids:
            quantity = request.form.get(f'quantity-{product_id}')
            product_name = request.form.get(f'product_name-{product_id}')
            product_unit_price = request.form.get(f'product_unit_price-{product_id}')

            order_item = {
                'product_id': product_id,
                'product_name': product_name,
                'product_unit_price': float(product_unit_price),
                'quantity': int(quantity)
            }
            order_items.append(order_item)

        order_date = date.today()

        order_items_json = json.dumps(order_items)

        cursor = g.conn.execute(
            "INSERT INTO Order_info (order_id, customer_id, order_item_json, order_date) VALUES (%s, %s, %s, %s)",
            (new_order_id, customer_id, order_items_json, order_date)
        )

        cursor.close()

        product_ids = []

        return render_template("payment_success.html")

    return render_template("payment_success.html", error_message=error_message)


@app.errorhandler(400)
def bad_request(e):
    return "Bad Request: {}".format(e), 400



@app.route('/account', methods=['GET', 'POST'])
def account_post():
    session['url'] = request.url

    customer_id = session.get('customer_id', None)
    result = None
    if customer_id:
        cursor = g.conn.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
        result = cursor.fetchone()
        cursor.close()

    if result:
        context = {"customer": [{'customer_id': result.customer_id, 'first_name': result.first_name, 'last_name': result.last_name, 'age': result.age, 'address': result.address, 'email': result.email, 'phone_number': result.phone_number, 'membership': result.membership, 'preferences': result.preferences}]}
    else:
        context = {"customer": [{'customer_id': None, 'first_name': None, 'last_name': None, 'age': None, 'address': None, 'email': None, 'phone_number': None, 'membership': None, 'preferences': None}]}

    print(context)
    return render_template("account.html", **context)


@app.route('/order', methods=['GET', 'POST'])
def order_post():
    session['url'] = request.url

    customer_id = session.get('customer_id', None)

    orders = []
    if customer_id:
        cursor = g.conn.execute("SELECT * FROM Order_info WHERE customer_id = %s", (customer_id,))
        result = cursor.fetchall()
        cursor.close()

        for row in result:
            order_items = row[2]
            total_price = 0
            for item in order_items:
                # Fetch product details
                cursor = g.conn.execute("SELECT * FROM Product WHERE product_id = %s", (item['product_id'],))
                product_result = cursor.fetchone()
                cursor.close()

                # Get the product_name from the fetched product details
                item['product_name'] = product_result[1]

                total_price += item['quantity'] * item['product_unit_price']

            cursor = g.conn.execute("SELECT * FROM Customer WHERE customer_id = %s", (customer_id,))
            result = cursor.fetchall()
            first_name = result[0][1]
            last_name = result[0][2]
            cursor.close()

            order = {
                'order_id': row[0],
                'customer_id': row[1],
                'order_items': order_items,
                'order_date': row[3],
                'order_status': row[4],
                'first_name': first_name,
                'last_name': last_name,
                'total_price': total_price
            }
            orders.append(order)

    context = {"orders": orders}
    return render_template("order.html", **context)



@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    order_id = request.form['order_id']
    # Update the order_status to 'canceled' for the specified order_id
    g.conn.execute("UPDATE Order_info SET order_status = 'canceled' WHERE order_id = %s", (order_id,))
    # Redirect back to the orders page
    return redirect(url_for('order_post'))


@app.route('/submit_review', methods=['POST'])
def submit_review():

    return redirect(url_for('order_post'))



def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    #
    # example of a database query
    #
    select_query = "SELECT name from test"
    cursor = g.conn.execute(text(select_query))
    names = []
    for result in cursor:
        names.append(result[0])
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)


#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the  ("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    # accessing form inputs from user
    name = request.form['name']
    # passing params in for each variable into query
    params = {}
    params["new_name"] = name
    g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
    g.conn.commit()
    return redirect('/')


'''
@app.route('/login')
def login():
        abort(401)
        this_is_never_executed()
'''

if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

                python server.py

        Show the help text using:

                python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host="0.0.0.0", port=PORT, debug=debug, threaded=threaded)

    run()
