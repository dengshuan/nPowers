import os
from datetime import datetime
from PIL import Image
from flask import url_for, request
from nPowers import app

@app.template_filter()
def get_image(id, type='thumbnail'):
    img = 'uploads/' + id + '_' + type + '.jpeg'
    return url_for('static', filename=img)

@app.template_filter()
def get_ids(object_list):
    return [str(obj.id) for obj in object_list]

@app.template_filter()
def tell_square(id):
    img = Image.open(os.path.join(app.config['UPLOAD_DIR'], id+'_thumbnail'+'.jpeg'))
    width, height = img.size
    return (width/height>2) or (height/width>2)

@app.template_filter()
def format_time(t):
    return t.strftime('%A %d. %B %Y')

@app.template_filter()
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
