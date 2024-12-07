from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from redis.client import Redis
from flask_session import Session
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
sess = Session()


def create_app():
	app = Flask(__name__)
	CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
	# CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://172.19.32.1:3000", "http://192.168.100.46:3000/"]}})

	app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
	app.config['PAYSTACK_PUBLIC_KEY'] = os.environ.get('PAYSTACK_PUBLIC_KEY')
	app.config['PAYSTACK_SECRET_KEY'] = os.environ.get('PAYSTACK_SECRET_KEY')
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')  # Fixed Typo
	app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE')
	app.config['SESSION_REDIS'] = Redis(host='127.0.0.1', port=6379)

	

	db.init_app(app)
	sess.init_app(app)

	from .views import views
	from .auth import auth

	app.register_blueprint(views, url_prefix='/')
	app.register_blueprint(auth, url_prefix='/auth')

	from .models import Product, User, Cart, WishList, Orders

	with app.app_context():
	    db.create_all()
	    
	return app 