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

SECRET = 'AK1747' # secret word used for hashing string
def hash_str(s):
    """hash string combining with secret word using hmac 
    Arg:
        s: A string.
    Return:
        hex digits 
    """
    return hmac.new(SECRET, s).hexdigest()

def make_salt():
    """generate random 5 letters long string"""
    return ''.join([random.choice(string.letters) for x in xrange(5)])

def make_hash_val(s):
    """make a pair of a string and its hashed value
    Arg:
        s: A string.
    Return:
        A string in the format of "string | hashed value of string"
    """
    y = "%s|%s" %(s, hash_str(s))
    return y

def check_hash_val(hashed_val):
    """
    Check if input is a valid pair of string and hashed string generated 
    according to our security rule

    Arg:
        hashed_val: In the format of "string | hashed string"
    Return:
        original val or None 
    """
    x = hashed_val.split('|')[0]
    # compare original pair and generated pair
    if hashed_val == make_hash_val(x): 
        return x

def make_password(name, pw, salt=None):
    """makde password

    Hash the combination of name, password and salt to generate hashed password.
    Avoid storing plain passwords.

    Args:
        name: username
        pw: password which user typed in
        salt: add something hard to break the password, 5-letter string
    Return:
        "x | salt", where 'x' is hashed string in hexadecimal digits.
    """
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" %(h, salt)

def set_cookie_val(val):
    """set cookie value, in the format of "s | hash(s)" """
    return make_hash_val(str(val))

def redirect_url():
    """redirect the url

    First try to redirect to the url in the 'next' request, then try previous 
    page, finally redirect to home page.
    """
    return request.args.get('next') or request.referrer or \
           url_for('renderHomePage')

class LoginManager:
    """Accounts System
    
    It wrapps important login, logout, and signup methods. It also contains some
    helper functions to verify password, name and email, and generate cookies. 

    After logging in, the page will redirect to previous page. 

    Attributes:
        path: The app's base url. Like "/catalog" 
        user: After successfully one logs in, it will create a user object
            retrieved from 'user' table. 
    """ 
    def __init__(self, path):
        self.path = path
        self.user = None

    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    def valid_username(self, username):
        """Username has at least 3 letters and at most 20 characters letters, 
        digits and underscore are allowed
        """
         return self.USER_RE.match(username)

    PASS_RE = re.compile(r"^.{3,20}$")
    def valid_password(self, password):
        """Password has at least 3 letters and at most 20 characters no limits
        on character
        """
         return self.PASS_RE.match(password)

    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    def valid_email(self, email):
        """Email address is regular email address"""
         return self.EMAIL_RE.match(email)

    def valid_pw(self, name, pw, h):
        """Check if the password is valid"""
        salt = h.split('|')[1]
        return h == make_password(name, pw, salt)

    def read_cookie(self, s):
        """First try to read cookie, then check if it is valid"""
        cookie_val = request.cookies.get(s)
        return cookie_val and check_hash_val(cookie_val)

    def login_set_cookie(self, user, response):
        """Set cookie after successfully log in
        Args:
            response: flask response object, used for setting cookie
            user: user object
        Return:
            response setting a cookie in the format like:
            "name=user_id; value=129381728937192;path=/catalog"
        """
        response.set_cookie('user_id', value=set_cookie_val(user.id), path='/catalog')

    def initialize(self):
        """Read cookie and retrieve user object"""
        uid = self.read_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))
        
    def get_valid_user(self, name, pw):
        """Check if name and pw are paired
        Return: 
            user object or None if no user or password is wrong 
        """
        u = User.get_by_name(name)
        if u and self.valid_pw(name, pw, u.pw_hash):
            return u

    def login_required(self, func):
        """decorator to decorate functions which require login"""
        @wraps(func)
        def login_checker(*a, **kw):
            ret = func(*a, **kw)
            if not self.user:
                return redirect(url_for('login'))
            return ret
        return login_checker

    def login(self, *a, **kw):
        """Login

        If the request method is 'POST',
        1. Verify user.
        2. Render error message if the user doesn't exist or wrong password.
        3. Set cookie, set self.user and return response to redirect to previous 
        page if valid user

        If the request method is 'GET',
        Render the page

        Args:
            No inputs
        Return:
            flask response 
        """
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            valid_login = False

            u = self.get_valid_user(username, password)

            if not u:
                return render_template('login.html', error_message = "Invalid Login") 
            else:
                # redirect_to_prev: page before direct to login page
                redirect_to_prev = redirect(request.form['next_url'])
                response = make_response(redirect_to_prev)
                self.login_set_cookie(u, response)
                self.user = u
                return response
        else:
            # remember the previous url using redirect_url()
            # usually the previous url is request.referrer
            next_url = redirect_url() 
            # write next_url into html to let "POST" get it
            return render_template('login.html', next_url = next_url)

    def signup(self):
        """Signup

        If the request method is 'POST',
        1. Verify username, password, password_verify and email.
        2. Create user if all above are correct.
        3. Render error messages if some of them are incorrect.
        4. Set cookie, set self.user, and redirect to home

        If the request method is 'GET',
        Render the signup page

        Args:
            No inputs
        Return:
            flask response 
        """
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
    """Logout

    Redirect to home, set the cookie null and set self.user None

    Return:
        flask response
    """
        redirect_to_home = redirect(url_for('renderHomePage'))
        response = make_response(redirect_to_home)
        response.set_cookie('user_id', value='', path='/catalog')
        self.user = None
        return response

# User
class User(Base):
    """User table
        
    It saves users' information. 
    Columns: Id, Name, Hashed Password, Email Address

    Methods are all classmethod because We don't need to instantiate user.
    There's only one user table.
    """
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
        """return newly stored user object"""
        newUser = User(name=name, pw_hash=make_password(name, pw), email=email)
        session.add(newUser)
        session.commit()
        return newUser
        

engine = create_engine('postgresql+psycopg2:///catalog')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
