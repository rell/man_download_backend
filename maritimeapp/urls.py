from django.urls import path, include
from . import views
from .views import (
    apiOverview,
    SitesList, SiteDetail, SiteMeasurementsDaily15List, \
    SiteMeasurementsDaily20List, SiteMeasurementsAllPoints10List, \
    SiteMeasurementsAllPoints15List, SiteMeasurementsAllPoints20List, \
    SiteMeasurementsSeries20List, SiteMeasurementsSeries15List, SiteDelete, \
    AllSitesMeasurementsAP10List,

)

urlpatterns = [
    path('', apiOverview, name='api-overview'),
    path('sites/', SitesList.as_view(), name='sites-list'),
    path('sites/<str:name>/', SiteDetail.as_view(), name='site-detail'),
    path('sites/<str:name>/measurements/daily15/', SiteMeasurementsDaily15List.as_view(),
         name='site-measurements-daily15'),
    path('sites/<str:name>/measurements/daily20/', SiteMeasurementsDaily20List.as_view(),
         name='site-measurements-daily20'),
    path('sites/<str:name>/measurements/allpoints10/', SiteMeasurementsAllPoints10List.as_view(),
         name='site-measurements-allpoints10'),
    path('sites/<str:name>/measurements/allpoints15/', SiteMeasurementsAllPoints15List.as_view(),
         name='site-measurements-allpoints15'),
    path('sites/<str:name>/measurements/allpoints20/', SiteMeasurementsAllPoints20List.as_view(),
         name='site-measurements-allpoints20'),
    path('sites/<str:name>/measurements/series20/', SiteMeasurementsSeries20List.as_view(),
         name='site-measurements-series20'),
    path('sites/<str:name>/measurements/series15/', SiteMeasurementsSeries15List.as_view(),
         name='site-measurements-series15'),
    path('sites/<str:name>/measurements/allpoints10/', AllSitesMeasurementsAP10List.as_view(),
         name='all-sites-measurements-allpoints10'),
    path('sites/<str:name>/delete/', SiteDelete.as_view(), name='site-delete'),
]
