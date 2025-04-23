from flask_pymongo import PyMongo
mongo = PyMongo()

def init_db(app):
    from config import MONGO_URI, DB_NAME
    app.config["MONGO_URI"] = f"{MONGO_URI}/{DB_NAME}"
    mongo.init_app(app)
