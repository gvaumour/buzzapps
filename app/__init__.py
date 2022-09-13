from flask import Flask
import os


app = Flask(__name__)


from app import views
from app import models

