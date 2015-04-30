import os
from PIL import Image
from flask import url_for, request
from nPowers import app


@app.template_filter()
def get_image(key, width=300, height=200):
    mode = '?imageView2/2/w/{}/h/{}'.format(width, height)
    url = app.config['QINIU_URL'] + 'uploads/' + key + mode
    return url


@app.template_filter()
def get_static(name):
    return app.config['QINIU_URL'] + name


@app.template_filter()
def get_ids(object_list):
    return [str(obj.id) for obj in object_list]


@app.template_filter()
def tell_square(uuid):
    img = Image.open(os.path.join(app.config['UPLOAD_DIR'],
                                  uuid+'_thumbnail'+'.png'))
    width, height = img.size
    return (width / height > 2) or (height / width > 2)


@app.template_filter()
def format_time(t):
    return t.strftime('%A %d. %B %Y')


@app.template_filter()
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
