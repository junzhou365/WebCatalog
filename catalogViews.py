from flask import make_response, render_template, request, redirect, jsonify, url_for, send_from_directory
from . import catalog
import logging

from .catalog_models import Category, Item, Image 
from .loginManager import LoginManager, User, SECRET

login_manager = LoginManager('/catalog')

def render_page(*a, **kw):
    """Just pass user object to template to display user name"""
    kw['user'] = login_manager.user
    kw['catalog'] = catalog
    return render_template(*a, **kw)

def redirect_url():
    """Redirect the url

    First try to redirect to the url in the 'next' query, then try previous 
    page, finally redirect to home page.
    """
    return request.args.get('next') or \
           request.referrer or \
           url_for('renderHomePage')

@catalog.route('/', methods = ['GET'])
def renderHomePage():
    """Catalog home page
    
    It retrieves all categories and latest 10 items, then pass them to response
    to render them. Items are listed in 2d list. 
    In addtion, it initialize login_manager.

    Returns:
        render_page response
    """
    login_manager.initialize()
    categories = Category.get_all()
    items = Item.get_latest_10_items()
    # Create 2d array used for displaying in the html
    # Its size is 4 * rows
    items_2d = []
    col_num = 4 # col_num % 12 = 0
    for i in range(0, len(items), col_num):
        temp = []
        for j in range(i, min(len(items), i+col_num)):
            temp.append(items[j])
        items_2d.append(list(temp))
    return render_page('catalog.html', categories = categories, items = items_2d, col_num = col_num)

@catalog.route('/categories/<int:category_id>/')
def showCategory(category_id):
    """Show Category and all the items in it

    It retrieves all items in this category from database and then pass the 
    reformed 2d array of items and category to the response to display them.

    Arg:
        category_id: category id
    Returns:
        render_page
    """
    category = Category.get_by_id(category_id)
    items = Item.get_all_by_category(category_id)
    # Create 2d array used for displaying in the html
    # Its size is 3 * rows
    items_2d = []
    col_num = 3 # col_num % 12 = 0
    for i in range(0, len(items), col_num):
        temp = []
        for j in range(i, min(len(items), i+3)):
            temp.append(items[j])
        items_2d.append(list(temp))
    return render_page('showCategory.html', category = category, items = items_2d)



@catalog.route('/categories/new', methods = ['GET', 'POST'])
@login_manager.login_required
def newCategory():
    """Edit a new category

    It is responsible for creating new category. It verifies the input form,
    which is category name, stores it.

    Returns:
        render_page if 'GET'
        redirect to show newly created category if 'POST'
    """
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
            return redirect(url_for('catalog.showCategory', category_id=category.id))

    else:
        return render_page('updateCategory.html')
@catalog.route('/categories/<int:category_id>/edit/', methods = ['GET', 'POST'])
@login_manager.login_required
def editCategory(category_id):
    """Edit an existing category

    It changes the name of existing category and category column of all
    items belonging to it.

    Returns:
        render_page if 'GET'
        redirect to show changed category if 'POST'
    """
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
            return redirect(url_for('catalog.showCategory', category_id=editingCategory.id))
    else:
        return render_page('updateCategory.html', category = editingCategory)

# Delete a category
@catalog.route('/categories/<int:category_id>', methods = ['DELETE']) 
@login_manager.login_required
def deleteCategory(category_id):
    """Delete an existing category

    It deletes the selected existing category and all items belonging to it.
    Only 'POST' is allowed here to ensure security.
    No need to redirect or render a new delete page because JS would implement
    it.

    Returns:
        redirect to show deleted category, which will be EMPTY page. 
    """
    deleted_category_name = Category.get_by_id(category_id).name
    Category.delete_by_id(category_id)
    return render_page('showCategory.html', deleted_category_name = deleted_category_name)
            
# Show an Item
@catalog.route('/category_<int:category_id>/item_<int:item_id>', methods = ['GET'])
def showItem(category_id, item_id):
    """Show Item

    This view function needs login.
    It is responsible for creating new category. It verifies the input form,
    which is category name, stores it.

    Returns:
        render_page if 'GET'
        redirect to show newly created category if 'POST'
    """
    item = Item.get_by_id(item_id)
    category = Category.get_by_id(category_id)
    image = Image.get_by_id(item.img_id)
    return render_page('showItem.html', item = item, category = category, image = image)

@catalog.route('/category_<int:category_id>/newItem/', methods = ['GET', 'POST'])
@login_manager.login_required
def newItem(category_id):
    """Edit a new Item

    It create a new item. It verifies the input form,
    which is item name, item description, item image url.
    Image is downloaded from provided url. Item stores item name, item
    description, and image object id. 

    Returns:
        render_page if 'GET'
        redirect to show newly created item if 'POST'
    """
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

@catalog.route('/category_<int:category_id>/item_<int:item_id>/editItem/', methods = ['GET', 'POST'])
@login_manager.login_required
def editItem(category_id, item_id):
    """Edit an existing item

    It changes the name of existing category and category column of all
    items belonging to it.

    Returns:
        render_page if 'GET'
        redirect to show changed category if 'POST'
    """
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
@catalog.route('/category_<int:category_id>/item_<int:item_id>/deleteItem', methods = ['POST'])
@login_manager.login_required
def deleteItem(category_id, item_id):
    """Delete an existing item

    It deletes the selected existing item. 
    Only 'POST' is allowed here to ensure security.
    No need to redirect or render a new delete page because JS would implement
    it.

    Args:

    Returns:
        redirect to show deleted item, which will be EMPTY page. 
    """
    deleted_item_title = Item.get_by_id(item_id).title
    Item.delete_by_id(item_id)
    return render_page('showItem.html', deleted_item_title = deleted_item_title, category_id = category_id)

@catalog.route('/search', methods = ['GET'])
def search():
    """Search full name in database"""
    q = request.args.get('q')
    item = Item.get_by_title(q)
    category = None
    if item:
        category = Category.get_by_id(item.category_id)

    return render_page('searchResult.html', category = category, item = item)

# add url_rule to Login
catalog.add_url_rule('/login/', 'login', login_manager.login, methods = ['GET', 'POST'])

# add url_rule to Signup
catalog.add_url_rule('/signup/', 'signup', login_manager.signup, methods = ['GET', 'POST'])

# add url_rule to Logout
catalog.add_url_rule('/logout/', 'logout', login_manager.logout, methods = ['GET'])

# JSON 
@catalog.route('/.json')
def categories_json():
    """Categories JSON output"""
    categories = Category.get_all()
    return jsonify(Categories=[c.serialize for c in categories])

@catalog.route('/category_<int:category_id>.json')
def items_json(category_id):
    """Items JSON output"""
    items = Item.get_all_by_category(category_id)
    return jsonify(Items=[i.serialize for i in items])

@catalog.route('/category_<int:category_id>/item_<int:item_id>.json')
def item_json(category_id, item_id):
    """Single item JSON output"""
    item = Item.get_by_id(item_id)
    return jsonify(Item=item.serialize)
    
# XML
@catalog.route('/.xml')
def categories_xml():
    """Categories XML output"""
    categories = Category.get_all()
    categories_xml = render_template('catalog.xml', categories = categories)
    response = make_response(categories_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

    
