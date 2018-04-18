from django.contrib.gis import forms
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSException, GEOSGeometry


class YandexPointFormField(forms.PointField):
    def to_python(self, value):
        if value and not isinstance(value, GEOSGeometry):
            try:
                value = GEOSGeometry(value)
            except (GEOSException, ValueError, TypeError):
                lon, lat = value.replace(' ', '').split(',')
                value = 'SRID=4326;POINT (%s %s)' % (lat, lon)
        return super(YandexPointFormField, self).to_python(value)


class YandexPointField(models.PointField):
    form_class = YandexPointFormField
