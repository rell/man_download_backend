import math
import ast
import json
import time
from django.middleware.csrf import get_token

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.http import Http404
# from decimal import Decimal
from django.contrib.gis.geos import Point, Polygon
import os
import tarfile
from django.http import FileResponse, HttpResponse
import shutil
from starlette.background import BackgroundTask

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from .models import SiteMeasurementsAllPoints10, SiteMeasurementsAllPoints15, SiteMeasurementsAllPoints20, \
    SiteMeasurementsDaily15, SiteMeasurementsDaily20, SiteMeasurementsSeries15, SiteMeasurementsSeries20

from .serializers import *


class CreateDeleteMixin:
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if self.lookup_url_kwarg is None:
            return self.delete_all(request, *args, **kwargs)
        else:
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

    def delete_all(self, request, *args, **kwargs):
        Site.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SitesList(generics.ListCreateAPIView):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    lookup_field = 'site_id'
    pagination_class = PageNumberPagination
    pagination_class.page_size = 100


class SitesAtDate(generics.ListCreateAPIView):
    serializer_class = SiteMeasurementsDaily15Serializer
    lookup_field = 'site_id'
    pagination_class = PageNumberPagination
    pagination_class.page_size = 100
    queryset = SiteMeasurementsDaily15.objects.all()

    def get_queryset(self):
        # queryset = SiteMeasurementsDaily15.objects.all()
        [start_date, end_date, min_lat, min_lng, max_lat, max_lng] = [None] * 6

        if self.request.GET.get('start_date') != 'null' and self.request.GET.get('start_date'):
            start_date = self.request.GET.get('start_date')

        if self.request.GET.get('end_date') != 'null' and self.request.GET.get('end_date'):
            end_date = self.request.GET.get('end_date')

        if self.request.GET.get('min_lat') != 'null' and self.request.GET.get('min_lat'):
            min_lat = ast.literal_eval(self.request.GET.get('min_lat'))

        if self.request.GET.get('max_lat') != 'null' and self.request.GET.get('max_lat'):
            max_lat = ast.literal_eval(self.request.GET.get('max_lat'))

        if self.request.GET.get('min_lng') != 'null' and self.request.GET.get('min_lng'):
            min_lng = ast.literal_eval(self.request.GET.get('min_lng'))

        if self.request.GET.get('max_lng') != 'null' and self.request.GET.get('max_lng'):
            max_lng = ast.literal_eval(self.request.GET.get('max_lng'))

        if all([start_date, end_date]):
            self.queryset = self.queryset.filter(date__gte=start_date, date__lte=end_date).distinct()

        elif start_date:
            self.queryset = self.queryset.filter(date__gte=start_date).distinct()

        elif end_date:
            self.queryset = self.queryset.filter(date__lte=end_date).distinct()

        elif all([min_lat, max_lat, min_lng, max_lng, start_date, end_date]):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))

            self.queryset = self.queryset.filter(date__range=[start_date, end_date], latlng__within=polygon)
            count = self.queryset.filter(date__range=[start_date, end_date], latlng__within=polygon).count()

        elif all([min_lat, max_lat, min_lng, max_lng, start_date]):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))
            self.queryset = self.queryset.filter(date__gte=start_date, latlng__within=polygon)

        elif all([min_lat, max_lat, min_lng, max_lng, end_date]):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))
            self.queryset = self.queryset.filter(date__lte=end_date, latlng__within=polygon)

        elif all([min_lat, max_lat, min_lng, max_lng]):
            min_point = Point(float(min_lng), float(min_lat))
            print(min_point)
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))

            self.queryset = self.queryset.filter(
                latlng__within=polygon
            )

        else:
            self.queryset = SitesList.get_queryset(self)

        return self.queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.model == SiteMeasurementsDaily15:
            serializer = self.get_serializer(queryset, many=True)
            site_measurements = serializer.data

            # Extracting the "site" and "date" fields from each object
            extracted_data = []
            for measurement in site_measurements:
                site_name = measurement['site']['name']
                # date = measurement['date']
                existing_entry = next((entry for entry in extracted_data if entry['site_name'] == site_name), None)
                if existing_entry:
                    pass
                    # existing_entry['dates'].append(date)
                else:
                    # extracted_data.append({'site_name': site_name, 'dates': [date]})
                    extracted_data.append({'site_name': site_name})

            return Response(extracted_data)

        else:
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)


