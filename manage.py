#!/usr/bin/env python
import os
import simplejson as json
from flask.ext.script import Manager, Server

from nPowers import app, models
from nPowers.utils import ImageHandler

manager = Manager(app)


@manager.command
def init_db(data_file='data.json'):
    "Initialize database."
    with open(data_file, 'r') as f:
        data = json.load(f)
    tag_counter, power_counter, site_counter = 0, 0, 0
    for t in data.get('tag'):
        tag = models.Tag()
        tag.name = t
        tag.save()
        tag_counter += 1
    for p in data.get('power'):
        power = models.Power()
        power.name = p.get('name')
        power.url = p.get('url')
        power.intro = p.get('intro')
        for t in p.get('tags'):
            tag = models.Tag.objects.filter(name=t)
            if tag:
                power.tags.append(tag[0])
        power.save()
        power_counter += 1
    for s in data.get('site'):
        site = models.Site()
        site.name = s.get('name')
        site.url = s.get('url')
        site.intro = s.get('intro')
        for p in s.get('powers'):
            power = models.Power.objects.filter(name=p)
            if power:
                site.powers.append(power[0])
        site.save()
        site_counter += 1
    print('Insert %s tags, %s powers, %s sites' % (tag_counter, power_counter,
                                                   site_counter))


@manager.command
def init_logo(logo_dir='logo'):
    """Initialize logo."""
    count = 0
    for img in os.listdir(logo_dir):
        slug = img.split('.')[0]
        file = os.path.join(logo_dir, img)
        handler = ImageHandler(file)
        handler.make_thumbnail(300, 200)
        uuid = handler.uuid
        power = models.Power.objects.filter(slug=slug).first()
        if power:
            power.img = uuid
            power.save()
            count = count + 1
    print("Initialize %s logos" % count)


@manager.command
def remove_outdated(upload_dir='nPowers/static/uploads'):
    count = 0
    sids = [site.img for site in models.Site.objects.all()]
    pids = [power.img for power in models.Power.objects.all()]
    ids = sids + pids
    for img in os.listdir(upload_dir):
        if img.split('_')[0] not in ids:
            os.remove(os.path.join(upload_dir, img))
            count = count + 1
    print("Remove %s outdated images" % count)


manager.add_command('runserver', Server(
    use_debugger=True,
    use_reloader=True,
    host='0.0.0.0'
))


if __name__ == '__main__':
    manager.run()
