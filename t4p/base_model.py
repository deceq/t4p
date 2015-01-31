import json
import uuid

import memcache

from config import config


class BaseModel(object):

    memcache_url = '{host}:{port}'.format(**config['memcache'])
    mem_client = memcache.Client([memcache_url], debug=0)

    def __init__(self, *args, **kwargs):
        self.model = {}
        for item in dir(self):
            if item.startswith('f_'):
                self.model[item[2:]] = locals()['kwargs'].get(item[2:], '')
            if item.startswith('r_'):
                self.model[item[2:]] = locals()['kwargs'][item[2:]]
        print self.model

    @classmethod
    def get(cls, **kwargs):
        key = cls.conf_key_format.format(**kwargs)
        val = BaseModel.mem_client.get(key)
        try:
            return json.loads(val)
        except:
            return val

    @classmethod
    def generate_ajax_form(cls):
        method_name = '_' + str(uuid.uuid4()).replace('-', '')
        div_id = '_' + str(uuid.uuid4()).replace('-', '')
        js_method = '''
<script type="text/javascript">
function %s() {
%s
$.post( "?", { %s }, function (data) {
var json_data = JSON.parse(data);
if (json_data.data == true) {
$('%s').empty();
$('%s').append('<p class="bg-primary">Action done!</p>');
} else {
$('%s').prepend('<p class="bg-danger">Wrong request! Try again!</p><br/>');
};
}
);}
</script>'''

        form = '''	<div id="{div_id}"
<form action="#">
{fields}
<button type="submit" class="btn btn-default" onClick="{method_name}()">
Submit</button>
</form>'''

        field = '''
<div class="form-group">
<label for="{field_name}">{upper_field_name}</label>
<input type="text" class="form-control" id="{field_name}">
</div>
'''

        js_field = "var {field_name} = $('#{field_name}').val();"
        post_field = "{field_name} : {field_name}"

        fields = ''
        js_fields = ''
        post_fields = []
        for item in dir(cls):
            if item.startswith('f_'):
                field_name = item.split('f_')[-1]
                fields += field.format(field_name=field_name,
                                       upper_field_name=field_name.upper())
                js_fields += js_field.format(field_name=field_name)
                post_fields.append(post_field.format(field_name=field_name))
        post_fields = ",".join(post_fields)

        js_method = js_method % (
            method_name, js_fields, post_fields, div_id, div_id, div_id)
        form = form.format(fields=fields, method_name=method_name,
                           div_id=div_id, js_fields=js_fields,
                           post_fields=post_fields)

        return "".join([js_method, form])

    def delete(self):
        key = self.conf_key_format.format(**self.model)
        return BaseModel.mem_client.delete(key)

    def save(self):
        key = self.conf_key_format.format(**self.model)
        value = self.model

        duplicated = False
        if self.conf_unique:
            if BaseModel.mem_client.get(key):
                duplicated = True

        if duplicated:
            print("Key duplicated: %s" % key)
            return False

        BaseModel.mem_client.set(key, json.dumps(value))
        return True
