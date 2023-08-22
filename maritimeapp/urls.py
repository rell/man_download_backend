from django.urls import path
from . import views

urlpatterns = [
    path('', views.apiOverview,
         name='api-overview'),
    path('sites/', views.SitesList.as_view(),
         name='sites-list'),
    path('measurements/sites/', views.SitesAtDate.as_view(),
         name='sites-at-date'),
    # path('sites/<str:name>/', SiteDetail.as_view(),
    #         name='site-detail'),
    path('measurements/', views.SiteMeasurementsList.as_view(),
         name='site-measurements-daily15'),
    path('measurements/info/', views.measurementsOverview,
         name='measurements-overview'),
    # path('sites/measurements/D15/', SiteMeasurementsDaily15ListDate.as_view(),
    #    name='measurement-list'),
    path('sites/<str:name>/delete/', views.SiteDelete.as_view(),
         name='site-delete'),

    path('download/', views.download_data, name='download_tar'),

]
