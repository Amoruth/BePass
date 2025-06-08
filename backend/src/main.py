from flask import Flask
from flask_cors import CORS
from register import register_user
from train import train_user
from verify import verify_user

app = Flask(__name__)
CORS(app)

app.add_url_rule('/register', view_func=register_user, methods=['POST'])
app.add_url_rule('/train', view_func=train_user, methods=['POST'])
app.add_url_rule('/verify', view_func=verify_user, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
