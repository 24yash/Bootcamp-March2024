from flask import Flask, render_template, redirect 
from .models import *

from flask import current_app as app

@app.route('/')
def hello_world():
    a = "string"
    blogs = Blog.query.all()
    return render_template('index.html', a=a, blogs=blogs)

@app.route('/login')
def login():
    return render_template('login.html')