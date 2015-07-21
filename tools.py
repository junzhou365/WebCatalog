import urllib2
import os

IMAGES_PATH = "static/images/"

def download_file(url):
    """Download file from url to "static/images"

    Download file. Filename is automatically given by the url last part.
    Args:
        url: string
    Returns:
        file path: string, relative path like "static/images/120938120.jpg"

    file_path is used for html src
    """
    if not url:
        return None
    baseFile = os.path.basename(url) # base file name
    file_path = os.path.join(IMAGES_PATH, baseFile)
    try:
        req = urllib2.urlopen(url)
    except urllib2.HTTPError:
        return None
    dirname = os.path.dirname(__file__) + '/' + IMAGES_PATH

    if not os.path.exists(dirname):
        print dirname
        os.makedirs(dirname)

    f = open(os.path.join(dirname, baseFile), 'wb') # 'wb': write binary

    file_size_dl = 0 # downloaded file size
    block_sz = 8192
    while True:
        buffer = req.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
    f.close()
    return '/' + file_path