# class SitesList(CreateDeleteMixin, generics.ListCreateAPIView):
#     queryset = Site.objects.all()
#     serializer_class = SiteSerializer
#     lookup_field = 'site_id'
#     pagination_class = PageNumberPagination
#     pagination_class.page_size = 100


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


class SiteMeasurementsList(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['site', 'date']
    ordering_fields = ['date', 'time']
    ordering = ['-date']
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10000

    def get_serializer_class(self):
        level = self.request.GET.get('level')
        datatype = self.request.GET.get('type')
        reading = self.request.GET.get('reading')
        if all([level, datatype, reading]):
            serializer_classes = {
                'aod': {
                    'all': {
                        '10': SiteMeasurementsAllPoints10Serializer,
                        '15': SiteMeasurementsAllPoints15Serializer,
                        '20': SiteMeasurementsAllPoints20Serializer,
                    },
                    'daily': {
                        '15': SiteMeasurementsDaily15Serializer,
                        '20': SiteMeasurementsDaily20Serializer,
                    },
                    'series': {
                        '15': SiteMeasurementsSeries15Serializer,
                        '20': SiteMeasurementsSeries20Serializer,
                    },
                },
                'sda': {

                },
            }
            return serializer_classes[reading][datatype][level]
        else:
            return SiteMeasurementsDaily15Serializer

    def get_model(self):
        level = self.request.GET.get('level')
        datatype = self.request.GET.get('type')
        reading = self.request.GET.get('reading')
        if all([level, datatype, reading]):
            set_query = {
                'aod': {
                    'all': {
                        '10': SiteMeasurementsAllPoints10,
                        '15': SiteMeasurementsAllPoints15,
                        '20': SiteMeasurementsAllPoints20,
                    },
                    'daily': {
                        '15': SiteMeasurementsDaily15,
                        '20': SiteMeasurementsDaily20,
                    },
                    'series': {
                        '15': SiteMeasurementsSeries15,
                        '20': SiteMeasurementsSeries20,
                    },
                },
                'sda': {

                },
            }
            return set_query[reading][datatype][level]
        else:
            return SiteMeasurementsDaily15

    def get_queryset(self):
        # queryset = self.get_queryset()
        model_class = self.get_model()
        # if model_class is not None:
        queryset = model_class.objects.all()
        # else:
        #     Handle the case where the requested model class is not found
        # queryset = super().get_queryset()

        # serializer_class = self.get_serializer_class()
        # self.get_serializer_class()
        min_lat = self.request.GET.get('min_lat')
        max_lat = self.request.GET.get('max_lat')
        min_lng = self.request.GET.get('min_lng')
        max_lng = self.request.GET.get('max_lng')
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        site_id = self.request.GET.get('site_id')

        if all([start_date_str, end_date_str, site_id]):
            name = site_id
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            self.queryset = queryset.filter(date__range=[start_date, end_date], site_id__name=name)

        elif all([start_date_str, site_id]):
            name = site_id
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            self.queryset = queryset.filter(date__gte=start_date, site_id__name=name)

        elif all([end_date_str, site_id]):
            name = site_id
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            self.queryset = queryset.filter(date__lte=end_date, site_id__name=name)

        elif all([start_date_str, end_date_str]):
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            self.queryset = queryset.filter(date__range=[start_date, end_date])

        elif all([min_lat, max_lat, min_lng, max_lng]) and all([min_lat, max_lat, min_lng, max_lng]) != 'null' and '':
            # print(all([min_lat, max_lat, min_lng, max_lng]) is not 'null' or '')
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))

            self.queryset = queryset.filter(
                latlng__within=polygon
            )

        elif all([min_lat, max_lat, min_lng, max_lng, start_date_str, end_date_str]) and all(
                [min_lat, max_lat, min_lng, max_lng, start_date_str, end_date_str]) != 'null' and '':
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))

            self.queryset = queryset.filter(date__range=[start_date, end_date], latlng__within=polygon)

        elif site_id:
            name = site_id
            self.queryset = queryset.objects.filter(site_id__name=name)

        elif start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            self.queryset = queryset.filter(date__gte=start_date)

        elif end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            self.queryset = queryset.filter(date__lte=end_date)
        elif queryset is not None:
            self.queryset = queryset

        return self.queryset.all()


