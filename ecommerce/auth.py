from flask import Blueprint, request, jsonify, session
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/get_current_user', methods=['GET'])
def get_current_user():
	try:
		user_id = session['user_id']
		if not user_id:
			return jsonify({"message": "Unauthorized"}), 401
		user = db.session.get(User, user_id)
		if user:
			return jsonify(user.to_json()), 200

	except KeyError:
		return jsonify({"message": "User not found"}), 404


@auth.route('/get_users', methods=['GET'])
def get_users():
	users = User.query.all()
	json_users = [user.to_json() for user in users]
	user_email = [user['email'] for user in json_users] 
	return jsonify({"users": user_email})

@auth.route('/register', methods=['POST'])
def register():
	first_name = request.json.get("firstName")
	last_name = request.json.get("lastName")
	email = request.json.get("email")

	new_user = User(email=email.strip(), first_name=first_name.strip(), last_name=last_name.strip())
	new_user.set_password(request.json.get("password1"))

	db.session.add(new_user)
	db.session.commit()

	user = db.session.execute(db.select(User).filter_by(email=email)).scalar()

	session['user_id'] = user.id


	return jsonify({"message": "Account successfuly created"})
	


@auth.route('/login', methods=['POST'])
def login():
	email = request.json.get("email")
	user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
	if not user or not user.verify_password(request.json.get("password")):
		return jsonify({"message": "Invalid email or password."}), 401


	session['user_id'] = user.id
	return jsonify({"message": "Successfully logged in"}), 200

@auth.route('/edit-profile', methods=['POST'])
def edit_profile():
	user_id = session['user_id']
	if not user_id:
		return jsonify({"message": "Unauthorized"}), 401
		
	user = db.get_or_404(User, user_id)
	form = request.json

	if form:
		if bool(form.get('email')):
			user.email = form.get('email').strip()
		if bool(form.get('firstName')):
			user.first_name = form.get('firstName').strip()
		if bool(form.get('lastName')):
			user.last_name = form.get('lastName').strip()
		if bool(form.get('phone')):
			user.phone = form.get('phone').strip()
		if bool(form.get('address')):
			user.address = form.get('address').strip()
		if bool(form.get('address2')):
			user.address2 = form.get('address2').strip()
		if bool(form.get('city')):
			user.city = form.get('city').strip()
		if bool(form.get('country')):
			user.country = form.get('country')
		if bool(form.get('zipCode')):
			user.zip_code = form.get('zipCode').strip()

		db.session.commit()

		return jsonify({'message': 'User updated'}), 200

	return jsonify({'message': 'error while updating'}), 400



@auth.route('/logout', methods=['GET'])
def logout():
	session['user_id'] = None
	return jsonify({"message": "logged out"})
