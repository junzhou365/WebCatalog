from flask import render_template
from Catalog import app

@app.route('/')
def welcome():
    return render_template('welcome.html')

