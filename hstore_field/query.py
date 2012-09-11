import datetime
from django import VERSION
from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from django.db.models.sql.where import WhereNode, EmptyShortCircuit
from django.db.models.sql.datastructures import EmptyResultSet
from django.contrib.gis.db.models.query import GeoQuerySet
from django.contrib.gis.db.models.sql.query import GeoQuery
from django.contrib.gis.db.models.sql.where import GeoWhereNode

def make_hstore_atom (node, child, qn, connection):
    lvalue, lookup_type, value_annot, param = child
    kwargs = VERSION[:2] >= (1, 3) and {'connection': connection} or {}
    if lvalue.field.db_type(**kwargs) == 'hstore':
        try:
            lvalue, params = lvalue.process(lookup_type, param, connection)
        except EmptyShortCircuit:
            raise EmptyResultSet
        field = node.sql_for_columns(lvalue, qn, connection)
        if lookup_type == 'exact':
            if isinstance(param, dict):
                return ('%s = %%s' % field, [param])
            else:
                raise ValueError('invalid value')
        elif lookup_type == 'contains':
            if isinstance(param, dict):
                return ('%s @> %%s' % field, [param])
            elif isinstance(param, (list, tuple)):
                if param:
                    return ('%s ?& %%s' % field, [param])
                else:
                    raise ValueError('invalid value')
            elif isinstance(param, basestring):
                return ('%s ? %%s' % field, [param])
            else:
                raise ValueError('invalid value')
        elif lookup_type == 'in':
            if isinstance(param, (list, tuple)):
                key, values = param
                return ("%s->'%s' IN %%s" % (field, key), [tuple(values)])
            else:
                raise ValueError('invalid value')
        elif lookup_type in ['lt', 'lte', 'gt', 'gte']:
            if isinstance(param, (list, tuple)):
                key, value = param
                operator = ['<', '<=', '>', '>='][('lt', 'lte', 'gt', 'gte').index(lookup_type)]
                if isinstance(value, datetime.datetime):
                    cast_type = 'timestamp'
                elif isinstance(value, datetime.date):
                    cast_type = 'date'
                elif isinstance(value, datetime.time):
                    cast_type = 'time'
                elif isinstance(value, int):
                    cast_type = 'integer'
                else:
                    cast_type = 'double precision'
                return ("CAST(%s->'%s' AS %s) %s %%s" % (field, key, cast_type, operator), [value])
            else:
                raise ValueError('invalid value')
        else:
            raise TypeError('invalid lookup type')
    else:
        return None

class HStoreWhereNode (WhereNode):
    def make_atom(self, child, qn, connection):
        return make_hstore_atom(self, child, qn, connection) or super(HStoreWhereNode, self).make_atom(child, qn, connection)

class HStoreGeoWhereNode (GeoWhereNode):
    def make_atom(self, child, qn, connection):
        return make_hstore_atom(self, child, qn, connection) or super(HStoreGeoWhereNode, self).make_atom(child, qn, connection)

class HStoreQuery (Query):
    def __init__(self, model):
        super(HStoreQuery, self).__init__(model, HStoreWhereNode)

class HStoreGeoQuery (GeoQuery):
    def __init__(self, model):
        super(HStoreGeoQuery, self).__init__(model, HStoreGeoWhereNode)

class HStoreQuerySet (QuerySet):
    def __init__(self, model=None, query=None, using=None):
        query = query or HStoreQuery(model)
        super(HStoreQuerySet, self).__init__(model=model, query=query, using=using)

class HStoreGeoQuerySet (GeoQuerySet):
    def __init__(self, model=None, query=None, using=None):
        query = query or HStoreGeoQuery(model)
        super(HStoreGeoQuerySet, self).__init__(model=model, query=query, using=using)
