from catalogDB import Item, Category, Image
import datetime
import os

os.mkdir('static/images')
# porsche
porsche = Category.store('Porsche')
# 911
x = Image.store('911', '', 'http://best-carz.com/data_images/gallery/models/porsche-911/porsche-911-02.jpg')
Item.store(x.img_title, 'Sports Car', porsche.id, x.id)

# Cayenne
x = Image.store('Cayenne', '', 'http://image.motortrend.com/f/roadtests/suvs/1407_2015_porsche_cayenne_first_look/71289689/2015-porsche-cayenne-turbo-front-view.jpg')
Item.store(x.img_title, 'SUV', porsche.id, x.id)

# 918-Spyder
x = Image.store('918-Spyder', '', 'http://uncrate.com/p/2010/02/porsche-918-spyder-xl.jpg')
Item.store(x.img_title, 'Sports Car', porsche.id, x.id)


# BMW
bmw = Category.store('BMW')

# M3
x = Image.store('M3', '', 'http://cdn.bmwblog.com/wp-content/uploads/292398_10150995008502393_451986615_n-1.jpg')
Item.store(x.img_title, 'Sports Car', bmw.id, x.id)

# X5
x = Image.store('X5', '', 'http://wallpapers111.com/wp-content/uploads/2015/03/BMW-X5-Pictures.jpg')
Item.store(x.img_title, 'SUV', bmw.id, x.id)

# i8
x = Image.store('i8', '', 'http://www.wired.com/wp-content/uploads/2014/05/088_BMW_i8-new.jpg')
Item.store(x.img_title, 'Electric Car', bmw.id, x.id)

# Mercedes-Benz
benz = Category.store('Mercedes-Benz')

# GLK
x = Image.store('GLK', '', 'http://media.emercedesbenz.com.s3.amazonaws.com/magazine/wp-content/uploads/Mercedes-Benz-GLK-12C179_166.jpg')
Item.store(x.img_title, 'SUV', benz.id, x.id)

# E350
x = Image.store('E350', '', 'http://www.sellanycar.com/cars-related/wp-content/uploads/2015/03/2015-Mercedes-Benz-E-Class-Sedan-on-Top-10-Best-Gas-Mileage-Luxury-Cars.jpg')
Item.store(x.img_title, 'Sedan', benz.id, x.id)

# SLS-AMG
x = Image.store('SLS-AMG', '', 'http://images.thecarconnection.com/lrg/2015-mercedes-benz-sls-amg-gt_100446077_l.jpg')
Item.store(x.img_title, 'Sports Car', benz.id, x.id)
