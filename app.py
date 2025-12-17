import os
from flask import Flask, request
from flask_smorest import Api, abort
from flask_migrate import Migrate
from db import db
import models  # Обов'язково імпортуємо моделі для роботи міграцій

# Імпортуємо схеми для валідації
from schemas import UserSchema, CategorySchema, RecordSchema


def create_app():
    app = Flask(__name__)

    # Завантаження конфігурації з файлу config.py
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    # ---------- USERS ----------
    @app.route('/user', methods=['POST'])
    def create_user():
        user_data = UserSchema().load(request.json)
        user = models.UserModel(**user_data)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(400, message="User with this name already exists.")
        return UserSchema().dump(user), 201

    @app.route('/user/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        user = models.UserModel.query.get_or_404(user_id)
        return UserSchema().dump(user)

    # ---------- CATEGORIES (Variant 2) ----------
    @app.route('/category', methods=['POST'])
    def create_category():
        category_data = CategorySchema().load(request.json)
        # Якщо user_id не передано, категорія автоматично стане загальною (null в БД)
        category = models.CategoryModel(**category_data)
        try:
            db.session.add(category)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(500, message="An error occurred while creating the category.")
        return CategorySchema().dump(category), 201

    @app.route('/category', methods=['GET'])
    def get_categories():
        user_id = request.args.get('user_id', type=int)

        # ЛОГІКА ВАРІАНТУ №2:
        # Показуємо категорії, де user_id порожній (загальні)
        # АБО де user_id збігається з ID користувача (приватні)
        if user_id:
            categories = models.CategoryModel.query.filter(
                (models.CategoryModel.user_id == None) |
                (models.CategoryModel.user_id == user_id)
            ).all()
        else:
            # Якщо user_id не вказано — тільки загальні
            categories = models.CategoryModel.query.filter_by(user_id=None).all()

        return CategorySchema(many=True).dump(categories)

    # ---------- RECORDS ----------
    @app.route('/record', methods=['POST'])
    def create_record():
        record_data = RecordSchema().load(request.json)
        record = models.RecordModel(**record_data)
        try:
            db.session.add(record)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(400, message="Check if user_id and category_id exist.")
        return RecordSchema().dump(record), 201

    @app.route('/record/<int:record_id>', methods=['GET'])
    def get_record(record_id):
        record = models.RecordModel.query.get_or_404(record_id)
        return RecordSchema().dump(record)

    @app.route('/record', methods=['GET'])
    def get_records():
        user_id = request.args.get('user_id', type=int)
        category_id = request.args.get('category_id', type=int)

        query = models.RecordModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.filter_by(category_id=category_id)

        return RecordSchema(many=True).dump(query.all())

    # ---------- DELETE ----------
    @app.route('/user/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        user = models.UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000)