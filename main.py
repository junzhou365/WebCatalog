from flask import Flask, make_response, render_template, request, redirect, jsonify, url_for
app = Flask(__name__)

from catalogDB import Base, Category, Item 
from loginManager import LoginManager, User, SECRET
app.secret_key = SECRET

login_manager = LoginManager(app, '/catalog')

import logging

def render_page(*a, **kw):
    kw['user'] = login_manager.user
    return render_template(*a, **kw)

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('renderHomePage')

# Home Page
@app.route('/')
@app.route('/catalog/')
def renderHomePage():
    login_manager.initialize()
    categories = Category.get_all()
    return render_page('catalog.html', categories = categories)

# Show a category
@app.route('/catalog/category_<int:category_id>/', methods = ['GET'])
def showCategory(category_id):
    category = Category.filter_by_id(category_id)
    items = Item.get_all_by_category(category_id)
    return render_page('showCategory.html', category = category, items = items)


# Edit a new category
@app.route('/catalog/newCategory/', methods = ['GET', 'POST'])
@login_manager.login_required
def newCategory():
    if request.method == 'POST':
        Category.store(request.form['category_name'])
        return redirect(url_for('renderHomePage'))
    else:
        return render_page('updateCategory.html')

# Edit a category
@app.route('/catalog/category_<int:category_id>/editCategory/', methods = ['GET', 'POST'])
@login_manager.login_required
def editCategory(category_id):
    editingCategory = filter_by_id(category_id)
    if request.method == 'POST':
        if request.form['category_name']:
            editingCategory.name = request.form['category_name']
            return redirect(url_for('renderHomePage'))
    else:
        return render_page('updateCategory.html', category = editingCategory)

# Delete a category
@app.route('/catalog/category_<int:category_id>/deleteCategory', methods = ['GET', 'POST']) 
@login_manager.login_required
def deleteCategory(category_id):
    deleted_category_name = Category.filter_by_id(category_id).name
    if request.method == 'POST':
        Category.delete_by_id(category_id)
        return render_page('showCategory.html', deleted_category_name = deleted_category_name)
    else:
        pass
            
# Show an Item
@app.route('/catalog/category_<int:category_id>/item_<int:item_id>', methods = ['GET'])
def showItem(category_id, item_id):
    item = Item.filter_by_id(item_id)
    category = Category.filter_by_id(category_id)
    return render_page('showItem.html', item = item, category = category)

# Edit a new Item
@app.route('/catalog/category_<int:category_id>/newItem/', methods = ['GET', 'POST'])
@login_manager.login_required
def newItem(category_id):
    if request.method == 'POST':
        Item.store(request.form['item_title'], request.form['item_desc'], category_id)
        return redirect(url_for('renderHomePage'))
    else:
        return render_page('updateItem.html')

# Delete an item
@app.route('/catalog/category_<int:category_id>/item_<int:item_id>/deleteItem', methods = ['GET'])
@login_manager.login_required
def deleteItem(category_id, item_id):
    Item.delete_by_id(item_id)
    return redirect(url_for('showCategory/category_id'))

# Search
@app.route('/catalog/search', methods = ['GET'])
def search():
    q = request.args.get('q')
    category = Category.filter_by_name(q)
    item = Item.filter_by_title(q)
    return render_page('searchResult.html', category = category, item = item)

# Login
app.add_url_rule('/catalog/login/', 'login', login_manager.login, methods = ['GET', 'POST'])

# Signup
app.add_url_rule('/catalog/signup/', 'signup', login_manager.signup, methods = ['GET', 'POST'])

# Logout
app.add_url_rule('/catalog/logout/', 'logout', login_manager.logout, methods = ['GET'])




if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
