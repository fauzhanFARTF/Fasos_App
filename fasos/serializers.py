from rest_framework import serializers
from .models import MedicalFacility, DistrictOfficeFacility, CCTVFacility
from django.contrib.gis.geos import Point

class BaseFacilitySerializer(serializers.ModelSerializer):
    location = serializers.JSONField(required=False, allow_null=True)
    photo = serializers.ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        loc = validated_data.pop('location', None)
        if loc and 'coordinates' in loc:
            validated_data['location'] = Point(loc['coordinates'][0], loc['coordinates'][1], srid=4326)
        validated_data['operator'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        loc = validated_data.pop('location', None)
        if loc and 'coordinates' in loc:
            instance.location = Point(loc['coordinates'][0], loc['coordinates'][1], srid=4326)
        return super().update(instance, validated_data)

class MedicalFacilitySerializer(BaseFacilitySerializer):
    class Meta:
        model = MedicalFacility
        fields = '__all__'
        read_only_fields = ['operator', 'date_field']

class DistrictOfficeFacilitySerializer(BaseFacilitySerializer):
    class Meta:
        model = DistrictOfficeFacility
        fields = '__all__'
        read_only_fields = ['operator', 'date_field']

class CCTVFacilitySerializer(BaseFacilitySerializer):
    class Meta:
        model = CCTVFacility
        fields = '__all__'
        read_only_fields = ['operator', 'date_field']