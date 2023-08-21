from django.urls import path
from .views import *

urlpatterns = [
    path('', apiOverview, name='api-overview'),
    path('sites/', SitesList.as_view(), name='sites-list'),
    path('measurements/sites/', SitesAtDate.as_view(), name='sites-at-date'),

    # path('sites/<str:name>/', SiteDetail.as_view(), name='site-detail'),
    path('measurements/', SiteMeasurementsList.as_view(),
         name='site-measurements-daily15'),
    path('measurements/info/', measurementsOverview, name='measurements-overview'),    # path('sites/measurements/D15/', SiteMeasurementsDaily15ListDate.as_view(), name='measurement-list'),
    path('sites/<str:name>/delete/', SiteDelete.as_view(), name='site-delete'),
]
