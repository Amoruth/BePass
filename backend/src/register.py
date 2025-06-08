from flask import request, jsonify
import json
import os

USER_FILE = "data/user_data.json"

def load_users():
    if not os.path.exists(USER_FILE) or os.path.getsize(USER_FILE) == 0:
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "用户名或密码不能为空"}), 400

    users = load_users()
    if username in users:
        return jsonify({"error": "用户已存在"}), 409

    users[username] = password
    save_users(users)
    os.makedirs(f"data/{username}", exist_ok=True)
    return jsonify({"message": "注册成功"}), 200
