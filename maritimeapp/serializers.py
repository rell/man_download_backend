from rest_framework import serializers
from .models import Site, SiteMeasurementsAllPoints10, SiteMeasurementsAllPoints15, SiteMeasurementsAllPoints20, \
    SiteMeasurementsDaily15, SiteMeasurementsDaily20, SiteMeasurementsSeries20, SiteMeasurementsSeries15


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['name', 'description']


class SiteMeasurementsAllPoints10Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsAllPoints10
        fields = ['id', 'site', 'date', 'time', 'air_mass', 'latlng', 'aod_340nm', 'aod_380nm',
                  'aod_440nm', 'aod_500nm', 'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm',
                  'water_vapor', 'angstrom_exponent', 'last_processing_date', 'aeronet_number',
                  'microtops_number']

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsAllPoints10.objects.create(site=site, **validated_data)


class SiteMeasurementsAllPoints15Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsAllPoints15
        fields = ['id', 'site', 'date', 'time', 'air_mass', 'latlng', 'aod_340nm', 'aod_380nm',
                  'aod_440nm', 'aod_500nm', 'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm',
                  'water_vapor', 'angstrom_exponent', 'last_processing_date', 'aeronet_number',
                  'microtops_number']

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsAllPoints15.objects.create(site=site, **validated_data)


class SiteMeasurementsAllPoints20Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsAllPoints20
        fields = ['id', 'site', 'date', 'time', 'air_mass', 'latlng', 'aod_340nm', 'aod_380nm',
                  'aod_440nm', 'aod_500nm', 'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm',
                  'water_vapor', 'angstrom_exponent', 'last_processing_date', 'aeronet_number',
                  'microtops_number']

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsAllPoints20.objects.create(site=site, **validated_data)


class SiteMeasurementsDaily15Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsDaily15
        fields = ['id', 'site', 'date', 'time', 'air_mass', 'latlng', 'aod_340nm', 'aod_380nm',
                  'aod_440nm', 'aod_500nm', 'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm',
                  'water_vapor', 'angstrom_exponent', 'std_340nm', 'std_380nm', 'std_440nm',
                  'std_500nm', 'std_675nm', 'std_870nm', 'std_1020nm', 'std_1640nm',
                  'std_water_vapor', 'std_angstrom_exponent', 'num_observations',
                  'last_processing_date', 'aeronet_number', 'microtops_number']

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsDaily15.objects.create(site=site, **validated_data)


class SiteMeasurementsDaily20Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsDaily20
        fields = ['id', 'site', 'date', 'time', 'air_mass', 'latlng', 'aod_340nm', 'aod_380nm',
                  'aod_440nm', 'aod_500nm', 'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm',
                  'water_vapor', 'angstrom_exponent', 'std_340nm', 'std_380nm', 'std_440nm',
                  'std_500nm', 'std_675nm', 'std_870nm', 'std_1020nm', 'std_1640nm',
                  'std_water_vapor', 'std_angstrom_exponent', 'num_observations',
                  'last_processing_date', 'aeronet_number', 'microtops_number']

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsDaily20.objects.create(site=site, **validated_data)


class SiteMeasurementsSeries20Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsSeries20
        fields = ['id', 'site', 'date', 'time', 'air_mass', 'latlng', 'aod_340nm', 'aod_380nm',
                  'aod_440nm', 'aod_500nm', 'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm',
                  'water_vapor', 'angstrom_exponent_440_870', 'std_340nm', 'std_380nm', 'std_440nm',
                  'std_500nm', 'std_675nm', 'std_870nm', 'std_1020nm', 'std_1640nm',
                  'std_water_vapor', 'std_angstrom_exponent_440_870', 'num_observations',
                  'last_processing_date', 'aeronet_number', 'microtops_number']

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsSeries20.objects.create(site=site, **validated_data)


class SiteMeasurementsSeries15Serializer(serializers.ModelSerializer):
    site = SiteSerializer(read_only=True)

    class Meta:
        model = SiteMeasurementsSeries15
        fields = ['id', 'site', 'date', 'time', 'air_mass', 'latlng', 'aod_340nm', 'aod_380nm',
                  'aod_440nm', 'aod_500nm', 'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm',
                  'water_vapor', 'angstrom_exponent_440_870', 'std_340nm', 'std_380nm', 'std_440nm',
                  'std_500nm', 'std_675nm', 'std_870nm', 'std_1020nm', 'std_1640nm',
                  'std_water_vapor', 'std_angstrom_exponent_440_870', 'num_observations',
                  'last_processing_date', 'aeronet_number', 'microtops_number']

    def create(self, validated_data):
        site_data = validated_data.pop('site')
        site, _ = Site.objects.get_or_create(name=site_data['name'], defaults={'description': site_data['description']})
        return SiteMeasurementsSeries15.objects.create(site=site, **validated_data)