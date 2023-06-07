from flask import Flask
from app.main.errors import exception
from app.main.swagger_doc import blueprint1 as api
from app.main.views import crawled

app = Flask(__name__)
# app.register_blueprint(exception, url_prefix='/error')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(crawled, url_prefix='/crawled')
