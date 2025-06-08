from flask import request, jsonify
import os
import json
import numpy as np
import joblib
from train import get_password

def verify_user():
    data = request.get_json()
    username = data.get("username")
    typed_pw = data.get("typedPassword")
    features = data.get("features")

    if not username or not typed_pw or not features:
        return jsonify({"error": "参数不完整"}), 400

    password = get_password(username)
    if not password:
        return jsonify({"error": "用户不存在"}), 404

    if typed_pw != password:
        return jsonify({"message": "密码错误", "verified": False, "confidence": 0}), 200

    model_path = f"data/{username}/model.pkl"
    sample_file = f"data/{username}/samples.json"

    if not os.path.exists(model_path) or not os.path.exists(sample_file):
        return jsonify({"error": "模型尚未训练"}), 400

    model = joblib.load(model_path)
    features_np = np.array(features).reshape(1, -1)

    # predict 返回 1 正常，-1 异常
    pred = model.predict(features_np)[0]

    # 计算置信度：用score_samples并归一化
    samples = []
    with open(sample_file, "r") as f:
        samples = json.load(f)

    samples_np = np.array(samples)
    scores_samples = model.score_samples(samples_np)
    score = model.score_samples(features_np)[0]

    min_score, max_score = min(scores_samples), max(scores_samples)
    if max_score - min_score == 0:
        conf = 1.0
    else:
        conf = (score - min_score) / (max_score - min_score)

    if pred == -1 or conf < 0.6:
        return jsonify({
            "message": "行为特征不一致",
            "verified": False,
            "confidence": round(conf * 100, 2)
        }), 200

    # 只有当置信度很高才加入增量样本
    if conf >= 0.9:
        samples.append(features_np[0].tolist())
        # 限制样本数量，保留最近50个样本
        samples = samples[-50:]
        with open(sample_file, "w") as f:
            json.dump(samples, f)

        X = np.array(samples)
        from sklearn.ensemble import IsolationForest
        new_model = IsolationForest(contamination=0.1, random_state=42)
        new_model.fit(X)
        joblib.dump(new_model, model_path)

    return jsonify({
        "message": "验证成功",
        "verified": True,
        "confidence": round(conf * 100, 2)
    }), 200
