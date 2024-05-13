from flask import Flask, render_template, redirect, url_for, send_from_directory, render_template_string, request, session, flash
from pathlib import Path
from datetime import timedelta
import time
import json


app = Flask(__name__)
app.secret_key = "b010de0b733688f73a8ea76120afe85615b988249ebd057cca7eeedd358d3c05"
app.permanent_session_lifetime = timedelta(days=5)

with open('products.json', 'r') as file:
        data = json.load(file)
product_data = data[0]


@app.route('/', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
@app.route('/index', methods=["POST", "GET"])
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
    bot_chat_id = "1952892389"    
    message = "\n".join([f"{key}:{value}" for key, value in message_content.items()])
    files = []
    url = 'https://api.telegram.org/bot6960033187:AAGEurWvnfuoXuHEivkDzKB3nF7SP5XnHPY/SendMessage'
    data = {'chat_id': bot_chat_id, 'text': message}
    response = requests.post(url, files=files, data=data)

@app.route('/sending', methods=["POST", "GET"])
def Contactus():
    try:
        if request.method == "POST":            
            STT(message_content)
            flash('Thanks For Your Feedback We Will Get Back To You', 'success')
            return redirect(url_for('Home'))
        flash('Sorry Check Your Input', 'danger')
        return render_template("index.html", contactusform=contactusform, form=form)
    except Exception as e:
        flash(f'an error occured Try again \n hint: {e}', 'danger')
        return render_template('index.html', contactusform=contactusform, form=form)       
    return redirect(url_for('Home'))

@app.route('/done')
def Done():
    session.pop('cart', None)
    return redirect(url_for('Home'))
    
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
        'email': request.form['email']
    }
    return render_template('wallet.html', name=order_details['name'], address=order_details['address'], zip=order_details['zip'], country=order_details['country'], city=order_details['city'], cart=formatted_cart_items, subtotal=subtotal)  

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
    app.run(debug=False, port=4444)    