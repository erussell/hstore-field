# hstore-field

hstore-field is a library which integrates the `[hstore](http://www.postgresql.org/docs/9.0/interactive/hstore.html)` 
extension of PostgreSQL into Django, assuming one is using Django 1.3+, PostgreSQL 9.0+, and Psycopg 2.3+.

hstore-field draws inspiration from [jordanm/django-hstore](http://github.com/jordanm/django-hstore)
and [niwibe/django-orm-extensions](https://github.com/niwibe/django-orm-extensions), but 
it offers several advantages over those libraries:

 1. Does not require a custom database backend (at the cost of not supporting indexes on
    hstore fields)
 1. Is fully compatable with PostGIS and GeoDjango
 1. Supports range lookup types in queries (i.e., `__lt`, `__gt`, etc...)

## Limitations

- Because we're not using a custom database backend, hstore-field does not support indexes 
  on hstore fields.
- Only numbers, strings, and dates may be stored in an hstore dictionary. Hstore-field will 
  convert numbers and dates to strings for you when you write to the field, but it will not 
  convert them back into their original types when the hstore dictionary is retrieved from 
  the database.
- Hstore-field will automatically try to install configure hstore on any database you connect 
  to, using the `connection_created` signal. If you connect to multiple databases, this could
  present a problem.

## Running the tests

    you$ python manage.py test test_hstore_field 
    
  For this to work
  1. hstore must be installed in your PostgreSQL contrib folder
  1. If you are running PostgreSQL 9.0, the directory containing `pg_config` must be on your `PATH`

## Usage

Model definition is straightforward:

    from django.db import models
    from hstore_field import fields

    class Item (models.Model):
        name = models.CharField(max_length=64)
        data = fields.HStoreField()
        objects = fields.HStoreManager()

Or, for model classes that use GeoDjango:

    from django.contrib.gis.db import models
    from hstore_field import fields
    
    class GeoItem (models.Model):
        name = models.CharField(max_length=64)
        point = models.PointField(null=True)
        data = fields.HStoreField()
        objects = fields.HStoreGeoManager()

You then treat the `data` field as a dictionary of string pairs:

    instance = Item.objects.create(name='something', data={'a': '1', 'b': '2'})
    assert instance.data['a'] == '1'

    empty = Item.objects.create(name='empty')
    assert empty.data == {}

    empty.data['a'] = '1'
    empty.save()
    assert Item.objects.get(name='something').data['a'] == '1'

You can issue queries against hstore fields:

    # equivalence
    Item.objects.filter(data={'a': '1', 'b': '2'})

    # subset by key/value mapping
    Item.objects.filter(data__contains={'a': '1'})

    # subset by list of keys
    Item.objects.filter(data__contains=['a', 'b'])

    # subset by single key
    Item.objects.filter(data__contains='a')
    
    # subset by list of values
    Item.objects.filter(data__in=['a', ['1', '2']])

You can also issue range queries against hstore fields:
    
    # subset by range query using integer
    Item.objects.filter(data__lt=['a', 1])
    
    # subset by range query using float
    Item.objects.filter(data__lt=['a', 1.1])

    # subset by range query as timestamp
    Item.objects.filter(data__lt=['a', datetime.datetime(2012, 1, 1, 0, 15)])
    
    # subset by range query as date
    Item.objects.filter(data__lt=['a', datetime.date(2012, 1, 1)])
    
    # subset by range query as time
    Item.objects.filter(data__lt=['a', datetime.time(0, 15)])
    
Range queries are not especially fast, because they require a table scan and for every 
record's data->a value to be cast from string to another type. However, it is likely to
be much faster than shipping the entire table to the application layer as Django model
objects and filtering it there.

Support for indexing hstore values as numbers and/or dates is planned for a future 
release.
