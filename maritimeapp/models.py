from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import ArrayField


class Site(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    description = models.TextField()


class SiteMeasurementsDaily15(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255, default='')
    date = models.DateField(db_index=True)
    time = models.TimeField(db_index=False)
    air_mass = models.FloatField(default=-999.0)
    latlng = gis_models.PointField(default=Point(0, 0))
    aod_340nm = models.FloatField(default=-999.0)
    aod_380nm = models.FloatField(default=-999.0)
    aod_440nm = models.FloatField(default=-999.0)
    aod_500nm = models.FloatField(default=-999.0)
    aod_675nm = models.FloatField(default=-999.0)
    aod_870nm = models.FloatField(default=-999.0)
    aod_1020nm = models.FloatField(default=-999.0)
    aod_1640nm = models.FloatField(default=-999.0)
    water_vapor = models.FloatField(default=-999.0)
    angstrom_exponent_440_870 = models.FloatField(default=-999.0)
    std_340nm = models.FloatField(default=-999.0)
    std_380nm = models.FloatField(default=-999.0)
    std_440nm = models.FloatField(default=-999.0)
    std_500nm = models.FloatField(default=-999.0)
    std_675nm = models.FloatField(default=-999.0)
    std_870nm = models.FloatField(default=-999.0)
    std_1020nm = models.FloatField(default=-999.0)
    std_1640nm = models.FloatField(default=-999.0)
    std_water_vapor = models.FloatField(default=-999.0)
    std_angstrom_exponent_440_870 = models.FloatField(default=-999.0)
    num_observations = models.IntegerField(default=0)
    last_processing_date = models.DateField()
    aeronet_number = models.IntegerField(default=0)
    microtops_number = models.IntegerField(default=0)


class SiteMeasurementsDaily20(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255, default='')
    date = models.DateField(db_index=True)
    time = models.TimeField(db_index=False)
    air_mass = models.FloatField(default=-999.0)
    latlng = gis_models.PointField(default=Point(0, 0))
    aod_340nm = models.FloatField(default=-999.0)
    aod_380nm = models.FloatField(default=-999.0)
    aod_440nm = models.FloatField(default=-999.0)
    aod_500nm = models.FloatField(default=-999.0)
    aod_675nm = models.FloatField(default=-999.0)
    aod_870nm = models.FloatField(default=-999.0)
    aod_1020nm = models.FloatField(default=-999.0)
    aod_1640nm = models.FloatField(default=-999.0)
    water_vapor = models.FloatField(default=-999.0)
    angstrom_exponent_440_870 = models.FloatField(default=-999.0)
    std_340nm = models.FloatField(default=-999.0)
    std_380nm = models.FloatField(default=-999.0)
    std_440nm = models.FloatField(default=-999.0)
    std_500nm = models.FloatField(default=-999.0)
    std_675nm = models.FloatField(default=-999.0)
    std_870nm = models.FloatField(default=-999.0)
    std_1020nm = models.FloatField(default=-999.0)
    std_1640nm = models.FloatField(default=-999.0)
    std_water_vapor = models.FloatField(default=-999.0)
    std_angstrom_exponent_440_870 = models.FloatField(default=-999.0)
    num_observations = models.IntegerField(default=0)
    last_processing_date = models.DateField()
    aeronet_number = models.IntegerField(default=0)
    microtops_number = models.IntegerField(default=0)


class SiteMeasurementsAllPoints10(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    time = models.TimeField(db_index=True)
    filename = models.CharField(max_length=255, default='')
    dates = ArrayField(models.DateField(), blank=True, default=list)

    def add_date(self, date):
        self.dates.append(date)
        self.save()

    def remove_date(self, date):
        self.dates.remove(date)
        self.save()

class SiteMeasurementsAllPoints15(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    time = models.TimeField(db_index=True)
    filename = models.CharField(max_length=255, default='')
    dates = ArrayField(models.DateField(), blank=True, default=list)

    def add_date(self, date):
        self.dates.append(date)
        self.save()

    def remove_date(self, date):
        self.dates.remove(date)
        self.save()


class SiteMeasurementsAllPoints20(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    time = models.TimeField(db_index=True)
    filename = models.CharField(max_length=255, default='')
    dates = ArrayField(models.DateField(), blank=True, default=list)

    def add_date(self, date):
        self.dates.append(date)
        self.save()

    def remove_date(self, date):
        self.dates.remove(date)
        self.save()


class SiteMeasurementsSeries20(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    time = models.TimeField(db_index=True)
    filename = models.CharField(max_length=255, default='')
    dates = ArrayField(models.DateField(), blank=True, default=list)

    def add_date(self, date):
        self.dates.append(date)
        self.save()

    def remove_date(self, date):
        self.dates.remove(date)
        self.save()

class SiteMeasurementsSeries15(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    time = models.TimeField(db_index=True)
    filename = models.CharField(max_length=255, default='')
    dates = ArrayField(models.DateField(), blank=True, default=list)

    def add_date(self, date):
        self.dates.append(date)
        self.save()

    def remove_date(self, date):
        self.dates.remove(date)
        self.save()

# OLD MODEL SETUP
#
# class SiteMeasurementsAllPoints10(models.Model):
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)
#     date = models.DateField(db_index=True)
#     time = models.TimeField(db_index=True)
#     air_mass = models.FloatField()
#     latlng = gis_models.PointField(default=Point(0, 0))
#     aod_340nm = models.FloatField()
#     aod_380nm = models.FloatField()
#     aod_440nm = models.FloatField()
#     aod_500nm = models.FloatField()
#     aod_675nm = models.FloatField()
#     aod_870nm = models.FloatField()
#     aod_1020nm = models.FloatField()
#     aod_1640nm = models.FloatField()
#     water_vapor = models.FloatField()
#     angstrom_exponent = models.FloatField()
#     last_processing_date = models.DateField()
#     aeronet_number = models.IntegerField()
#     microtops_number = models.IntegerField()
#
#
# class SiteMeasurementsAllPoints15(models.Model):
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)
#     date = models.DateField(db_index=True)
#     time = models.TimeField(db_index=True)
#     air_mass = models.FloatField()
#     latlng = gis_models.PointField(default=Point(0, 0))
#     aod_340nm = models.FloatField()
#     aod_380nm = models.FloatField()
#     aod_440nm = models.FloatField()
#     aod_500nm = models.FloatField()
#     aod_675nm = models.FloatField()
#     aod_870nm = models.FloatField()
#     aod_1020nm = models.FloatField()
#     aod_1640nm = models.FloatField()
#     water_vapor = models.FloatField()
#     angstrom_exponent = models.FloatField()
#     last_processing_date = models.DateField()
#     aeronet_number = models.IntegerField()
#     microtops_number = models.IntegerField()
#
#
# class SiteMeasurementsAllPoints20(models.Model):
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)
#     date = models.DateField(db_index=True)
#     time = models.TimeField(db_index=True)
#     air_mass = models.FloatField()
#     latlng = gis_models.PointField(default=Point(0, 0))
#     aod_340nm = models.FloatField()
#     aod_380nm = models.FloatField()
#     aod_440nm = models.FloatField()
#     aod_500nm = models.FloatField()
#     aod_675nm = models.FloatField()
#     aod_870nm = models.FloatField()
#     aod_1020nm = models.FloatField()
#     aod_1640nm = models.FloatField()
#     water_vapor = models.FloatField()
#     angstrom_exponent = models.FloatField()
#     last_processing_date = models.DateField()
#     aeronet_number = models.IntegerField()
#     microtops_number = models.IntegerField()
#
#
# class SiteMeasurementsSeries20(models.Model):
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)
#     date = models.DateField(db_index=True)
#     time = models.TimeField(db_index=True)
#     air_mass = models.FloatField()
#     latlng = gis_models.PointField(default=Point(0, 0))
#     aod_340nm = models.FloatField()
#     aod_380nm = models.FloatField()
#     aod_440nm = models.FloatField()
#     aod_500nm = models.FloatField()
#     aod_675nm = models.FloatField()
#     aod_870nm = models.FloatField()
#     aod_1020nm = models.FloatField()
#     aod_1640nm = models.FloatField()
#     water_vapor = models.FloatField()
#     angstrom_exponent_440_870 = models.FloatField()
#     std_340nm = models.FloatField()
#     std_380nm = models.FloatField()
#     std_440nm = models.FloatField()
#     std_500nm = models.FloatField()
#     std_675nm = models.FloatField()
#     std_870nm = models.FloatField()
#     std_1020nm = models.FloatField()
#     std_1640nm = models.FloatField()
#     std_water_vapor = models.FloatField()
#     std_angstrom_exponent_440_870 = models.FloatField()
#     num_observations = models.IntegerField()
#     last_processing_date = models.DateField()
#     aeronet_number = models.IntegerField()
#     microtops_number = models.IntegerField()
#
#
# class SiteMeasurementsSeries15(models.Model):
#     site = models.ForeignKey(Site, on_delete=models.CASCADE)
#     date = models.DateField(db_index=True)
#     time = models.TimeField(db_index=True)
#     air_mass = models.FloatField()
#     latlng = gis_models.PointField(default=Point(0, 0))
#     aod_340nm = models.FloatField()
#     aod_380nm = models.FloatField()
#     aod_440nm = models.FloatField()
#     aod_500nm = models.FloatField()
#     aod_675nm = models.FloatField()
#     aod_870nm = models.FloatField()
#     aod_1020nm = models.FloatField()
#     aod_1640nm = models.FloatField()
#     water_vapor = models.FloatField()
#     angstrom_exponent_440_870 = models.FloatField()
#     std_340nm = models.FloatField()
#     std_380nm = models.FloatField()
#     std_440nm = models.FloatField()
#     std_500nm = models.FloatField()
#     std_675nm = models.FloatField()
#     std_870nm = models.FloatField()
#     std_1020nm = models.FloatField()
#     std_1640nm = models.FloatField()
#     std_water_vapor = models.FloatField()
#     std_angstrom_exponent_440_870 = models.FloatField()
#     num_observations = models.IntegerField()
#     last_processing_date = models.DateField()
#     aeronet_number = models.IntegerField()
#     microtops_number = models.IntegerField()
