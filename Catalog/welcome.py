from flask import render_template
from Catalog import app

# Home Page
@app.route('/')
def welcome():
    return render_template('welcome.html')

