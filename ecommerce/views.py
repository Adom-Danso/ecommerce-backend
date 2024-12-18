from flask import Blueprint, request, jsonify, session, current_app as app
from . import db
from .models import Product, Cart, WishList, Orders, User
from sqlalchemy import and_
import json, requests


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "Backend is up and running!"

@views.route('/get_products', methods=['GET'])
def get_products():
	products = Product.query.all()
	products = [product.to_json() for product in products]

	return jsonify({"products": products})

@views.route('/cart', methods=['GET'])
def cart():
	user_id = session['user_id']
	items = db.session.execute(db.select(Cart).filter_by(user_id=user_id)).scalars()
	products = [{'id': item.product_id, 'quantity': item.quantity} for item in items]
	product_ids = [product['id'] for product in products]  # Extract all product IDs
	fetched_products = (
	    db.session.execute(
	        db.select(Product).filter(Product.id.in_(product_ids)).order_by(Product.timestamp.desc())
	    ).scalars().all()
	)

	# Create a list of products with their quantities
	cart_products = [
	    {
	        'product': product.to_json(),  # The Product object
	        'quantity': next((p['quantity'] for p in products if p['id'] == product.id), 0)
	    }
	    for product in fetched_products
	]

	no_of_items_in_cart = len(cart_products)
	total_price = 0
	if cart_products:
		for item in cart_products:
			total_price += int(item['product']['price'])

	return jsonify({
		'products': cart_products, 
		'totalPrice': total_price,
		'cartNumber': no_of_items_in_cart
	})

@views.route('/add-to-cart/<int:id>', methods=['POST'])
def add_to_cart(id):
	user_id = session['user_id']
	product = db.session.execute(db.select(Cart).filter(and_(Cart.user_id == user_id, Cart.product_id == id))).scalars().first()
	if product is None:
		new_item = Cart(product_id=id, user_id=user_id, quantity=request.json.get('quantity'))
		db.session.add(new_item)
		db.session.commit()

	return jsonify({'message': 'succesfully added to cart'})

@views.route('/empty-cart-items', methods=['DELETE'])
def empty_cart():
	user_id = session['user_id']

	cart_items = db.session.execute(db.select(Cart).filter_by(user_id=user_id)).scalars()
	if cart_items:
		for item in cart_items: 
			db.session.delete(item)
	db.session.commit()
	return jsonify({'message': 'Cart items have been deleted'})

@views.route('/delete-cart-item/<int:id>', methods=['DELETE'])
def remove_from_cart(id):
	user_id = session['user_id']
	cart_item = db.session.execute(db.select(Cart).filter(and_(Cart.user_id == user_id, Cart.product_id == id))).scalars().first()
	if cart_item is not None:
		db.session.delete(cart_item)
		db.session.commit()

	return jsonify({'message': 'succesfully removed from cart'})


@views.route('/wish-list', methods=['GET'])
def wishlist():
	user_id = session['user_id']
	products = db.session.execute(db.select(WishList).filter_by(user_id=user_id)).scalars()
	product_ids = [product.product_id for product in products]
	wishlist_items = list(db.session.execute(db.select(Product).filter(Product.id.in_(product_ids))).scalars())
	wishlist_products = [product.to_json() for product in wishlist_items]

	return jsonify(wishlist_products)

@views.route('/add-or-remove-from-wishlist/<int:product_id>', methods=['POST'])
def add_or_remove_from_wishlist(product_id):
	user_id = session['user_id']
	item =  db.session.execute(db.select(WishList).filter(and_(WishList.user_id == user_id, WishList.product_id == product_id))).scalars().first()
	if item is not None:
		db.session.delete(item)
		db.session.commit()
		message = "Removed from wishlist"
	elif item is None:
		new_item = WishList(product_id=product_id, user_id=user_id)
		db.session.add(new_item)
		db.session.commit()
		message = 'Added to wishlist'
		
	return jsonify({'message': message})


@views.route('/orders', methods=['GET'])
def orders():
	user_id = session['user_id']
	orders = list(db.session.execute(db.select(Orders).filter(Orders.user_id == user_id).order_by(Orders.timestamp.desc())).scalars())
	summary = [order.to_json() for order in orders]
	# for order in orders:
	# 	# order_data_dict = json.loads(order.order_items)
	# 	summary.append({
	# 		'order': order.to_json(),
	# 		# 'summary_data': order_data_dict.items()
	# 		})

	return jsonify(summary)


@views.route('/submit_ref_data', methods=['POST'])
def submit_ref_data():
	data = request.json
	pay_ref = data.get('ref')

	if not pay_ref:
		return jsonify({'error': 'No reference provided'}), 400

	# Store the reference in the session
	session['pay_ref'] = pay_ref
	pay_ref = session['pay_ref']

	return jsonify({'message': 'Reference received successfully'})


@views.route('/place-order', methods=['POST'])
def place_order():
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    form = request.json
    paymentAddress = form.get('paymentAddress')
    pay_ref = form.get('paystackReference')  # Get payment reference

    if not pay_ref:
        return jsonify({"message": "Payment reference missing. Please try again."}), 400

    # Verify payment with Paystack
    headers = {
        'Authorization': f"Bearer {app.config['PAYSTACK_SECRET_KEY']}",
        'Content-Type': 'application/json',
    }
    response = requests.get(
        f'https://api.paystack.co/transaction/verify/{pay_ref}',
        headers=headers,
        timeout=30
    )
    if response.status_code != 200:
        return jsonify({'message': 'Payment verification failed due to network error.'}), 500

    response_data = response.json()
    if not response_data.get('status') or response_data['data']['status'] != 'success':
        return jsonify({'message': 'Payment verification failed. Please try again.'})

    # Fetch cart items and calculate total price on the server
    cart_items = list(db.session.execute(db.select(Cart).filter(Cart.user_id == user_id)).scalars())
    product_ids = [item.product_id for item in cart_items]
    cart_products = list(db.session.execute(db.select(Product).filter(Product.id.in_(product_ids))).scalars())

    server_total_price = 0
    order_items = {}
    for item in cart_products:
        quantity = next((cart_item.quantity for cart_item in cart_items if cart_item.product_id == item.id), 1)
        item_total = item.price * quantity
        server_total_price += item_total
        order_items[item.name] = {"price": item.price, "quantity": quantity}

    # Compare server-calculated total with Paystack amount
    paystack_amount = response_data['data']['amount'] / 100  # Convert to base currency (e.g., Naira)
    if server_total_price != paystack_amount:
        return jsonify({'message': 'Payment amount mismatch. Please try again.'}), 400

    # Format delivery details
    delivery_details = paymentAddress.get('address') + ', ' + paymentAddress.get('city') + ', ' + paymentAddress.get('country')
    if bool(paymentAddress.get('address2')):
        delivery_details = f"{paymentAddress['address2']}, {delivery_details}"

    # Create and save the order
    new_order = Orders(
        user_id=user.id,
        username=f'{user.first_name} {user.last_name}',
        order_items=json.dumps(order_items),
        delivery_details=delivery_details,
        total_price=server_total_price
    )
    new_order.generate_order_name(user_id)

    db.session.add(new_order)

    # Remove cart items
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()
    return jsonify({'message': 'Order has been placed'}), 201
