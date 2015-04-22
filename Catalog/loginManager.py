import re
import hashlib
import hmac
import random
import string
import logging

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

from flask import flash, make_response, render_template, request, redirect, jsonify, url_for
from functools import wraps

SECRET = 'AK1747'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_salt():
    return ''.join([random.choice(string.letters) for x in xrange(5)])


def make_hash_val(s):
    y = "%s|%s" %(s, hash_str(s))
    return y

def check_hash_val(hashed_val):
    x = hashed_val.split('|')[0]
    if hashed_val == make_hash_val(x):
        return x

def make_password(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" %(h, salt)

def set_cookie_val(val):
    return make_hash_val(str(val))

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('renderHomePage')

# Accounts System 
class LoginManager:

    def __init__(self, path):
        self.path = path
        self.user = None

    # username has at least 3 letters and at most 20 characters
    # Letters, digits and underscore are allowed
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    def valid_username(self, username):
         return self.USER_RE.match(username)

    # password has at least 3 letters and at most 20 characters
    # No limits on character
    PASS_RE = re.compile(r"^.{3,20}$")
    def valid_password(self, password):
         return self.PASS_RE.match(password)

    # email address is regular email address
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    def valid_email(self, email):
         return self.EMAIL_RE.match(email)

    # cookie has the form
#    COOKIE_RE = re.compile(r'.+=;\s*Path=/catalog')
#    def valid_cookie(self, cookie):
#        return cookie and self.COOKIE_RE.match(cookie)

    def valid_pw(self, name, pw, h):
        salt = h.split('|')[1]
        return h == make_password(name, pw, salt)

    def read_cookie(self, name):
        cookie_val = request.cookies.get(name)
        return cookie_val and check_hash_val(cookie_val)

    def login_set_cookie(self, user, response):
        response.set_cookie('user_id', value=set_cookie_val(user.id), path='/catalog')

    def initialize(self):
        uid = self.read_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))
        
    def get_valid_user(self, name, pw):
        u = User.get_by_name(name)
        if u and self.valid_pw(name, pw, u.pw_hash):
            return u

    def login_required(self, func):
        @wraps(func)
        def login_checker(*a, **kw):
            ret = func(*a, **kw)
            if not self.user:
                return redirect(url_for('login'))
            return ret
        return login_checker

    # login
    def login(self, *a, **kw):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            valid_login = False

            u = self.get_valid_user(username, password)

            if not u:
                return render_template('login.html', error_message = "Invalid Login") 
            else:
                #flash("You were logged in")
                #redirect_to_home = redirect(url_for('renderHomePage'))
                redirect_to_prev = redirect(request.form['next_url'])
                response = make_response(redirect_to_prev)
                self.login_set_cookie(u, response)
                self.user = u
                return response
        else:
            next_url = redirect_url()
            return render_template('login.html', next_url = next_url)


    # signup
    def signup(self):
        if request.method == 'POST':
            has_fault = False
            username = request.form.get('username')
            password = request.form.get('password')
            verify = request.form.get('verify')
            email = request.form.get('email')

            u = User.get_by_name(username)
            if u:
                return render_template('signup.html', error_username="User already exists.")

            params = dict(username = username, email = email)

            if not self.valid_username(username):
                params['error_username'] = "Invalid Username"
                has_fault = True

            if not self.valid_password(password):
                params['error_password'] = "Invalid Password"
                has_fault = True
            elif verify != password:
                params['error_verify'] = "Passwords Mismatch"
                has_fault = True

            if email and not self.valid_email(email):
                params['error_email'] = "Invalid email"
                has_fault = True

            if has_fault:
                return render_template("signup.html", **params)
            else:
                u = User.store(username, password, email)
                redirect_to_home = redirect(url_for('renderHomePage'))
                response = make_response(redirect_to_home)
                self.login_set_cookie(u, response)
                self.user = u
                return response
        else:
            return render_template('signup.html')

    # logout
    def logout(self):
        redirect_to_home = redirect(url_for('renderHomePage'))
        response = make_response(redirect_to_home)
        response.set_cookie('user_id', value='', path='/catalog')
        self.user = None
        return response

# User
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    pw_hash = Column(String(250), nullable=False)
    email = Column(String(250))

    @classmethod
    def get_by_name(cls, name):
        return session.query(User).filter_by(name = name).first()

    @classmethod
    def get_by_id(cls, uid):
        return session.query(User).filter_by(id = uid).first()

    @classmethod
    def store(cls, name, pw, email):
        newUser = User(name=name, pw_hash=make_password(name, pw), email=email)
        session.add(newUser)
        session.commit()
        return newUser
        

engine = create_engine('postgresql+psycopg2:///catalog')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