class SiteDelete(generics.DestroyAPIView):
    queryset = Site.objects.all()
    lookup_field = 'name'

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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


@api_view(['GET'])
def measurementsOverview(request):
    urls = {
        'required params': 'type, level, aod',
        "all - 10": "/measurements/?reading=aod&level=10&type=all&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "all - 15": "/measurements/?reading=aod&level=15&type=all&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "all - 20": "/measurements/?reading=aod&level=20&type=all&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "daily - 15": "/measurements/?reading=aod&level=15&type=daily&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "daily - 20": "/measurements/?reading=aod&level=20&type=daily&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "series - 15": "/measurements/?reading=aod&level=15&type=series&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "series - 20": "/measurements/?reading=aod&level=20&type=series&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "box latlng example - Atlantic Ocean": "/measurements/?reading=aod&level=20&type=series&min_lat=0&min_lng=-80&max_lat=60&max_lng=-20"
    }
    return Response(urls)


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


@csrf_exempt
def download_data(request):
    print(request.method)
    if request.method == 'OPTIONS':
        try:
            print("HERE")
            print(request.body.find('sites'))
            data = json.loads(request.body.decode('utf-8'))
            sites = data.get('sites', [])
            print(sites)

            # TODO: Process the sites variable as needed

            response = HttpResponse()
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = 'OPTIONS, GET, HEAD, POST'  # Allow POST and OPTIONS methods
            response["Access-Control-Allow-Headers"] = "*"
            # csrf_token = 'my_custom_csrf_token_value'
            # response.set_cookie('X-CSRFToken', csrf_token)
            return response

        except json.decoder.JSONDecodeError:
            return HttpResponse('Invalid JSON data in the request body.')  # sites = data.get('sites', [])
        # print(sites)
        #
        # response = HttpResponse()
        # response['Access-Control-Allow-Origin'] = '*'
        # response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        # response['Access-Control-Allow-Headers'] = 'Content-Type'
        # return response
    else:
        # data = request.POST.get('sites')
        sites = request.GET.get('sites')
        if sites is not None:
            sites = ast.literal_eval(sites)

        # TODO: Eventually add optional date filtering of sets
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        timestamp = str(int(time.time()))

        source_dir = r'D:/DevOps/Active/mandatabase/SRC'  # Path to the source directory
        temp_base_dir = r'D:/DevOps/Active/mandatabase/temp'  # Path to the temporary directory
        unique_temp_folder = timestamp + '_MAN_DATA'
        tar_file_name = unique_temp_folder + '.tar.gz'  # Name for the tar archive
        temp_dir = os.path.join(temp_base_dir, unique_temp_folder)
        save_path = os.path.join(temp_base_dir, tar_file_name)
        keep_files = ['data_usage_policy']

        try:
            def cleanup():
                shutil.rmtree(temp_dir)
                os.remove(save_path)

            # Copy the contents of source_dir to temp_dir
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if (sites is not None and any(site in file for site in sites)) or any(
                            kf in file for kf in keep_files):
                        source_file = os.path.join(root, file)
                        dest_file = os.path.join(temp_dir, os.path.relpath(source_file, source_dir))
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        shutil.copy2(source_file, dest_file)

            response = create_tar_file(temp_dir, save_path, tar_file_name)

            return response

        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            os.remove(save_path, dir_fd=None)

            # Return an error response
            return HttpResponse('An error occurred while processing the request.')


def create_tar_file(temp_dir, save_path, tar_file_name):
    with tarfile.open(save_path, 'w:gz') as tar:
        tar.add(temp_dir, arcname=os.path.basename(temp_dir))
    return FileResponse(open(save_path, 'rb'), as_attachment=True, filename=tar_file_name)
