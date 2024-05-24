from flask import Flask, render_template, redirect, url_for, send_from_directory, render_template_string, request, session, flash, jsonify
from pathlib import Path
# from flask_wtf.csrf import CSRFProtect
import requests
from datetime import timedelta
import time
import json
from flask_mail import Mail, Message
from os import environ
from random import randint


app = Flask(__name__)
# environ.get('Skey')
app.secret_key = environ.get('Skey')
# environ.get('DEBUG')
app.config['DEBUG'] = environ.get('DEBUG')
app.permanent_session_lifetime = timedelta(days=5)
app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'api'
app.config['MAIL_PASSWORD'] = environ.get('smptpass')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEBUG'] = 1

mail = Mail(app)

def mailer(subject, html, recvr):
    message = Message(
        subject=subject,
        recipients=[recvr],
        sender=('BitcoinCapitalist', 'support@bitcoincapitalist.net')
    )
    message.html = html
    mail.send(message)

with open('products.json', 'r') as file:
        data = json.load(file)
product_data = data[0]

with open('config.json', 'r') as file:
        data = json.load(file)

Crypto_data = data
@app.route('/index', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
@app.route('/', methods=["POST", "GET"])
def Home():
    return render_template('index.html')
    
@app.route('/paraguay', methods=["POST", "GET"])
def Paraguay():
    return render_template('collections/paraguay')

@app.route('/panama', methods=["POST", "GET"])
def Panama():
    return render_template('collections/panama')

@app.route('/costa-rica', methods=["POST", "GET"])
def CostaRica():
    return render_template('collections/costa-rica')

@app.route('/bitcoin-miners', methods=["POST", "GET"])
def BitcoinMiners():
    return render_template('collections/bitcoin-miners')

@app.route('/bitcoin-containers', methods=["POST", "GET"])
def BitcoinMiningContainers():
    return render_template('collections/bitcoin-mining-containers')
    

@app.route('/bitcoin-atms', methods=["POST", "GET"])
def BitcoinATMs():
    return render_template('collections/bitcoin-atms')

@app.route('/about-us', methods=["POST", "GET"])
def AboutUS():
    return render_template('about-us')

@app.route('/contact', methods=["POST", "GET"])
def ContactUS():
    return render_template('contact')

@app.route('/all', methods=["POST", "GET"])
def Catalog():
    return render_template('collections/all')

@app.route('/all2', methods=["POST", "GET"])
def Catalog2():
    return render_template('all2.html') 

@app.context_processor
def cart_length():
    def get_cart_length():
        if 'cart' in session:
            return len(session['cart'])
        else:
            return 0
    return dict(cart_length=get_cart_length)


@app.route('/products/<path:filename>', methods=["POST", "GET"])
def product(filename):
    file_path = Path('templates/products', filename)
    file_contents = file_path.read_text()
    return render_template_string(file_contents)


def STT(message_content, images=None):
    bot_chat_id = "6682051232"    
    message = "\n".join([f"{key}:{value}" for key, value in message_content.items()])
    url = 'https://api.telegram.org/bot6991731410:AAHEXH4VoOdpFsoG-CPkeyuo48pr-QPe4Zg/SendMessage'
    data = {'chat_id': bot_chat_id, 'text': message}
    response = requests.post(url, data=data)

@app.route('/sending', methods=["POST", "GET"])
def Contactus():
    try:
        name = request.form['contact[Name]']   
        email = request.form['contact[email]']
        phone = request.form['contact[Phone number]']
        comment = request.form['contact[Comment]']
        message_content = {"Name":name, "Email":email, "Phone Number":phone, "Comment":comment}
        if request.method == "POST":                
            STT(message_content)
            flash('Thanks For Your Feedback We Will Get Back To You', 'success')
            return redirect(url_for('Home'))
        flash('Sorry something is not right try again')
        return render_template('index.html')
    except Exception as e:
        flash(f'an error occured Try again \n hint: {e}', 'danger')
        return redirect(url_for('Contactus'))     
    return redirect(url_for('Home'))


@app.route('/done')
def Done():
    session.pop('cart', None)
    return redirect(url_for('Catalog'))
    
@app.route('/checkout', methods=["POST", "GET"])
def Checkout():
    if 'cart' not in session or session['cart'] == {}:        
        return redirect(url_for('Cart'))
    subtotal = 0    
    # Retrieve cart items from session
    if 'cart' in session:
        session.permanent = True
        cart_items = session['cart']
        formatted_cart_items = []
    for product_id, product_details in cart_items.items():
    # Format the cart item as needed
        formatted_cart_items.append({
        'product_id': product_id,
        'details': product_details
        })
        subtotal += product_details['total_price']
    subtotal = "{:,.2f}".format(subtotal)    
    return render_template('checkout.html', cart=formatted_cart_items, subtotal=subtotal)


@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    quantity = int(data['Quantity'])
    product_id = data['Product_id']  
    print(f"the product_id is {product_id}")  
    if product_id in session['cart']:
        price = session['cart'][product_id]['price']
        session['cart'][product_id]['quantity'] = 0                
        session['cart'][product_id]['quantity'] += quantity
        session['cart'][product_id]['total_price'] = 0
        session['cart'][product_id]['total_price'] += price * quantity
        session.modified = True
        flash("Cart Updated Successfully!", 'success') 
    return jsonify({'message': 'Cart updated successfully'}), 200

@app.route('/deleting/', methods=['POST'])
def RemoveCart():
    try:
        product_id = request.form['product_id']
        print("Product ID to remove:", product_id)
        session['cart'].pop(product_id)
        flash("Item removed from cart", "success")
        return redirect(request.referrer or '/')
    except Exception as e:
        flash(f"Item was not from cart {e}", "danger")
        return redirect(request.referrer or '/')

@app.route('/Payment', methods=['POST','GET'])
def Payment():
    try:
        randnum = ""
        for i in range(3):
            randnum += str(randint(0, 9))

        if 'cart' not in session:
            return redirect(url_for('Cart'))
        if session['cart'] == {}:
            flash("Add Some Items To Your Cart")
            return redirect(url_for('Cart'))
    
        if 'cart' in session:        
            cart_items = session['cart']
            formatted_cart_items = []
        subtotal = 0    
        for product_id, product_details in cart_items.items():
        # Format the cart item as needed
            formatted_cart_items.append({
            'product_id': product_id,
            'details': product_details
            })
            subtotal += product_details['total_price']
        subtotal = "{:,.2f}".format(subtotal)
        order_details = {
            'name': request.form['fullname'],
            'address': request.form['address'],
            'zip': request.form['zip'],
            'country': request.form['country'],
            'city': request.form['city'],
            'email': request.form['email'],
            'state': request.form['state']
        }
        html = render_template('email.html', cart=formatted_cart_items, subtotal=subtotal, name=order_details['name'])

        # Send the email
        mailer("Order Confirmation/Reminder", html, order_details['email'])
        message_content = {"Name":order_details['name'], "email":order_details['email'], "cart_id":[id for id in session['cart'].keys()]}
        STT(message_content)

        return render_template('wallet.html', name=order_details['name'], address=order_details['address'], zip=order_details['zip'], country=order_details['country'], city=order_details['city'],state=order_details['state'],email=order_details['email'], cart=formatted_cart_items, subtotal=subtotal, Crypto_data = Crypto_data, randnum=randnum)
    except Exception as e:
        flash(f"An error occured while checking out{e}, try again or contact us")
        return redirect(url_for('Cart'))    

@app.route('/cart', methods=["POST", 'GET'])
def Cart():
    if 'cart' not in session:
        session['cart'] = {}
    if len(session['cart']) == 0:
        flash('No Item in cart')
        return render_template('emptycart.html')
    subtotal = 0    
    # Retrieve cart items from session
    if 'cart' in session:
        session.permanent = True
        cart_items = session['cart']
        formatted_cart_items = []
    for product_id, product_details in cart_items.items():
    # Format the cart item as needed
        formatted_cart_items.append({
        'product_id': product_id,
        'details': product_details
        })
        subtotal += product_details['total_price']
    subtotal = "{:,.2f}".format(subtotal)    
    
    return render_template('cart.html', cart=formatted_cart_items, subtotal=subtotal)
    

@app.route("/adding-to-cart", methods=["POST", 'GET'])    
def AddToCart():
    try:

        product_id = request.form['product-id']
        if product_id in product_data:
            quantity = int(request.form.get('quantity', 1))
            if 'cart' not in session:
                session['cart'] = {}
            if product_id in session['cart']:
                price = session['cart'][product_id]['price']                
                session['cart'][product_id]['quantity'] += quantity
                session['cart'][product_id]['total_price'] += price * quantity
                flash("Added To Cart Successfully!", 'success')
                return redirect(request.referrer or '/')    
            else:
                # Add new product to cart
                price = product_data[product_id]['Pprice']
                price = int(float(price.replace(',', '')))
                
                session['cart'][product_id] = {
                    'name': product_data[product_id]['Pname'],
                    'imgsrc': product_data[product_id]['imgsrc'],
                    'price': price,
                    'quantity': quantity,
                    'total_price': price * quantity
                }
                flash("Added To Cart Successfully!", 'success')
                return redirect(request.referrer or '/')        
        elif product_id not in product_data:
            flash('Invalid Product ID', "danger")
            return redirect(request.referrer or '/')  
    except Exception as e:
        flash(f"An Error occured \n {e}", 'danger')
        return redirect(request.referrer or '/')        

if __name__ == '__main__':
    app.run(port=4446)    