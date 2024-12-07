from . import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import uuid, json

def get_uuid():
	return uuid.uuid4().hex

#=============User table==================
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, unique=True)
	first_name = db.Column(db.String(120), nullable=False)
	last_name = db.Column(db.String(120), nullable=False)
	email = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.String(120), nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	cart = db.relationship('Cart', backref='user', lazy=True)
	wish_list = db.relationship('WishList', backref='user', lazy=True)
	orders = db.relationship('Orders', backref='user', lazy=True)
	role = db.Column(db.String(50), nullable=False, default='normal')
	phone = db.Column(db.String(120), nullable=True)
	address = db.Column(db.String(120), nullable=True)
	address2 = db.Column(db.String(120), nullable=True)
	city = db.Column(db.String(120), nullable=True)
	zip_code = db.Column(db.String(120), nullable=True)
	country = db.Column(db.String(120), nullable=True)

	def to_json(self):
		return {
			"id": self.id,
			"firstName": self.first_name,
			"lastName": self.last_name,
			"phone": self.phone,
			"email": self.email,
			"timestamp": self.timestamp,
			"address": self.address,
			"address2": self.address2,
			"city": self.city,
			"zipCode": self.zip_code,
			"country": self.country,
		}


	def __repr__(self):
		return '<User %r>' % self.first_name

	#===========User method for converting the user password in to a hash password===========
	def set_password(self, password):
		hash_password = generate_password_hash(password)
		self.password = hash_password

	#===========Verifying password typed by user when logging in by comparing it to the already stored password===========
	def verify_password(self, password):
		return check_password_hash(self.password, password)

#=============Product table==================
class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	description = db.Column(db.String(50), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	food_and_Grocery = db.Column(db.Boolean, nullable=False)
	mobilePhones_and_Tablets = db.Column(db.Boolean, nullable=False)
	electronics = db.Column(db.Boolean, nullable=False)
	sports = db.Column(db.Boolean, nullable=False)
	home_Furniture_and_Appliances = db.Column(db.Boolean, nullable=False)
	fashion = db.Column(db.Boolean, nullable=False)
	health_and_Beauty = db.Column(db.Boolean, nullable=False)
	toys = db.Column(db.Boolean, nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	image_name = db.Column(db.String(), nullable=False)

	def to_json(self):
		return {
			"id": self.id,
			"name": self.name,
			"description": self.description,
			"price": self.price,
			"food_and_Grocery": self.food_and_Grocery,
			"mobilePhones_and_Tablets": self.mobilePhones_and_Tablets,
			"electronics": self.electronics,
			"sports": self.sports,
			"home_Furniture_and_Appliances": self.home_Furniture_and_Appliances,
			"fashion": self.fashion,
			"health_and_Beauty": self.health_and_Beauty,
			"toys": self.toys,
			"timestamp": self.timestamp,
			"image_name": self.image_name,
		}


#=============Cart table==================
class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) 
	quantity = db.Column(db.Integer, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	def to_json(self):
		return {
			"id": self.id,
			"product_id": self.product_id,
			"quantity": self.quantity,
			"user_id": self.user_id,
			"timestamp": self.timestamp
		}


#=============Wishlist table==================
class WishList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	def to_json(self):
		return {
			"id": self.id,
			"product_id": self.product_id,
			"user_id": self.user_id,
			"timestamp": self.timestamp
		}


#=============Orders table==================
class Orders(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	username = db.Column(db.String(50), nullable=False)
	order_name = db.Column(db.String(50), nullable=False)
	order_items = db.Column(db.String(200), nullable=False)
	status = db.Column(db.String(50), nullable=False, default='pending')
	delivery_details = db.Column(db.String(50), nullable=False)
	total_price = db.Column(db.Integer, nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	#==============Method for generating unique order names==================
	def generate_order_name(self, user_id):
		self.order_name = f"ORDER-{user_id}{uuid.uuid4().hex[:10].upper()}"

	def to_json(self):
		return {
			"id": self.id,
			"userId": self.user_id,
			"username": self.username,
			"orderName": self.order_name,
			"orderItems": json.loads(self.order_items),
			"status": self.status,
			"deliveryDetails": self.delivery_details,
			"totalPrice": self.total_price,
			"timestamp": self.timestamp
		}
