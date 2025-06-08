// frontend/script.js

function getFeatures() {
  const now = performance.now();
  // 简化特征，真实可换成更复杂的击键行为
  return [Math.random(), Math.random(), now % 1000];
}

function getPayload() {
  return {
    username: document.getElementById("username").value,
    typedPassword: document.getElementById("password").value,
    features: getFeatures()
  };
}

function post(url, data) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  }).then(res => res.json());
}

function updateStatus(text) {
  document.getElementById("status").innerText = text;
}

function register() {
  const data = {
    username: document.getElementById("username").value,
    password: document.getElementById("password").value
  };
  post("http://localhost:5000/register", data)
    .then(res => updateStatus(res.message || res.error))
    .catch(err => updateStatus("请求失败: " + err));
}

function train() {
  const data = getPayload();
  post("http://localhost:5000/train", data)
    .then(res => updateStatus(res.message || res.error))
    .catch(err => updateStatus("请求失败: " + err));
}

function verify() {
  const data = getPayload();
  post("http://localhost:5000/verify", data)
    .then(res => {
      if (res.verified) {
        updateStatus("验证成功，置信度：" + res.confidence + "%");
      } else {
        updateStatus("验证失败，置信度：" + res.confidence + "%");
      }
    })
    .catch(err => updateStatus("请求失败: " + err));
}
