from flask import Blueprint, request, jsonify, session, current_app as app
from .models import Product, Orders, User

admin = Blueprint('admin', __name__)

@admin.route('/get-database', methods=['GET'])
def get_database():
	users = User.query.all()
	orders = Orders.query.all()
	products = Product.query.all()

	user_list = [user.to_json() for user in users]
	orders_list = [order.to_json() for order in orders]
	products_list = [product.to_json() for product in products]

	return jsonify({
		"users": user_list,
		"orders": orders_list,
		"products": products_list,
	})

@admin.route('/get-users', methods=['GET'])
def get_users():
	users = User.query.all()

	user_list = [user.to_json() for user in users]
	
	return jsonify(user_list)


@admin.route('/get-products', methods=['GET'])
def get_products():
	products = Product.query.all()

	products_list = [product.to_json() for product in products]
	
	return jsonify(products_list)

@admin.route('/get-orders', methods=['GET'])
def get_orders():
	orders = Orders.query.all()

	orders_list = [order.to_json() for order in orders]
	
	return jsonify(orders_list)