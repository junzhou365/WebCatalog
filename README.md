# Catalog App

This is a project of Udacity Fullstack Nano-degree. It's a web application that provides basic functionality for categorizing items. Storing other information of item such as image or description is supported.

The database used is PostgreSQL. SQLAlchemy is used to access and manage the database. 
Flask is the framework and Jinja2 is the template. It's written in python. In frontend, JavaScript is used to add some effects. Bootstrap makes CSS easier.

It's been deployed to AWS EC2 at [here](http://www.junzhou365.com/catalog).

### setup steps

1. git clone https://github.com/junzhou365/WebCatalog.git
2. cd WebCatalog
2. psql -f Catalog/database_setup.sql -- create database
3. python Catalog/database_init.py  -- add some test items and categories
4. python runserver.py   -- run the app at localhost:5000/catalog

### Structure

It consists of the following important files.

*catalogDB.py* defines different database tables as classes by SQLAlchemy and provides interfaces to interact with them. 

*database_init.py* initializes the database and puts in some default items.

*database_setup.sql* simply creates a database called catalog in postgresql.

*catalogViews.py* is the main body of the project. View functions of rendering the websites are defined here. 

*loginManager.py* defines login and registration system. The system consists of two parts.  User class interacts with User table. Login, Logout, and Signup view functions have been well defined.  Additionaly, it defines some security functions such as make_hash_val and make_password.

*runserver.py* is only used for running the application.
