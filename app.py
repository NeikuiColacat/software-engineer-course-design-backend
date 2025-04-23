from flask import Flask
from models.db import init_db
from routes import user, health, manage 

app = Flask(__name__)
init_db(app)

# 注册 Blueprint
app.register_blueprint(user.bp, url_prefix="/user")
app.register_blueprint(health.bp)
app.register_blueprint(manage.bp, url_prefix="/manage")

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
