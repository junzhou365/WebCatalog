from catalogDB import Item, Category, Image
import datetime

porsche = Category.store('Porsche')

img_911 = Image.store('911', '', 'http://best-carz.com/data_images/gallery/models/porsche-911/porsche-911-02.jpg')
Item.store('911', 'My favorite', porsche.id, img_911.id)




