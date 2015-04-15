# Catalog App

This is a project of Udacity Fullstack Nano-degree. It's a web application that provides basic functionality for categorizing items. Other information of item such as image or description can be stored.

It uses SQLAlchemy to access and manage PostgreSQL database. Flask is the framework and Jinja2 is the template. It's written in python.

### setup steps:

1. psql -f database_setup.sql -- create database
2. python database_init.py  -- add some test items and categories
3. python main.py   -- run the app at localhost:5000/catalog

It consists of the following important files.

catalogDB.py defines tables as classes using SQLAlchemy and provides methods to interact with them.

database_init.py initializes the database and puts in some default items.

database_setup.sql creates database called catalog in postgresql.

main.py is the main body of the project. View functions of rendering the websites are defined here. 

loginManager.py defines login and registration system. The system consists of two parts. User class interacts with User table. Login, Logout, and Signup view functions have been well defined. 

