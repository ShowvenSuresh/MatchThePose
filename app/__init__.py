import os 
from flask import Flask, app, render_template


app = Flask(__name__)

@app.route('/')
def page1():
    return render_template('page1.html')


@app.route('/game')
def page2():
    return render_template('page2.html')



