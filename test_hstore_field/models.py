from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.db import models
from hstore_field import fields


class Item (models.Model):
    name = models.CharField(max_length=64)
    data = fields.HStoreField()
admin.site.register(Item)

class Related (models.Model):
    item = models.ForeignKey(Item)
admin.site.register(Related)

class GeoItem (models.Model):
    name = models.CharField(max_length=64)
    point = models.PointField(null=True)
    data = fields.HStoreField()
    objects = models.GeoManager()
admin.site.register(GeoItem, OSMGeoAdmin)
