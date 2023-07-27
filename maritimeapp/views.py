from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.http import Http404
from django.core.paginator import Paginator
from django.http import JsonResponse

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
        'List': '/site-list/',
        'Detail View': 'site-detail/<str:pk>',
        'Create': '/site-create/',
        'Update': '/site-update/<str:pk>',
        'Delete': '/site-delete/<str:pk>',
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
    pagination_class = PageNumberPagination


class SiteMeasurementsDaily20List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsDaily20.objects.all()
    serializer_class = SiteMeasurementsDaily20Serializer
    pagination_class = PageNumberPagination


class SiteMeasurementsAllPoints10List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsAllPoints10.objects.all()
    serializer_class = SiteMeasurementsAllPoints10Serializer
    pagination_class = PageNumberPagination


class SiteMeasurementsAllPoints15List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsAllPoints15.objects.all()
    serializer_class = SiteMeasurementsAllPoints15Serializer
    pagination_class = PageNumberPagination


class SiteMeasurementsAllPoints20List(CreateDeleteMixin, generics.ListCreateAPIView):
    queryset = SiteMeasurementsAllPoints20.objects.all()
    serializer_class = SiteMeasurementsAllPoints20Serializer
    pagination_class = PageNumberPagination


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
        queryset = SiteMeasurementsAllPoints10.objects.filter(site__name=name)
        return queryset


class SiteDelete(generics.DestroyAPIView):
    queryset = Site.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
