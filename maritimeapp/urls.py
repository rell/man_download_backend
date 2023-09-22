from django.urls import path, include
# from . import views
from .views import download_data, SiteDelete, measurementsOverview, SiteQueryset, get_csrf_token, SitesList, apiOverview, \
    SiteMeasurementsList

urlpatterns = \
[
    path('', apiOverview,
         name='api-overview'),
    path('sites/', SitesList.as_view(),
         name='sites-list'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('measurements/sites/', SiteQueryset.as_view(),
         name='sites-at-date'),
    # path('sites/<str:name>/', SiteDetail.as_view(),
    #         name='site-detail'),
    path('measurements/', SiteMeasurementsList.as_view(),
         name='site-measurements-daily15'),
    path('measurements/info/', measurementsOverview,
         name='measurements-overview'),
    # path('sites/measurements/D15/', SiteMeasurementsDaily15ListDate.as_view(),
    #    name='measurement-list'),
    path('sites/<str:name>/delete/', SiteDelete.as_view(), name='site-delete'),
    path('download/', download_data, name='download_data'),
]
