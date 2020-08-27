from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restful import Api

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)

db = MongoEngine()
db.init_app(app)

from application import routes

api.add_resource(routes.GetPostAPI, '/api/')
api.add_resource(routes.GetUpdateDeleteAPI, '/api/<idx>/')
