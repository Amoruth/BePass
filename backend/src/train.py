from flask import request, jsonify
import os
import json
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

USER_FILE = "data/user_data.json"

def get_password(username):
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE, "r") as f:
        users = json.load(f)
    return users.get(username)

def train_user():
    data = request.get_json()
    username = data.get("username")
    typed_pw = data.get("typedPassword")
    features = data.get("features")

    if not username or not typed_pw or not features:
        return jsonify({"error": "参数不完整"}), 400

    password = get_password(username)
    if password != typed_pw:
        return jsonify({"error": "密码错误，不能训练"}), 403

    user_dir = f"data/{username}"
    os.makedirs(user_dir, exist_ok=True)
    sample_file = f"{user_dir}/samples.json"
    model_file = f"{user_dir}/model.pkl"

    # 加载已有样本
    samples = []
    if os.path.exists(sample_file):
        with open(sample_file, "r") as f:
            samples = json.load(f)

    # 添加新样本前需验证置信度是否高
    # 先尝试加载模型，如果存在就用模型判定新样本是否正常
    if os.path.exists(model_file) and samples:
        model = joblib.load(model_file)
        feat_np = np.array(features).reshape(1, -1)
        pred = model.predict(feat_np)[0]  # 1正常，-1异常
        score = model.score_samples(feat_np)[0]  # 分数越高越正常，未归一化

        # 简单归一化到0~1区间 (这里可能需要根据实际情况调整)
        # IsolationForest score_samples 越大越正常，取min-max归一化样本置信度
        scores_all = model.score_samples(np.array(samples))
        min_score, max_score = min(scores_all), max(scores_all)
        if max_score - min_score == 0:
            conf = 1.0
        else:
            conf = (score - min_score) / (max_score - min_score)

        if pred == -1 or conf < 0.8:
            return jsonify({"error": "样本置信度低，拒绝训练"}), 400

    samples.append(features)

    if len(samples) < 3:
        with open(sample_file, "w") as f:
            json.dump(samples, f)
        return jsonify({"message": f"已采集样本 {len(samples)}/3，继续输入相同口令"}), 200

    # 训练 IsolationForest 模型
    X = np.array(samples)
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    joblib.dump(model, model_file)

    with open(sample_file, "w") as f:
        json.dump(samples, f)

    return jsonify({"message": "模型训练成功"}), 200
