from django.urls import path, include
from . import views
from .views import (
    apiOverview,
    SitesList, SiteDetail, SiteMeasurementsDaily15List, \
    SiteMeasurementsDaily20List, SiteMeasurementsAP10List, \
    SiteMeasurementsAP15List, SiteMeasurementsAP20List, \
    SiteMeasurementsSeries20List, SiteMeasurementsSeries15List, SiteDelete, \
    AllSitesMeasurementsAP10List, SiteMeasurementsDaily20ListDate, \
    SiteMeasurementsDaily15ListDate, SiteMeasurementsDaily20ListLatLng, \
    SiteMeasurementsDaily15ListLatLng

)


urlpatterns = [
    path('', apiOverview, name='api-overview'),
    path('sites/', SitesList.as_view(), name='sites-list'),
    # path('sites/<str:name>/', SiteDetail.as_view(), name='site-detail'),
    path('sites/<str:name>/measurements/daily15/', SiteMeasurementsDaily15List.as_view(),
         name='site-measurements-daily15'),
    path('sites/measurements/D15/', SiteMeasurementsDaily15ListDate.as_view(), name='measurement-list'),
    path('sites/measurements/D15/<str:startdate>/', SiteMeasurementsDaily15ListDate.as_view(), name='measurement-list'),
    path('sites/measurements/D15/<str:startdate>/<str:enddate>/', SiteMeasurementsDaily15ListDate.as_view(),
         name='measurement-list'),
    path('sites/measurements/D15/', SiteMeasurementsDaily15ListLatLng.as_view(), name='site-measurements-daily20-list'),

    path('sites/<str:name>/measurements/daily20/', SiteMeasurementsDaily20List.as_view(),
         name='site-measurements-daily20'),
    path('sites/measurements/D20/', SiteMeasurementsDaily20ListDate.as_view(), name='measurement-list'),
    path('sites/measurements/D20/<str:startdate>/', SiteMeasurementsDaily20ListDate.as_view(), name='measurement-list'),
    path('sites/measurements/D20/<str:startdate>/<str:enddate>/', SiteMeasurementsDaily20ListDate.as_view(),
         name='measurement-list'),
    path('sites/measurements/D20/', SiteMeasurementsDaily20ListLatLng.as_view(), name='site-measurements-daily20-list'),
    path('sites/<str:name>/measurements/AP10/', AllSitesMeasurementsAP10List.as_view(),
         name='all-sites-measurements-allpoints10'),
    path('sites/<str:name>/measurements/AP15/', SiteMeasurementsAP15List.as_view(),
         name='site-measurements-allpoints15'),
    path('sites/<str:name>/measurements/AP20/', SiteMeasurementsAP20List.as_view(),
         name='site-measurements-allpoints20'),
    path('sites/<str:name>/measurements/series20/', SiteMeasurementsSeries20List.as_view(),
         name='site-measurements-series20'),
    path('sites/<str:name>/measurements/series15/', SiteMeasurementsSeries15List.as_view(),
         name='site-measurements-series15'),
    path('sites/<str:name>/delete/', SiteDelete.as_view(), name='site-delete'),
]
