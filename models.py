from db import db

class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    # Зв'язок з категоріями та записами
    password = db.Column(db.String(256), nullable=False)
    categories = db.relationship("CategoryModel", back_populates="user", lazy="dynamic")
    records = db.relationship("RecordModel", back_populates="user", lazy="dynamic")


class CategoryModel(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=False, nullable=False)
    # nullable=True дозволяє створювати ЗАГАЛЬНІ категорії
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    user = db.relationship("UserModel", back_populates="categories")
    records = db.relationship("RecordModel", back_populates="category", lazy="dynamic")


class RecordModel(db.Model):
    __tablename__ = "record"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    sum = db.Column(db.Float(precision=2), nullable=False)

    user = db.relationship("UserModel", back_populates="records")
    category = db.relationship("CategoryModel", back_populates="records")