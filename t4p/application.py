import os
import json

import tornado
import memcache
import htmlmin

from config import config, base_path

from handler import Handler

ioloop = tornado.ioloop.IOLoop.instance()


class Application(object):

    def __init__(self, urls):
        urle = []

        for url, method in urls:
            handler = type(method.__name__ + 'Handler', (Handler,),
                           dict(handler=tornado.gen.coroutine(method)))
            urle.append((url, handler))
        print(urle)
        self.app = tornado.web.Application(
            urle, cookie_secret=config['cookie_secret'])
        self.template_dir = config['template_dir'] if config['template_dir'].startswith(base_path) \
            else os.path.join(base_path, config['template_dir'])
        self.template_files = []
        if config['use_memcache']:
            self.load_templates()

    def load_templates(self, path=None):
        memcache_url = '{host}:{port}'.format(**config['memcache'])
        mem_client = memcache.Client([memcache_url], debug=0)
        if not path:
            path = self.template_dir

        try:
            templates = os.listdir(path)
        except OSError as error:
            print('Error while loading template files: {}'.format(error))
            return

        for item in templates:
            _item = os.path.join(base_path, path, item)
            if os.path.isfile(_item):
                template_name = _item.replace(self.template_dir, '')[1:]
                key = 'template:{template_path}'.format(
                    template_path=template_name)
                value = {
                    "content": "",
                    "filename": template_name
                }
                with open(_item) as tpl_file:
                    value["content"] = htmlmin.minify(tpl_file.read())
                    mem_client.set(key, json.dumps(value))
            elif os.path.isdir(_item):
                self.load_templates(_item)
            else:
                print('Do nothing, shouldn\'t happen!')

    def start(self):
        self.app.listen(config['listen_port'])
        ioloop.start()
