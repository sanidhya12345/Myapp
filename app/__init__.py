from flask import Flask,g
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from  flask_mail import Mail
from .config import Config
db=MySQL()
mail=Mail()
app=Flask(__name__)
def create_app():
    app.config.from_object(Config)
    db.init_app(app)
    mail.init_app(app)
    from . import routes
    app.register_blueprint(routes.bp)
    return app

