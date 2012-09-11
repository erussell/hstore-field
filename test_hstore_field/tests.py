import datetime
from django import test
from . import models

class HStoreTest (test.TestCase):
    
    def _create_items (self, model):
        a = model.objects.create(name='a', data={'a': '1', 'b': '4', 'c': '0',    'd': '2012-01-01 00:01', 'e': '2012-01-01', 'f': '00:01' })
        b = model.objects.create(name='b', data={'a': '2', 'b': '5', 'c': '0.33', 'd': '2012-01-01 01:01', 'e': '2012-01-02', 'f': '01:30' })
        c = model.objects.create(name='c', data={'a': '3', 'b': '6', 'c': '0.66', 'd': '2012-01-02 13:30', 'e': '2012-02-02', 'f': '13:30' })
        return a, b, c

    def test_empty_instantiation (self):
        for model in (models.Item, models.GeoItem):
            a = model.objects.create(name='a')
            self.assertTrue(isinstance(a.data, dict))
            self.assertEqual(a.data, {})
    
    def test_date_encoding (self):
        for model in (models.Item, models.GeoItem):
            d = datetime.datetime.now()
            a = model.objects.create(name='a', data={'a': d})
            self.assertEqual(a.data['a'], d.isoformat())
    
    def test_nubmer_encoding (self):
        for model in (models.Item, models.GeoItem):
            x, y = 10, 10.25
            a = model.objects.create(name='a', data={'x': x, 'y': y})
            self.assertEqual(a.data['x'], str(x))
            self.assertEqual(a.data['y'], str(y))
    
    def test_encoding_error (self):
        for model in (models.Item, models.GeoItem):
            def encode_list ():
                model.objects.create(name='a', data={'a': ['1', '2']})
            def encode_dict (): 
                model.objects.create(name='a', data={'a': {'1': '2'}})
            self.assertRaises(TypeError, encode_list)
            self.assertRaises(TypeError, encode_dict)
    
    def test_empty_querying (self):
        for model in (models.Item, models.GeoItem):
            model.objects.create(name='a')
            self.assertTrue(model.objects.get(data={}))
            self.assertTrue(model.objects.filter(data={}))
            self.assertTrue(model.objects.filter(data__contains={}))
    
    def test_equivalence_querying (self):
        for model in (models.Item, models.GeoItem):
            for item in self._create_items(model):
                data = dict(( (k,item.data[k]) for k in ('a','b','c','d','e','f') ))
                self.assertEqual(model.objects.get(data=data), item)
                r = model.objects.filter(data=data)
                self.assertEqual(len(r), 1)
                self.assertEqual(r[0], item)
    
    def test_key_value_subset_querying (self):
        for model in (models.Item, models.GeoItem):
            for item in self._create_items(model):
                r = model.objects.filter(data__contains={'a': item.data['a']})
                self.assertEqual(len(r), 1)
                self.assertEqual(r[0], item)
                r = model.objects.filter(data__contains={'a': item.data['a'], 'b': item.data['b']})
                self.assertEqual(len(r), 1)
                self.assertEqual(r[0], item)
    
    def test_multiple_key_subset_querying (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            for keys in (['a'], ['a', 'b']):
                self.assertEqual(model.objects.filter(data__contains=keys).count(), 3)
            for keys in (['a', 'z'], ['z', 'y']):
                self.assertEqual(model.objects.filter(data__contains=keys).count(), 0)

    def test_single_key_querying (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            for key in ('a', 'b'):
                self.assertEqual(model.objects.filter(data__contains=key).count(), 3)
            for key in ('y', 'z'):
                self.assertEqual(model.objects.filter(data__contains=key).count(), 0)
    
    def test_in_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(data__in=('a', ['0'])).count(), 0)
            self.assertEqual(model.objects.filter(data__in=('a', ['1'])).count(), 1)
            self.assertEqual(model.objects.filter(data__in=('a', ['1','2'])).count(), 2)
            self.assertEqual(model.objects.filter(data__in=('a', ['1','2','3'])).count(), 3)
    
    def test_int_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(data__lt=('a', 2)).count(), 1)
            self.assertEqual(model.objects.filter(data__lte=('a', 2)).count(), 2)
            self.assertEqual(model.objects.filter(data__gt=('a', 2)).count(), 1)
            self.assertEqual(model.objects.filter(data__gte=('a', 2)).count(), 2)
    
    def test_float_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(data__lt=('c', 0.33)).count(), 1)
            self.assertEqual(model.objects.filter(data__lte=('c', 0.33)).count(), 2)
            self.assertEqual(model.objects.filter(data__gt=('c', 0.33)).count(), 1)
            self.assertEqual(model.objects.filter(data__gte=('c', 0.33)).count(), 2)
    
    def test_datetime_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(data__lt=('d', datetime.datetime(2012,1,1,0,0))).count(), 0)
            self.assertEqual(model.objects.filter(data__gt=('d', datetime.datetime(2012,1,2,13,30))).count(), 0)
            d = datetime.datetime(2012, 1, 1, 1, 1)
            self.assertEqual(model.objects.filter(data__lt=('d', d)).count(), 1)
            self.assertEqual(model.objects.filter(data__lte=('d', d)).count(), 2)
            self.assertEqual(model.objects.filter(data__gt=('d', d)).count(), 1)
            self.assertEqual(model.objects.filter(data__gte=('d', d)).count(), 2)
    
    def test_date_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(data__lt=('e', datetime.date(2011,12,31))).count(), 0)
            self.assertEqual(model.objects.filter(data__gt=('e', datetime.date(2012,3,1))).count(), 0)
            d = datetime.date(2012, 1, 2)
            self.assertEqual(model.objects.filter(data__lt=('e', d)).count(), 1)
            self.assertEqual(model.objects.filter(data__lte=('e', d)).count(), 2)
            self.assertEqual(model.objects.filter(data__gt=('e', d)).count(), 1)
            self.assertEqual(model.objects.filter(data__gte=('e', d)).count(), 2)
    
    def test_time_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(data__lt=('f', datetime.time(0,0))).count(), 0)
            self.assertEqual(model.objects.filter(data__gt=('f', datetime.time(23,0))).count(), 0)
            d = datetime.time(1,30)
            self.assertEqual(model.objects.filter(data__lt=('f', d)).count(), 1)
            self.assertEqual(model.objects.filter(data__lte=('f', d)).count(), 2)
            self.assertEqual(model.objects.filter(data__gt=('f', d)).count(), 1)
            self.assertEqual(model.objects.filter(data__gte=('f', d)).count(), 2)
