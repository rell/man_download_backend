from rest_framework import serializers
from .models import Site, SiteMeasurementsAllPoints10, SiteMeasurementsAllPoints15, SiteMeasurementsAllPoints20, \
    SiteMeasurementsDaily15, SiteMeasurementsDaily20, SiteMeasurementsSeries20, SiteMeasurementsSeries15
import math


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['name', 'description']


class CustomFloatField(serializers.FloatField):
    def to_representation(self, value):
        if math.isnan(value):
            return None
        return super().to_representation(value)


class SiteMeasurementsDaily15Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsDaily15
        fields = '__all__'

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsDaily15.objects.create(site=site, **validated_data)


class SiteMeasurementsDaily20Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsDaily20
        fields = '__all__'

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsDaily20.objects.create(site=site, **validated_data)


class SiteMeasurementsAllPoints10Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsAllPoints10
        fields = '__all__'

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsAllPoints10.objects.create(site=site, **validated_data)


class SiteMeasurementsAllPoints15Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsAllPoints15
        fields = '__all__'

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsAllPoints15.objects.create(site=site, **validated_data)


class SiteMeasurementsAllPoints20Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsAllPoints20
        fields = '__all__'

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsAllPoints20.objects.create(site=site, **validated_data)


# class SiteMeasurementsDaily15JSONSerializer(serializers.ModelSerializer):
#     site = SiteSerializer()
#
#     class Meta:
#         model = SiteMeasurementsDaily15
#         fields = '__all__'


class SiteMeasurementsSeries20Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsSeries20
        fields = '__all__'

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsSeries20.objects.create(site=site, **validated_data)


class SiteMeasurementsSeries15Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsSeries15
        fields = '__all__'

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsSeries15.objects.create(site=site, **validated_data)
