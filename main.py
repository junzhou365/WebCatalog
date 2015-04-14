from flask import Flask, make_response, render_template, request, redirect, jsonify, url_for, send_from_directory
app = Flask(__name__) 

from catalogDB import Base, Category, Item, Image 
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
def welcome():
    return render_template('welcome.html')

@app.route('/catalog/', methods = ['GET'])
def renderHomePage():
    login_manager.initialize()
    categories = Category.get_all()
    items = Item.get_latest_10_items()
    items_2d = []
    col_num = 4 # col_num % 12 = 0
    for i in range(0, len(items), col_num):
        temp = []
        for j in range(i, min(len(items), i+col_num)):
            temp.append(items[j])
        items_2d.append(list(temp))
    return render_page('catalog.html', categories = categories, items = items_2d, col_num = col_num)

# Show a category
@app.route('/catalog/category_<int:category_id>/', methods = ['GET'])
def showCategory(category_id):
    category = Category.filter_by_id(category_id)
    items = Item.get_all_by_category(category_id)
    items_2d = []
    for i in range(0, len(items), 3):
        temp = []
        for j in range(i, min(len(items), i+3)):
            temp.append(items[j])
        items_2d.append(list(temp))
    return render_page('showCategory.html', category = category, items = items_2d)


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
    image = Image.filter_by_id(item.img_id)
    return render_page('showItem.html', item = item, category = category, image = image)

# Edit a new Item
@app.route('/catalog/category_<int:category_id>/newItem/', methods = ['GET', 'POST'])
@login_manager.login_required
def newItem(category_id):
    category = Category.filter_by_id(category_id)
    if request.method == 'POST':
        img_title = None
        img_path = None
        img_url = request.form['img_url']
        
        image = Image.store(img_title, img_path, img_url)
        Item.store(request.form['item_title'], request.form['item_desc'], category_id, image.id)
        return redirect(url_for('renderHomePage'))
    else:
        return render_page('updateItem.html', category = category)

# Edit a Item
@app.route('/catalog/category_<int:category_id>/item_<int:item_id>/editItem/', methods = ['GET', 'POST'])
@login_manager.login_required
def editItem(category_id, item_id):
    item = Item.filter_by_id(item_id)
    image = Image.filter_by_id(item.img_id)
    category = Category.filter_by_id(category_id)
    categories = Category.get_all()
    if request.method == 'POST':
        img_title = None
        img_path = None
        img_url = request.form['img_url']
        image.update(img_title, img_path, img_url)
        new_category_id = request.form['category_id'] 
        item.update(request.form['item_title'], request.form['item_desc'], new_category_id, image.id)
        return redirect('catalog/category_%s/' % item.category_id)
    else:
        return render_page('updateItem.html', item = item, image = image, category = category, categories = categories)

# Delete an item
@app.route('/catalog/category_<int:category_id>/item_<int:item_id>/deleteItem', methods = ['GET', 'POST'])
@login_manager.login_required
def deleteItem(category_id, item_id):
    deleted_item_title = Item.filter_by_id(item_id).title
    if request.method == 'POST':
        Item.delete_by_id(item_id)
        return render_page('showItem.html', deleted_item_title = deleted_item_title, category_id = category_id)
    else:
        pass

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
