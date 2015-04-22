from flask import Flask, render_template
app = Flask(__name__) 

from catalog import *

# Home Page
@app.route('/')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0')
