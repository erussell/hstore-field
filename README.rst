hstore-field
============

hstore-field is a library which integrates the hstore_ extension
of PostgreSQL into Django, assuming one is using Django 1.3-1.5,
PostgreSQL 9.0+, and Psycopg 2.3+.

hstore-field is not compatible with Django 1.6 and above, because the
latest ORM refactor `removed the ability to create custom Q-like
objects`_. I'm currently seeking a work-around.

hstore-field draws some inspiration from `jordanm/django-hstore`_ and
`niwibe/django-orm-extensions`_, but it uses a completely different
mechanism for extending Django, which has the following advantages:

1. Does not require a custom database backend (at the cost of not
   supporting indexes on hstore fields)
2. Does not require a custom QuerySet class, making it fully compatible
   with GeoDjango or any other extension that does subclass QuerySet
3. Supports range lookup types in queries (i.e., ``__lt``, ``__gt``,
   etc...)
4. Mostly compatible with South (see limitations below for specifics)

Limitations
-----------

-  Because we're not using a custom database backend, hstore-field does
   not support indexes on hstore fields.
-  Only numbers, strings, and dates may be stored in an hstore
   dictionary. Hstore-field will convert numbers and dates to strings
   for you when you write to the field, but it *will not convert them
   back* into their original types when the hstore dictionary is
   retrieved from the database. You can make a custom class serialize to
   hstore by giving it a ``to_hstore`` method, which must return a
   string.
-  Hstore-field will automatically try to install configure hstore on
   any database you connect to, using the ``connection_created`` signal.
   If you connect to multiple databases, this could present a problem.
-  Adding an HStoreField with ``null=False`` to an existing model using
   South is problematic, because South cannot emit the correct SQL for
   the default. One workaround is to add the column by putting the SQL
   directly in the migration

   .. code:: python     
   
      def forwards(self, orm):         
         db.execute('ALTER TABLE "[table]" ADD COLUMN "[column]" hstore NOT NULL DEFAULT hstore(array[]::varchar[]);')

   Another alternative is to add the field with ``null=True``, populate the
   field, then set ``null=False``. This is actually considered good
   practice in general, because default values can cause unexpected
   problems.

.. _hstore: http://www.postgresql.org/docs/9.0/interactive/hstore.html
.. _removed the ability to create custom Q-like objects: https://github.com/django/django/commit/d3f00bd5706b35961390d3814dd7e322ead3a9a3#diff-0edd853580d56db07e4020728d59e193L1201
.. _jordanm/django-hstore: http://github.com/jordanm/django-hstore
.. _niwibe/django-orm-extensions: https://github.com/niwibe/django-orm-extensions


Running the tests
-----------------

::

    $ python manage.py test test_hstore_field 

For this to work 

1. hstore must be installed in your PostgreSQL contrib
   folder 
2. If you are running PostgreSQL 9.0, the directory containing
   ``pg_config`` must be on your ``PATH``

Usage
-----

Model definition is straightforward:

.. code:: python

    from django.db import models
    from hstore_field import fields

    class Item (models.Model):
        name = models.CharField(max_length=64)
        data = fields.HStoreField()

You then treat the ``data`` field as a dictionary of string pairs:

.. code:: python

    instance = Item.objects.create(name='something', data={'a': '1', 'b': '2'})
    assert instance.data['a'] == '1'

    empty = Item.objects.create(name='empty')
    assert empty.data == {}

    empty.data['a'] = '1'
    empty.save()
    assert Item.objects.get(name='something').data['a'] == '1'

You can issue queries against hstore keys using the ``HQ`` class
(similar to the ``Q`` class)

.. code:: python

    from hstore_field.query import HQ

    # return only objects whose dictionary contains a given key...
    Item.objects.filter(HQ(data__contains='a'))

    # ...or that contain all keys in a given list (or tuple)
    Item.objects.filter(HQ(data__contains=['a', 'b']))

You can also query against hstore values:

.. code:: python

    # find by exact value
    Item.objects.filter(HQ(data__a='1'])) # equivalent to Item.objects.filter(HQ(data__a__exact='1']))

    # subset by list of values
    Item.objects.filter(HQ(data__a__in=['1', '2']))

    # subset by range query using integer
    Item.objects.filter(HQ(data__a__lt=1))

    # subset by range query using float
    Item.objects.filter(HQ(data__a__gt=1.1))

    # subset by range query as timestamp
    Item.objects.filter(HQ(data__a__lte=datetime.datetime(2012, 1, 1, 0, 15)))

    # subset by range query as date
    Item.objects.filter(HQ(data__a__gte=datetime.date(2012, 1, 1)))

    # subset by range query as time
    Item.objects.filter(HQ(data__a__lte=datetime.time(7, 15)))

Note that, when issuing a range query against an hstore key using a
non-string type, any non-null values for that key that cannot be cast to
the appropriate type will cause the query to fail.

``HQ`` objects may be combined using ``&``, ``|``, and ``~``, just like
``Q`` objects. But they may only be combined with other ``HQ`` objects,
and not with any ``Q`` objects. To combine an ``HQ`` object with a ``Q``
object, you must first wrap the ``HQ`` object in a ``Q`` object. For
example:

.. code:: python

    Item.objects.filter(HQ(data__a__lt=10) & HQ(data__b__lt=20))     # YES!

    Item.objects.filter(Q(HQ(data__a__lt=10)) & Q(data__name="foo")) # YES!

    Item.objects.filter(HQ(data__a__lt=10) & Q(data__name="foo"))    # NO!

Range queries are not especially fast, because they require a table scan
and for every record's hstore->key to be cast from string to another
type. However, it is much faster than shipping the entire table to the
application layer as Django model objects and filtering them there (3-6
times faster in limited testing).

Support for indexing hstore values as numbers and/or dates is planned
for a future release.
