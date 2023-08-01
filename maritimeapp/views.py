import math

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.http import Http404
from django.core.paginator import Paginator
from django.http import JsonResponse
from  django.db.models import Q
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from .models import Site, SiteMeasurementsDaily15, SiteMeasurementsDaily20, \
    SiteMeasurementsAllPoints10, SiteMeasurementsAllPoints15, SiteMeasurementsAllPoints20, \
    SiteMeasurementsSeries20, SiteMeasurementsSeries15
from .serializers import SiteSerializer, SiteMeasurementsDaily15Serializer, \
    SiteMeasurementsDaily20Serializer, SiteMeasurementsAllPoints10Serializer, \
    SiteMeasurementsAllPoints15Serializer, SiteMeasurementsAllPoints20Serializer, \
    SiteMeasurementsSeries20Serializer, SiteMeasurementsSeries15Serializer


@api_view(['GET'])
def apiOverview(request):
    # TODO: UPDATE TO CURRENT URLS
    api_urls = {
        # 'List': '/site-list/',
        # 'Detail View': 'site-detail/<str:pk>',
        # 'Create': '/site-create/',
        # 'Update': '/site-update/<str:pk>',
        # 'Delete': '/site-delete/<str:pk>',
    }
    return Response(api_urls)


class CreateDeleteMixin:
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SitesList(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    pagination_class = None  # disable pagination



# class SiteDetail(CreateDeleteMixin, generics.RetrieveUpdateAPIView):
#     queryset = Site.objects.all()
#     serializer_class = SiteSerializer
#     lookup_field = 'id'


class SiteDetail(APIView):
    def delete(self, request, name):
        try:
            site = Site.objects.get(pk=name)
            site.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Site.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SiteMeasurementsDaily15List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsDaily15.objects.all()
    serializer_class = SiteMeasurementsDaily15Serializer

    def get_queryset(self):
        name = self.kwargs['name']
        queryset = SiteMeasurementsDaily15.objects.filter(site_id__name=name)
        queryset = [obj for obj in queryset if not any(math.isnan(getattr(obj, field)) for field in obj.__dict__.keys() if isinstance(getattr(obj, field), float))]
        return queryset



class SiteMeasurementsDaily15ListDate(generics.ListCreateAPIView):
    queryset = SiteMeasurementsDaily15.objects.all()
    serializer_class = SiteMeasurementsDaily15Serializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['site', 'date']
    ordering_fields = ['date', 'time']
    ordering = ['-date', '-time']

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date_str = self.request.query_params.get('startdate', None)
        end_date_str = self.request.query_params.get('enddate', None)
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(date__gte=start_date)
        elif end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(date__lte=end_date)
        return queryset


class SiteMeasurementsDaily15ListLatLng(generics.ListAPIView):
    queryset = SiteMeasurementsDaily15.objects.all()
    serializer_class = SiteMeasurementsDaily15Serializer

    def get_queryset(self):
        min_lat = self.request.query_params.get('min_lat', None)
        max_lat = self.request.query_params.get('max_lat', None)
        min_lng = self.request.query_params.get('min_lng', None)
        max_lng = self.request.query_params.get('max_lng', None)

        queryset = self.queryset

        if min_lat and max_lat and min_lng and max_lng:
            queryset = queryset.filter(latlng__within=(min_lng, min_lat, max_lng, max_lat))

        return queryset

class SiteMeasurementsDaily20List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsDaily20.objects.all()
    serializer_class = SiteMeasurementsDaily20Serializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        name = self.kwargs['name']
        queryset = SiteMeasurementsDaily15.objects.filter(site_id__name=name)
        queryset = [obj for obj in queryset if not any(math.isnan(getattr(obj, field)) for field in obj.__dict__.keys() if isinstance(getattr(obj, field), float))]
        return queryset


class SiteMeasurementsDaily20ListDate(generics.ListCreateAPIView):
    queryset = SiteMeasurementsDaily20.objects.all()
    serializer_class = SiteMeasurementsDaily20Serializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['site', 'date']
    ordering_fields = ['date', 'time']
    ordering = ['-date', '-time']

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date_str = self.request.query_params.get('startdate', None)
        end_date_str = self.request.query_params.get('enddate', None)
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(date__gte=start_date)
        elif end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(date__lte=end_date)
        return queryset


class SiteMeasurementsDaily20ListLatLng(generics.ListAPIView):
    queryset = SiteMeasurementsDaily20.objects.all()
    serializer_class = SiteMeasurementsDaily20Serializer

    def get_queryset(self):
        min_lat = self.request.query_params.get('min_lat', None)
        max_lat = self.request.query_params.get('max_lat', None)
        min_lng = self.request.query_params.get('min_lng', None)
        max_lng = self.request.query_params.get('max_lng', None)

        queryset = self.queryset

        if min_lat and max_lat and min_lng and max_lng:
            queryset = queryset.filter(latlng__within=(min_lng, min_lat, max_lng, max_lat))

        return queryset


class SiteMeasurementsAP10List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsAllPoints10.objects.all()
    serializer_class = SiteMeasurementsAllPoints10Serializer
    pagination_class = PageNumberPagination
    page_size = 100

    def get_queryset(self):
        name = self.kwargs['name']
        queryset = SiteMeasurementsDaily15.objects.filter(site_id__name=name)
        queryset = [obj for obj in queryset if not any(
            math.isnan(getattr(obj, field)) for field in obj.__dict__.keys() if isinstance(getattr(obj, field), float))]
        return queryset

class SiteMeasurementsAP15List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsAllPoints15.objects.all()
    serializer_class = SiteMeasurementsAllPoints15Serializer
    pagination_class = PageNumberPagination
    page_size = 100

    def get_queryset(self):
        name = self.kwargs['name']
        queryset = SiteMeasurementsDaily15.objects.filter(site_id__name=name)
        queryset = [obj for obj in queryset if not any(
            math.isnan(getattr(obj, field)) for field in obj.__dict__.keys() if isinstance(getattr(obj, field), float))]
        return queryset

class SiteMeasurementsAP20List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsAllPoints20.objects.all()
    serializer_class = SiteMeasurementsAllPoints20Serializer
    pagination_class = PageNumberPagination
    page_size = 100

    def get_queryset(self):
        name = self.kwargs['name']
        queryset = SiteMeasurementsDaily15.objects.filter(site_id__name=name)
        queryset = [obj for obj in queryset if not any(
            math.isnan(getattr(obj, field)) for field in obj.__dict__.keys() if isinstance(getattr(obj, field), float))]
        return queryset

class SiteMeasurementsSeries20List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsSeries20.objects.all()
    serializer_class = SiteMeasurementsSeries20Serializer
    pagination_class = PageNumberPagination


class SiteMeasurementsSeries15List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsSeries15.objects.all()
    serializer_class = SiteMeasurementsSeries15Serializer
    pagination_class = PageNumberPagination


# LIST


# class AllSitesMeasurementsAll10List(ListView):
#     model = SiteMeasurementsAllPoints10
#     queryset = SiteMeasurementsAllPoints10.objects.all()


class AllSitesMeasurementsAP10List(CreateDeleteMixin, generics.ListCreateAPIView):
    serializer_class = SiteMeasurementsAllPoints10Serializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        name = self.kwargs['name']
        queryset = SiteMeasurementsAllPoints10.objects.filter(site_id__name=name)
        return queryset

class SiteDelete(generics.DestroyAPIView):
    queryset = Site.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
