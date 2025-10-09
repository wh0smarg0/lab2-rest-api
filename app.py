import os

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ----- Збереження даних у пам'яті -----
users = []
categories = []
records = []

# ---------- USERS ----------
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [u for u in users if u['id'] != user_id]
    return jsonify({'message': 'User deleted'})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    new_user = {
        'id': len(users) + 1,
        'name': data.get('name')
    }
    users.append(new_user)
    return jsonify(new_user), 201


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)


# ---------- CATEGORIES ----------
@app.route('/category', methods=['GET'])
def get_categories():
    return jsonify(categories)


@app.route('/category', methods=['POST'])
def create_category():
    data = request.json
    new_category = {
        'id': len(categories) + 1,
        'name': data.get('name')
    }
    categories.append(new_category)
    return jsonify(new_category), 201


@app.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    global categories
    # Знайти категорію
    category = next((c for c in categories if c['id'] == category_id), None)
    if category is None:
        return jsonify({'error': 'Category not found'}), 404

    # Видалити
    categories = [c for c in categories if c['id'] != category_id]

    return jsonify({'message': f"Category '{category['name']}' deleted"})


# ---------- RECORDS ----------
@app.route('/record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    record = next((r for r in records if r['id'] == record_id), None)
    if record:
        return jsonify(record)
    return jsonify({'error': 'Record not found'}), 404


@app.route('/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    global records
    records = [r for r in records if r['id'] != record_id]
    return jsonify({'message': 'Record deleted'})


@app.route('/record', methods=['POST'])
def create_record():
    data = request.json
    new_record = {
        'id': len(records) + 1,
        'user_id': data.get('user_id'),
        'category_id': data.get('category_id'),
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'amount': data.get('amount')
    }
    records.append(new_record)
    return jsonify(new_record), 201


@app.route('/record', methods=['GET'])
def get_records():
    user_id = request.args.get('user_id', type=int)
    category_id = request.args.get('category_id', type=int)

    if not user_id and not category_id:
        return jsonify({'error': 'You must provide user_id or category_id'}), 400

    filtered = records
    if user_id:
        filtered = [r for r in filtered if r['user_id'] == user_id]
    if category_id:
        filtered = [r for r in filtered if r['category_id'] == category_id]

    return jsonify(filtered)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render дає свій PORT
    app.run(host="0.0.0.0", port=port, debug=True)
