from flask import Flask
from models.db import mongo, init_db
from routes.user import bp as user_bp
from routes.manage import bp as manage_bp
from routes.health import bp as health_bp
from routes.hugging_face import bp as hf_bp

app = Flask(__name__)
init_db(app)

app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(manage_bp, url_prefix="/manage")
app.register_blueprint(health_bp , url_prefix="")
app.register_blueprint(hf_bp , url_prefix="")

if __name__ == "__main__":
    app.run('0.0.0.0',debug=True,port=5000)