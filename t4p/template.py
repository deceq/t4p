import os
import json

import jinja2
import memcache

from config import config, base_path


class MemcacheLoader(jinja2.loaders.BaseLoader):

    def __init__(self, searchpath, encoding='utf-8'):
        self.encoding = encoding
        memcache_url = '{host}:{port}'.format(**config['memcache'])
        self.memcache = memcache.Client([memcache_url], debug=0)

    def get_source(self, environment, template):

        template_name = template
        key = 'template:{}'.format(template_name)
        template = self.memcache.get(key)

        if not template:
            raise Exception('No template found with name: %s' % template)

        template = json.loads(template)

        return template['content'].decode(self.encoding), \
            template['filename'], lambda: True

    def list_templates(self):
        found = set()
        for searchpath in self.searchpath:
            for dirpath, dirnames, filenames in os.walk(searchpath):
                for filename in filenames:
                    template = os.path.join(
                        dirpath, filename
                    )[len(searchpath):]\
                        .strip(os.path.sep) \
                        .replace(os.path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)


if config['use_memcache']:
    templateLoader = MemcacheLoader(searchpath="/")
else:
    tpl_searchpath = config['template_dir'] if config['template_dir'].startswith(base_path) \
        else os.path.join(base_path, config['template_dir'])
    templateLoader = jinja2.FileSystemLoader(searchpath=tpl_searchpath)

templateEnv = jinja2.Environment(loader=templateLoader)


def render_template(name, request, variables={}):
    TEMPLATE_FILE = name
    template = templateEnv.get_template(TEMPLATE_FILE)
    variables.update(config)
    variables['request'] = request
    return template.render(variables)
