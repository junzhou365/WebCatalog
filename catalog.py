from flask import Flask, make_response, render_template, request, redirect, jsonify, url_for, send_from_directory

from  main import app

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
    category = Category.get_by_id(category_id)
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
        category_name = request.form['category_name']
        params = dict(category_name = category_name)
        has_fault = False

        if not category_name:
            params['error_category_name'] = "Empty Category Name"
            has_fault = True

        elif Category.get_by_name(category_name):
            params['error_category_name'] = "Category already exists"
            has_fault = True
            
        if has_fault:
            return render_page('updateCategory.html', **params)

        else:
            category = Category.store(category_name)
            return redirect('/catalog/category_%s' % category.id)
    else:
        return render_page('updateCategory.html')

# Edit a category
@app.route('/catalog/category_<int:category_id>/editCategory/', methods = ['GET', 'POST'])
@login_manager.login_required
def editCategory(category_id):
    editingCategory = Category.get_by_id(category_id)
    if request.method == 'POST':
        category_name = request.form['category_name']
        params = dict(category_name = category_name)
        has_fault = False

        if not category_name:
            params['error_category_name'] = "Empty Category Name"
            has_fault = True

        elif Category.get_by_name(category_name):
            params['error_category_name'] = "Category already exists"
            has_fault = True
            
        if has_fault:
            return render_page('updateCategory.html', **params)

        else:
            editingCategory.update(category_name)
            # update all itmes of this category
            for item in editingCategory.get_all_items():
                item.update(category_id = editingCategory.id)
            return redirect('/catalog/category_%s' % editingCategory.id)
    else:
        return render_page('updateCategory.html', category = editingCategory)

# Delete a category
@app.route('/catalog/category_<int:category_id>/deleteCategory', methods = ['GET', 'POST']) 
@login_manager.login_required
def deleteCategory(category_id):
    deleted_category_name = Category.get_by_id(category_id).name
    if request.method == 'POST':
        Category.delete_by_id(category_id)
        return render_page('showCategory.html', deleted_category_name = deleted_category_name)
    else:
        pass
            
# Show an Item
@app.route('/catalog/category_<int:category_id>/item_<int:item_id>', methods = ['GET'])
def showItem(category_id, item_id):
    item = Item.get_by_id(item_id)
    category = Category.get_by_id(category_id)
    image = Image.get_by_id(item.img_id)
    return render_page('showItem.html', item = item, category = category, image = image)

# Edit a new Item
@app.route('/catalog/category_<int:category_id>/newItem/', methods = ['GET', 'POST'])
@login_manager.login_required
def newItem(category_id):
    category = Category.get_by_id(category_id)
    if request.method == 'POST':
        img_title = None
        img_path = None
        img_url = request.form['img_url']
        
        image = Image.store(img_title, img_path, img_url)
        item = Item.store(request.form['item_title'], request.form['item_desc'], category_id, image.id)
        return redirect('catalog/category_%s/item_%s' % (item.category_id, item.id))
    else:
        return render_page('updateItem.html', category = category)

# Edit a Item
@app.route('/catalog/category_<int:category_id>/item_<int:item_id>/editItem/', methods = ['GET', 'POST'])
@login_manager.login_required
def editItem(category_id, item_id):
    item = Item.get_by_id(item_id)
    image = Image.get_by_id(item.img_id)
    category = Category.get_by_id(category_id)
    categories = Category.get_all()
    if request.method == 'POST':
        img_title = None
        img_path = None
        img_url = request.form['img_url']
        image.update(img_title, img_path, img_url)
        new_category_id = request.form['category_id'] 
        item.update(title = request.form['item_title'], desc = request.form['item_desc'], category_id = new_category_id, img_id = image.id)
        return redirect('catalog/category_%s/item_%s' % (item.category_id, item.id))
    else:
        return render_page('updateItem.html', item = item, image = image, category = category, categories = categories)

# Delete an item
@app.route('/catalog/category_<int:category_id>/item_<int:item_id>/deleteItem', methods = ['GET', 'POST'])
@login_manager.login_required
def deleteItem(category_id, item_id):
    deleted_item_title = Item.get_by_id(item_id).title
    if request.method == 'POST':
        Item.delete_by_id(item_id)
        return render_page('showItem.html', deleted_item_title = deleted_item_title, category_id = category_id)
    else:
        pass

# Search
@app.route('/catalog/search', methods = ['GET'])
def search():
    q = request.args.get('q')
    item = Item.get_by_title(q)
    category = None
    if item:
        category = Category.get_by_id(item.category_id)

    return render_page('searchResult.html', category = category, item = item)

# Login
app.add_url_rule('/catalog/login/', 'login', login_manager.login, methods = ['GET', 'POST'])

# Signup
app.add_url_rule('/catalog/signup/', 'signup', login_manager.signup, methods = ['GET', 'POST'])

# Logout
app.add_url_rule('/catalog/logout/', 'logout', login_manager.logout, methods = ['GET'])

# JSON 
@app.route('/catalog.json')
def categories_json():
    categories = Category.get_all()
    return jsonify(Categories=[c.serialize for c in categories])

@app.route('/catalog/category_<int:category_id>.json')
def items_json(category_id):
    items = Item.get_all_by_category(category_id)
    return jsonify(Items=[i.serialize for i in items])

@app.route('/catalog/category_<int:category_id>/item_<int:item_id>.json')
def item_json(category_id, item_id):
    item = Item.get_by_id(item_id)
    return jsonify(Item=item.serialize)
    
# XML
@app.route('/catalog.xml')
def categories_xml():
    categories = Category.get_all()
    categories_xml = render_template('catalog.xml', categories = categories)
    response = make_response(categories_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

    
