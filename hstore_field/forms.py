import datetime
import numbers
from django import forms
from django.forms import widgets
from django.forms.util import flatatt, ValidationError
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

def to_hstore (obj):
    if obj is None:
        return ''
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
        return obj.isoformat()
    elif isinstance(obj, numbers.Number):
        return str(obj)
    elif isinstance(obj, basestring):
        return obj
    elif hasattr(obj, 'to_hstore'):
        return obj.to_hstore()
    else:
        raise TypeError("%r is not hstore serializable" % (obj,))

class HstoreEncoder (simplejson.JSONEncoder):
    def default (self, obj):
        return to_hstore(obj)

class HstoreWidget (widgets.Widget):
    def __init__(self, attrs=None):
        self.attrs = {'cols': '84', 'rows': '5'}
        if attrs:
            self.attrs.update(attrs)
    
    def render (self, name, value, attrs=None, choices=()):
        if value is None:
            value = ''
        elif not isinstance(value, unicode):
            value = simplejson.dumps(value, indent=2, cls=HstoreEncoder)
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<textarea%s>%s</textarea>' % (flatatt(final_attrs), conditional_escape(force_unicode(value))))
    
    def value_from_datadict(self, data, files, name):
        return data.get(name, u'{ }')

class HstoreField (forms.Field):
    widget = HstoreWidget
    default_error_messages = { 'invalid': u'Enter a valid hstore string.' }
    
    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        super(HstoreField, self).__init__(*args, **kwargs)
    
    def clean (self, value):
        if value is None or value == '':
            value = 'null'
        super(HstoreField, self).clean(value)
        try:
            value = simplejson.loads(value) 
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])
        return value
