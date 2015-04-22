#!/usr/bin/env python
import simplejson as json
from flask.ext.script import Manager, Server

from nPowers import app, models

manager = Manager(app)


@manager.command
def initdb(data_file='sites.json'):
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


manager.add_command('runserver', Server(
    use_debugger=True,
    use_reloader=True,
    host='0.0.0.0'
))


if __name__ == '__main__':
    manager.run()
