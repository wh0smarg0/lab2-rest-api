import os
from flask import Flask, request, jsonify
from flask_smorest import Api, abort
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256

from db import db
import models
from schemas import UserSchema, CategorySchema, RecordSchema

def create_app():
    app = Flask(__name__)

    # --- Налаштування додатку ---
    app.config.from_pyfile('config.py', silent=True)

    # Жорстко прописуємо ключ, щоб уникнути помилок підпису
    app.config["JWT_SECRET_KEY"] = "277429514895990073851732729762754298193"
    app.config["JWT_ERROR_MESSAGE_KEY"] = "message"

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)
    jwt = JWTManager(app)

    # --- Обробники помилок JWT (згідно з методичкою) ---
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "message": "Request does not contain an access token.",
            "error": "authorization_required"
        }), 401

    # ---------- AUTH (Реєстрація та Логін) ----------

    @app.route('/register', methods=['POST'])
    def register():
        user_data = UserSchema().load(request.json)
        # Хешування пароля
        user = models.UserModel(
            name=user_data["name"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(400, message="User with this name already exists.")
        return {"message": "User created successfully."}, 201

    @app.route('/login', methods=['POST'])
    def login():
        user_data = UserSchema().load(request.json)
        user = models.UserModel.query.filter_by(name=user_data["name"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # Створюємо токен, де identity — це ID користувача
            access_token = create_access_token(identity=str(user.id))
            return {"access_token": access_token}, 200

        abort(401, message="Invalid credentials.")

    # ---------- CATEGORIES (Захищені) ----------

    @app.route('/category', methods=['POST'])
    @jwt_required()
    def create_category():
        category_data = CategorySchema().load(request.json)
        category = models.CategoryModel(**category_data)
        try:
            db.session.add(category)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(500, message="An error occurred while creating the category.")
        return CategorySchema().dump(category), 201

    @app.route('/category', methods=['GET'])
    @jwt_required()
    def get_categories():
        user_id = request.args.get('user_id', type=int)
        # Логіка Варіанту №2: бачимо загальні (None) + свої (user_id)
        if user_id:
            categories = models.CategoryModel.query.filter(
                (models.CategoryModel.user_id == None) |
                (models.CategoryModel.user_id == user_id)
            ).all()
        else:
            categories = models.CategoryModel.query.filter_by(user_id=None).all()
        return CategorySchema(many=True).dump(categories)

    # ---------- RECORDS (Захищені) ----------

    @app.route('/record', methods=['POST'])
    @jwt_required()
    def create_record():
        record_data = RecordSchema().load(request.json)
        record = models.RecordModel(**record_data)
        try:
            db.session.add(record)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(400, message="Error creating record. Check user and category IDs.")
        return RecordSchema().dump(record), 201

    @app.route('/record', methods=['GET'])
    @jwt_required()
    def get_records():
        user_id = request.args.get('user_id', type=int)
        category_id = request.args.get('category_id', type=int)
        query = models.RecordModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.filter_by(category_id=category_id)
        return RecordSchema(many=True).dump(query.all())

    # ---------- USERS (Захищені) ----------

    @app.route('/user/<int:user_id>', methods=['GET'])
    @jwt_required()
    def get_user(user_id):
        user = models.UserModel.query.get_or_404(user_id)
        return UserSchema().dump(user)

    @app.route('/user/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    def delete_user(user_id):
        user = models.UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)