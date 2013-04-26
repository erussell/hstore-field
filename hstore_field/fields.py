import re
import os
import psycopg2
import subprocess
from django.conf import settings
from django.db import models
from django.db.backends.signals import connection_created
from psycopg2.extras import register_hstore, HstoreAdapter
from . import forms

def register_hstore_on_connection_creation (connection, sender, *args, **kwargs):
    oid = HstoreAdapter.get_oids(connection.connection)
    if oid is None or not oid[0]:
        if connection.connection.server_version < 90000:
            raise psycopg2.ProgrammingError("Database version not supported")
        elif connection.connection.server_version < 90100:
            pg_config = subprocess.Popen(["pg_config", "--sharedir"], stdout=subprocess.PIPE)
            share_dir = pg_config.communicate()[0].strip('\r\n ')
            hstore_sql = os.path.join(share_dir, 'contrib', 'hstore.sql')
            statements = re.compile(r";[ \t]*$", re.M)
            cursor = connection.cursor()
            with open(hstore_sql, 'U') as fp:
                for statement in statements.split(fp.read().decode(settings.FILE_CHARSET)):
                    statement = re.sub(ur"--.*([\n\Z]|$)", "", statement).strip()
                    if statement:
                        cursor.execute(statement + u";")
        else:
            cursor = connection.cursor()
            cursor.execute("CREATE EXTENSION hstore;")
    register_hstore(connection.connection, globally=True)

connection_created.connect(register_hstore_on_connection_creation, dispatch_uid='hstore_field.register_hstore_on_connection_creation')


class HStoreDictionary (dict):

    def __init__(self, value=None, field=None, instance=None, **params):
        super(HStoreDictionary, self).__init__(value, **params)
        self.field = field
        self.instance = instance


class HStoreDescriptor (object):

    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is not None:
            return instance.__dict__[self.field.name]
        else:
            raise AttributeError()

    def __set__(self, instance, value):
        if not isinstance(value, HStoreDictionary):
            value = self.field._attribute_class(value, self.field, instance)
        instance.__dict__[self.field.name] = value


class HStoreField (models.Field):

    _attribute_class = HStoreDictionary
    _descriptor_class = HStoreDescriptor

    __metaclass__ = models.SubfieldBase

    def formfield (self, **params):
        params['form_class'] = forms.HstoreField
        return super(HStoreField, self).formfield(**params)

    def contribute_to_class (self, cls, name):
        super(HStoreField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, self._descriptor_class(self))

    def db_type (self, connection=None):
        return 'hstore'

    def to_python(self, value):
        if isinstance(value, dict):
            for k,v in value.iteritems():
                value[k] = forms.to_hstore(v)
        return value or {}

    def get_prep_value (self, value):
        if not value:
            return {}
        elif isinstance(value, dict):
            result = {}
            for k,v in value.iteritems():
                result[k] = forms.to_hstore(v)
            return result
        else:
            return value

    def south_field_triple (self):
        from south.modelsinspector import introspector
        field_class = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        args, kwargs = introspector(self)
        return field_class, args, kwargs
