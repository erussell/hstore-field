from . import models
from django import test
from django.db.models import Q
from hstore_field.query import add_hstore, HQ
import datetime

class HStoreTest (test.TestCase):
    
    def _create_items (self, model):
        a = model.objects.create(name='a', data={'a': '1', 'b': '4', 'c': '0',    'd': '2012-01-01 00:01', 'e': '2012-01-01', 'f': '00:01' , 'g': 'Apple'})
        b = model.objects.create(name='b', data={'a': '2', 'b': '5', 'c': '0.33', 'd': '2012-01-01 01:01', 'e': '2012-01-02', 'f': '01:30', 'g': 'Dog'})
        c = model.objects.create(name='c', data={'a': '3', 'b': '6', 'c': '0.66', 'd': '2012-01-02 13:30', 'e': '2012-02-02', 'f': '13:30', 'g': 'Car'})
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
    
    def test_key_value_subset_querying (self):
        for model in (models.Item, models.GeoItem):
            for item in self._create_items(model):
                r = model.objects.filter(HQ(data__a=item.data['a']))
                self.assertEqual(len(r), 1)
                self.assertEqual(r[0], item)
                r = model.objects.filter(HQ(data__a=item.data['a'], data__b=item.data['b']))
                self.assertEqual(len(r), 1)
                self.assertEqual(r[0], item)
    
    def test_multiple_key_subset_querying (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            for keys in (['a'], ['a', 'b']):
                self.assertEqual(model.objects.filter(HQ(data__contains=keys)).count(), 3)
            for keys in (['a', 'z'], ['z', 'y']):
                self.assertEqual(model.objects.filter(HQ(data__contains=keys)).count(), 0)

    def test_single_key_querying (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            for key in ('a', 'b'):
                self.assertEqual(model.objects.filter(HQ(data__contains=key)).count(), 3)
            for key in ('y', 'z'):
                self.assertEqual(model.objects.filter(HQ(data__contains=key)).count(), 0)
    
    def test_in_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(HQ(data__a__in=['0'])).count(), 0)
            self.assertEqual(model.objects.filter(HQ(data__a__in=['1'])).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__a__in=['1','2'])).count(), 2)
            self.assertEqual(model.objects.filter(HQ(data__a__in=['1','2','3'])).count(), 3)
    
    def test_int_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(HQ(data__a__lt=2)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__a__lte=2)).count(), 2)
            self.assertEqual(model.objects.filter(HQ(data__a__gt=2)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__a__gte=2)).count(), 2)
    
    def test_float_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(HQ(data__c__lt=0.33)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__c__lte=0.33)).count(), 2)
            self.assertEqual(model.objects.filter(HQ(data__c__gt=0.33)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__c__gte=0.33)).count(), 2)
    
    def test_datetime_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(HQ(data__d__lt=datetime.datetime(2012,1,1,0,0))).count(), 0)
            self.assertEqual(model.objects.filter(HQ(data__d__gt=datetime.datetime(2012,1,2,13,30))).count(), 0)
            d = datetime.datetime(2012, 1, 1, 1, 1)
            self.assertEqual(model.objects.filter(HQ(data__d__lt=d)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__d__lte=d)).count(), 2)
            self.assertEqual(model.objects.filter(HQ(data__d__gt=d)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__d__gte=d)).count(), 2)
    
    def test_date_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(HQ(data__e__lt=datetime.date(2011,12,31))).count(), 0)
            self.assertEqual(model.objects.filter(HQ(data__e__gt=datetime.date(2012,3,1))).count(), 0)
            d = datetime.date(2012, 1, 2)
            self.assertEqual(model.objects.filter(HQ(data__e__lt=d)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__e__lte=d)).count(), 2)
            self.assertEqual(model.objects.filter(HQ(data__e__gt=d)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__e__gte=d)).count(), 2)
    
    def test_time_range_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(HQ(data__f__lt=datetime.time(0,0))).count(), 0)
            self.assertEqual(model.objects.filter(HQ(data__f__gt=datetime.time(23,0))).count(), 0)
            d = datetime.time(1,30)
            self.assertEqual(model.objects.filter(HQ(data__f__lt=d)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__f__lte=d)).count(), 2)
            self.assertEqual(model.objects.filter(HQ(data__f__gt=d)).count(), 1)
            self.assertEqual(model.objects.filter(HQ(data__f__gte=d)).count(), 2)
    
    def test_related_query (self):
        a = models.Item.objects.create(name='a', data={'a': '1', 'b': '4', 'c': '0',    'd': '2012-01-01 00:01', 'e': '2012-01-01', 'f': '00:01' })
        models.Related.objects.create(item=a)
        self.assertEqual(models.Related.objects.filter(HQ(item__data__a=1)).count(), 1)
        self.assertEqual(models.Related.objects.filter(HQ(item__data__a=2)).count(), 0)
    
    def test_extra_query (self):
        models.Item.objects.create(name='a', data={'a': '1', 'b': '4', 'c': '0',    'd': '2012-01-01 00:01', 'e': '2012-01-01', 'f': '00:01' })
        item = add_hstore(models.Item.objects.all(), 'data', 'a', 'extra_a')[0]
        self.assertEqual(item.extra_a, '1')
        
    def test_combine_hq (self):
        self._create_items(models.Item)
        self.assertEqual(models.Item.objects.filter(HQ(data__a='1') & HQ(data__a='2')).count(), 0)
        self.assertEqual(models.Item.objects.filter(HQ(data__a='1') | HQ(data__a='2')).count(), 2)
        self.assertEqual(models.Item.objects.filter(HQ(data__a__lt=3) & ~HQ(data__a='2')).count(), 1)
        self.assertEqual(models.Item.objects.filter(Q(name='a') & Q(HQ(data__a='1'))).count(), 1)

    def test_iexact_query (self):
        for model in (models.Item, models.GeoItem):
            self._create_items(model)
            self.assertEqual(model.objects.filter(HQ(data__g__iexact='apple')).count(), 1)
            self.assertNotEqual(model.objects.filter(HQ(data__g='apple')).count(), 0)
            self.assertEqual(model.objects.filter(HQ(data__g__iexact='dog')).count(), 1)
            self.assertNotEqual(model.objects.filter(HQ(data__g='dog')).count(), 0)
            self.assertEqual(model.objects.filter(HQ(data__g__iexact='car')).count(), 1)
            self.assertNotEqual(model.objects.filter(HQ(data__g='car')).count(), 0)
