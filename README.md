# 行为口令

行为口令是基于行为特征的密码验证系统，通过结合用户的打字节律与口令内容进行身份验证，提升传统密码系统的安全性。

本项目使用 Flask 构建后端，利用使用 `IsolationForest` 实现仅依赖正样本的异常检测。



## 使用说明

- 本项目支持用户注册 / 登录 / 行为训练 / 验证
- 每个用户本地缓存样本 ≥3 才会训练模型，验证通过的正向样本也会被纳入增量学习
- 验证时会优先验证密码是否正确，再验证打字节律是否符合（置信度 > 0.6）
- 成功后模型保存为 `{username}_model.pkl`

本项目为一web应用，运行在 `http://localhost:8000` 



### 注册

用户需先注册一个账号，后端为持久化保存账号密码（以明文形式保存在 `backend/data/user_data.json` 文件中）

![](/home/amoruth/courses/syss/密码学导论/hw/submitted/register.png)

### 训练

然后需要录入至少3个正样本进行模型的初始化训练（建议初始化的几次行为口令不要差距过大，本项目直接接受所有初始化口令，如果相差过大会导致初始化得到的模型太差）

![](/home/amoruth/courses/syss/密码学导论/hw/submitted/train_1.png)

![](/home/amoruth/courses/syss/密码学导论/hw/submitted/train_3.png)

模型训练好之后会持久化保存在后端。本项目训练模型采用的是 `IsolationForest`，只训练正样本特征。同时使用了增量样本学习，即在初始化训练模型之后，可以继续附加训练样本或验证通过的样本也会自动被添加（需置信度 >90%）



### 验证

首先会验证密码是否正确。若密码错误，会直接回显“验证失败，置信度：0%”

![](/home/amoruth/courses/syss/密码学导论/hw/submitted/verify_false.png)

若密码正确，则会进一步验证输入密码的速率，即“行为”的验证。若该次行为口令经过模型计算出置信度 > 60%，则认为通过验证

![](/home/amoruth/courses/syss/密码学导论/hw/submitted/verify_success.png)
