from flask import Flask 
from application.database import db

from flask_restful import Api
from application.resources import *

app = None 

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blogdata.sqlite3"
    db.init_app(app)

    app.secret_key = 'kkkuuuiii' 

    app.config['UPLOAD_FOLDER'] = 'static/images'

    app.app_context().push()

    api = Api(app)

    api.add_resource(HelloWorld, '/api/helloworld')
    api.add_resource(BlogAPI, '/api/blog', '/api/blog/<int:id>')

    return app

app = create_app()

from application.controllers import *
from application.models import *

if __name__ == "__main__":
    app.run()