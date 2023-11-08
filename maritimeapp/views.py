import ast
import time
from django.middleware.csrf import get_token
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.http import Http404
from django.contrib.gis.geos import Point, Polygon
import tarfile
from io import StringIO
from django.http import JsonResponse
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
import pandas as pd
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import csv
import json
import os
import shutil
from .serializers import *
import concurrent.futures


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
                self.get_object().delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Http404:

                return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
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
    lookup_field = "site_id"
    pagination_class = PageNumberPagination
    pagination_class.page_size = 100


class SiteQueryset(generics.ListCreateAPIView):
    serializer_class = SiteMeasurementsDaily15Serializer
    lookup_field = "site_id"
    pagination_class = PageNumberPagination
    pagination_class.page_size = 100
    queryset = SiteMeasurementsDaily15.objects.all()

    def get_queryset(self):
        # queryset = SiteMeasurementsDaily15.objects.all()
        [start_date, end_date, min_lat, min_lng, max_lat, max_lng] = [None] * 6

        if self.request.GET.get("start_date") != "null" and self.request.GET.get("start_date"):
            start_date = self.request.GET.get("start_date")

        if self.request.GET.get("end_date") != "null" and self.request.GET.get("end_date"):
            end_date = self.request.GET.get("end_date")

        if self.request.GET.get("min_lat") != "null" and self.request.GET.get("min_lat"):
            min_lat = ast.literal_eval(self.request.GET.get("min_lat"))

        if self.request.GET.get("max_lat") != "null" and self.request.GET.get("max_lat"):
            max_lat = ast.literal_eval(self.request.GET.get("max_lat"))

        if self.request.GET.get("min_lng") != "null" and self.request.GET.get("min_lng"):
            min_lng = ast.literal_eval(self.request.GET.get("min_lng"))

        if self.request.GET.get("max_lng") != "null" and self.request.GET.get("max_lng"):
            max_lng = ast.literal_eval(self.request.GET.get("max_lng"))

        if all([min_lat, max_lat, min_lng, max_lng, start_date, end_date]):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))
            self.queryset = self.queryset.filter(date__range=[start_date, end_date], latlng__within=polygon)
            count = self.queryset.filter(date__range=[start_date, end_date], latlng__within=polygon).count()

        elif all([min_lat, max_lat, min_lng, max_lng, start_date]):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))
            self.queryset = self.queryset.filter(date__gte=start_date, latlng__within=polygon)

        elif all([min_lat, max_lat, min_lng, max_lng, end_date]):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))
            self.queryset = self.queryset.filter(date__lte=end_date, latlng__within=polygon)

        elif all([min_lat, max_lat, min_lng, max_lng]):
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))

            self.queryset = self.queryset.filter(
                latlng__within=polygon
            )

        elif all([start_date, end_date]):
            self.queryset = self.queryset.filter(date__gte=start_date, date__lte=end_date).distinct()

        elif start_date:
            self.queryset = self.queryset.filter(date__gte=start_date).distinct()

        elif end_date:
            self.queryset = self.queryset.filter(date__lte=end_date).distinct()

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
                site_name = measurement["site"]["name"]
                # date = measurement["date"]
                existing_entry = next((entry for entry in extracted_data if entry["site_name"] == site_name), None)
                if existing_entry:
                    pass
                    # existing_entry["dates"].append(date)
                else:
                    # extracted_data.append({"site_name": site_name, "dates": [date]})
                    extracted_data.append({"site_name": site_name})

            return Response(extracted_data)

        else:
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)


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
    filterset_fields = ["site", "date"]
    ordering_fields = ["date", "time"]
    ordering = ["-date"]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10000

    def get_serializer_class(self):
        level = self.request.GET.get("level")
        datatype = self.request.GET.get("type")
        reading = self.request.GET.get("reading")
        if all([level, datatype, reading]):
            serializer_classes = {
                "aod": {
                    # "all": {
                    #     "10": SiteMeasurementsAllPoints10Serializer,
                    #     "15": SiteMeasurementsAllPoints15Serializer,
                    #     "20": SiteMeasurementsAllPoints20Serializer,
                    # },
                    "daily": {
                        "15": SiteMeasurementsDaily15Serializer,
                        "20": SiteMeasurementsDaily20Serializer,
                    },
                    # "series": {
                    #     "15": SiteMeasurementsSeries15Serializer,
                    #     "20": SiteMeasurementsSeries20Serializer,
                    # },
                },
                # "sda": {
                #
                # },
            }
            return serializer_classes[reading][datatype][level]
        else:
            return SiteMeasurementsDaily15Serializer

    def get_model(self):
        level = self.request.GET.get("level")
        datatype = self.request.GET.get("type")
        reading = self.request.GET.get("reading")
        if all([level, datatype, reading]):
            set_query = {
                "aod": {
                    # "all": {
                    #     "10": SiteMeasurementsAllPoints10,
                    #     "15": SiteMeasurementsAllPoints15,
                    #     "20": SiteMeasurementsAllPoints20,
                    # },
                    "daily": {
                        "15": SiteMeasurementsDaily15,
                        "20": SiteMeasurementsDaily20,
                    },
                    # "series": {
                    #     "15": SiteMeasurementsSeries15,
                    #     "20": SiteMeasurementsSeries20,
                    # },
                },
                "sda": {

                },
            }
            return set_query[reading][datatype][level]
        else:
            return SiteMeasurementsDaily15

    def get_queryset(self):
        model_class = self.get_model()
        queryset = model_class.objects.all()

        min_lat = self.request.GET.get("min_lat")
        min_lng = self.request.GET.get("min_lng")
        max_lat = self.request.GET.get("max_lat")
        max_lng = self.request.GET.get("max_lng")
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")
        site_id = self.request.GET.get("site_id")

        if (all([min_lat, max_lat, min_lng, max_lng, start_date_str, end_date_str]) and
                all([min_lat, max_lat, min_lng, max_lng, start_date_str, end_date_str]) != "null" and
                all([min_lat, max_lat, min_lng, max_lng, start_date_str, end_date_str]) != ""):
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))

            self.queryset = queryset.filter(date__range=[start_date, end_date], latlng__within=polygon)

        elif (all([min_lat, max_lat, min_lng, max_lng]) and
              all([min_lat, max_lat, min_lng, max_lng]) != "null" and
              all([min_lat, max_lat, min_lng, max_lng]) != ""):
            min_point = Point(float(min_lng), float(min_lat))
            max_point = Point(float(max_lng), float(max_lat))
            polygon = Polygon.from_bbox((min_point.x, min_point.y, max_point.x, max_point.y))

            self.queryset = queryset.filter(
                latlng__within=polygon
            )

        elif all([start_date_str, end_date_str, site_id]):
            name = site_id
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            self.queryset = queryset.filter(date__range=[start_date, end_date], site_id__name=name)

        elif all([start_date_str, site_id]):
            name = site_id
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            self.queryset = queryset.filter(date__gte=start_date, site_id__name=name)

        elif all([end_date_str, site_id]):
            name = site_id
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            self.queryset = queryset.filter(date__lte=end_date, site_id__name=name)

        elif all([start_date_str, end_date_str]):
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            self.queryset = queryset.filter(date__range=[start_date, end_date])

        elif site_id:
            name = site_id
            self.queryset = queryset.objects.filter(site_id__name=name)

        elif start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            self.queryset = queryset.filter(date__gte=start_date)

        elif end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            self.queryset = queryset.filter(date__lte=end_date)

        elif queryset is not None:
            self.queryset = queryset

        return self.queryset.all()


class SiteDelete(generics.DestroyAPIView):
    queryset = Site.objects.all()
    lookup_field = "name"

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@api_view(["GET"])
def apiOverview(request):
    # TODO: UPDATE TO CURRENT URLS
    api_urls = {
        # "List": "/site-list/",
        # "Detail View": "site-detail/<str:pk>",
        # "Create": "/site-create/",
        # "Update": "/site-update/<str:pk>",
        # "Delete": "/site-delete/<str:pk>",
    }
    return Response(api_urls)


@api_view(["GET"])
def measurementsOverview(request):
    urls = {
        "required params": "type, level, aod",
        "daily - 15": "/measurements/?reading=aod&level=15&type=daily&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "daily - 20": "/measurements/?reading=aod&level=20&type=daily&site_id=ABC123&start_date=2022-01-01&end_date=2022-01-31",
        "box latlng example - Atlantic Ocean": "/measurements/?reading=aod&level=20&type=series&min_lat=0&min_lng=-80&max_lat=60&max_lng=-20"
    }
    return Response(urls)


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrfToken": csrf_token})


@csrf_exempt
def download_data(request):
    global cleanup
    if request.method == "POST":
        MAX_WORKERS = 4

        source_dir = r"./SRC"  # Path to the source directory
        temp_base_dir = r"./mandatabase/temp"  # Path to the temporary directory
        unique_temp_folder = str(int(time.time())) + "_MAN_DATA"
        tar_file_name = unique_temp_folder + ".tar.gz"  # Name for the tar archive
        temp_dir = os.path.join(temp_base_dir, unique_temp_folder)
        save_path = os.path.join(temp_base_dir, tar_file_name)
        keep_files = ["data_usage_policy"]
        data = json.loads(request.body.decode("utf-8"))

        sites = data["sites"]["list"]
        sites = [item for item in sites if item != ""]
        date_list = data["sites"]["dates"]
        options = data["download_options"]
        # key_list = [key for key, value in options.items() if value]

        # Quality Allowed
        # lev10 = data["download_options"]["lev10"]
        # lev15 = data["download_options"]["lev15"]
        # lev20 = data["download_options"]["lev20"]

        # Date Contraint
        start_date = data["date_range"]["start_date"]
        end_date = data["date_range"]["end_date"]

        # Check and assign new values if necessary
        if start_date is None or start_date == "null":
            start_date = None  # Replace with your default value

        if end_date is None or end_date == "null":
            end_date = None  # Replace with your default value

        try:
            def get_headerkey(filename):
                key_to_compare = None

                if "lev" in filename:
                    key_to_compare = filename.split('_')[-1]
                elif "ONEILL" in filename:
                    key_to_compare = filename.split('_')[-2]

                ap_aod = [
                    "points.lev10",
                    "points.lev15",
                    "points.lev20",
                ]
                daily_aod = [
                    "daily.lev15",
                    "daily.lev20",
                ]

                series_aod = [
                    "series.lev15",
                    "series.lev20",

                ]
                ap_sda = [
                    "points.ONEILL"
                ]

                daily_sda = [
                    "daily.ONEILL",
                ]
                series_sda = [
                    "series.ONEILL"
                ]

                if key_to_compare in ap_aod:
                    return "Date(dd:mm:yyyy),Time(hh:mm:ss),Air Mass,Latitude,Longitude,AOD_340nm,AOD_380nm,AOD_440nm,AOD_500nm,AOD_675nm,AOD_870nm,AOD_1020nm,AOD_1640nm,Water Vapor(cm),440-870nm_Angstrom_Exponent,Last_Processing_Date(dd:mm:yyyy),AERONET_Number,Microtops_Number".split(
                        ",")
                elif key_to_compare in daily_aod:
                    return "Date(dd:mm:yyyy),Time(hh:mm:ss),Air Mass,Latitude,Longitude,AOD_340nm,AOD_380nm,AOD_440nm,AOD_500nm,AOD_675nm,AOD_870nm,AOD_1020nm,AOD_1640nm,Water Vapor(cm),440-870nm_Angstrom_Exponent,STD_340nm,STD_380nm,STD_440nm,STD_500nm,STD_675nm,STD_870nm,STD_1020nm,STD_1640nm,STD_Water_Vapor(cm),STD_440-870nm_Angstrom_Exponent,Number_of_Observations,Last_Processing_Date(dd:mm:yyyy),AERONET_Number,Microtops_Number".split(
                        ",")
                elif key_to_compare in series_aod:
                    return "Date(dd:mm:yyyy),Time(hh:mm:ss),Air Mass,Latitude,Longitude,AOD_340nm,AOD_380nm,AOD_440nm,AOD_500nm,AOD_675nm,AOD_870nm,AOD_1020nm,AOD_1640nm,Water Vapor(cm),440-870nm_Angstrom_Exponent,STD_340nm,STD_380nm,STD_440nm,STD_500nm,STD_675nm,STD_870nm,STD_1020nm,STD_1640nm,STD_Water_Vapor(cm),STD_440-870nm_Angstrom_Exponent,Number_of_Observations,Last_Processing_Date(dd:mm:yyyy),AERONET_Number".split(
                        ",")

                elif key_to_compare in ap_sda:
                    return "Date(dd:mm:yyyy),Time(hh:mm:ss),Julian_Day,Latitude,Longitude,Total_AOD_500nm[tau_a],Fine_Mode_AOD_500nm[tau_f],Coarse_Mode_AOD_500nm[tau_c],FineModeFraction_500nm[eta],CoarseModeFraction_500nm[1-eta],2nd_Order_Reg_Fit_Error-Total_AOD_500nm[regression_dtau_a],RMSE_Fine_Mode_AOD_500nm[Dtau_f],RMSE_Coarse_Mode_AOD_500nm[Dtau_c],RMSE_FMF_and_CMF_Fractions_500nm[Deta],Angstrom_Exponent(AE)-Total_500nm[alpha],dAE/dln(wavelength)-Total_500nm[alphap],AE-Fine_Mode_500nm[alpha_f],dAE/dln(wavelength)-Fine_Mode_500nm[alphap_f],Solar_Zenith_Angle,Air_Mass,870nm_Input_AOD,675nm_Input_AOD,500nm_Input_AOD,440nm_Input_AOD,380nm_Input_AOD,Last_Processing_Date (dd:mm:yyyy),AERONET_Number,Microtops_Number,Number_of_Wavelengths,Exact_Wavelengths_for_Input_AOD(nm),x,u,c,s".split(
                        ",")
                elif key_to_compare in daily_sda:
                    return "Date(dd:mm:yyyy),Time(hh:mm:ss),Julian_Day,Latitude,Longitude,Total_AOD_500nm[tau_a],Fine_Mode_AOD_500nm[tau_f],Coarse_Mode_AOD_500nm[tau_c],FineModeFraction_500nm[eta],CoarseModeFraction_500nm[1-eta],2nd_Order_Reg_Fit_Error-Total_AOD_500nm[regression_dtau_a],RMSE_Fine_Mode_AOD_500nm[Dtau_f],RMSE_Coarse_Mode_AOD_500nm[Dtau_c],RMSE_FMF_and_CMF_Fractions_500nm[Deta],Angstrom_Exponent(AE)-Total_500nm[alpha],dAE/dln(wavelength)-Total_500nm[alphap],AE-Fine_Mode_500nm[alpha_f],dAE/dln(wavelength)-Fine_Mode_500nm[alphap_f],870nm_Input_AOD,675nm_Input_AOD,500nm_Input_AOD,440nm_Input_AOD,380nm_Input_AOD,STDEV-Total_AOD_500nm[tau_a],STDEV-Fine_Mode_AOD_500nm[tau_f],STDEV-Coarse_Mode_AOD_500nm[tau_c],STDEV-FineModeFraction_500nm[eta],STDEV-CoarseModeFraction_500nm[1-eta],STDEV-2nd_Order_Reg_Fit_Error-Total_AOD_500nm[regression_dtau_a],STDEV-RMSE_Fine_Mode_AOD_500nm[Dtau_f],STDEV-RMSE_Coarse_Mode_AOD_500nm[Dtau_c],STDEV-RMSE_FMF_and_CMF_Fractions_500nm[Deta],STDEV-Angstrom_Exponent(AE)-Total_500nm[alpha],STDEV-dAE/dln(wavelength)-Total_500nm[alphap],STDEV-AE-Fine_Mode_500nm[alpha_f],STDEV-dAE/dln(wavelength)-Fine_Mode_500nm[alphap_f],STDEV-870nm_Input_AOD,STDEV-675nm_Input_AOD,STDEV-500nm_Input_AOD,STDEV-440nm_Input_AOD,STDEV-380nm_Input_AOD,Number_of_Observations,Last_Processing_Date (dd:mm:yyyy),AERONET_Number,Microtops_Number,Number_of_Wavelengths,Exact_Wavelengths_for_Input_AOD(nm)".split(
                        ",")
                elif key_to_compare in series_sda:
                    return "Date(dd:mm:yyyy),Time(hh:mm:ss),Julian_Day,Latitude,Longitude,Total_AOD_500nm[tau_a],Fine_Mode_AOD_500nm[tau_f],Coarse_Mode_AOD_500nm[tau_c],FineModeFraction_500nm[eta],CoarseModeFraction_500nm[1-eta],2nd_Order_Reg_Fit_Error-Total_AOD_500nm[regression_dtau_a],RMSE_Fine_Mode_AOD_500nm[Dtau_f],RMSE_Coarse_Mode_AOD_500nm[Dtau_c],RMSE_FMF_and_CMF_Fractions_500nm[Deta],Angstrom_Exponent(AE)-Total_500nm[alpha],dAE/dln(wavelength)-Total_500nm[alphap],AE-Fine_Mode_500nm[alpha_f],dAE/dln(wavelength)-Fine_Mode_500nm[alphap_f],870nm_Input_AOD,675nm_Input_AOD,500nm_Input_AOD,440nm_Input_AOD,380nm_Input_AOD,STDEV-Total_AOD_500nm[tau_a],STDEV-Fine_Mode_AOD_500nm[tau_f],STDEV-Coarse_Mode_AOD_500nm[tau_c],STDEV-FineModeFraction_500nm[eta],STDEV-CoarseModeFraction_500nm[1-eta],STDEV-2nd_Order_Reg_Fit_Error-Total_AOD_500nm[regression_dtau_a],STDEV-RMSE_Fine_Mode_AOD_500nm[Dtau_f],STDEV-RMSE_Coarse_Mode_AOD_500nm[Dtau_c],STDEV-RMSE_FMF_and_CMF_Fractions_500nm[Deta],STDEV-Angstrom_Exponent(AE)-Total_500nm[alpha],STDEV-dAE/dln(wavelength)-Total_500nm[alphap],STDEV-AE-Fine_Mode_500nm[alpha_f],STDEV-dAE/dln(wavelength)-Fine_Mode_500nm[alphap_f],STDEV-870nm_Input_AOD,STDEV-675nm_Input_AOD,STDEV-500nm_Input_AOD,STDEV-440nm_Input_AOD,STDEV-380nm_Input_AOD,Number_of_Observations,Last_Processing_Date (dd:mm:yyyy),AERONET_Number,Microtops_Number,Number_of_Wavelengths,Exact_Wavelengths_for_Input_AOD(nm),x,y,z,a".split(
                        ",")
                else:
                    return None

            def move_accepted_files(file_pair):
                try:
                    filtered_df = None
                    source_file, dest_file, filename = file_pair

                    with open(source_file, "r") as file:
                        content = file.read()

                    # Split the content into lines
                    lines = content.split("\n")

                    # Extract the first four lines
                    first_four_lines = "\n".join(lines[:4])
                    original_header = lines[4]
                    with open(dest_file, "w") as file:
                        file.write(first_four_lines)

                    # Create a DataFrame from the remaining lines
                    remaining_content = "\n".join(lines[5:])

                    check_date_column = "Date(dd:mm:yyyy)"
                    header = get_headerkey(filename)
                    if ".lev" in filename:
                        df = pd.read_csv(StringIO("".join(remaining_content)), encoding="latin-1", header=None,
                                         delimiter=",")
                        df.columns = header
                        key = filename.rsplit("_", 1)[0]
                        key = key.split("_all")[0]
                        df[check_date_column] = pd.to_datetime(df[check_date_column], format="%d:%m:%Y")
                        is_in_list = df[check_date_column].isin(date_list[key])
                        filtered_df = df.loc[is_in_list]
                        filtered_df[check_date_column] = pd.to_datetime(filtered_df[check_date_column],
                                                                        format="%Y-%m-%d").dt.strftime("%d:%m:%Y")

                    if ".ONEILL" in filename:
                        df = pd.read_csv(StringIO("".join(remaining_content)), encoding="latin-1", header=None,
                                         delimiter=",")
                        df.columns = header
                        key = filename.rsplit("_", 1)[0]
                        key = key.split("_all")[0]
                        df[check_date_column] = pd.to_datetime(df[check_date_column], format="%d:%m:%Y")
                        is_in_list = df[check_date_column].isin(date_list[key])
                        filtered_df = df.loc[is_in_list]
                        filtered_df[check_date_column] = pd.to_datetime(filtered_df[check_date_column],
                                                                        format="%Y-%m-%d").dt.strftime("%d:%m:%Y")

                    if not filtered_df.empty:
                        filtered_df.to_csv(dest_file, index=False)
                        with open(dest_file, "r+") as file:
                            file_content = file.read()
                            lines = file_content.split('\n')
                            file_content = '\n'.join(lines[1:])
                            file.seek(0, 0)
                            file.write(f"{first_four_lines}\n{original_header}\n{file_content}")
                    else:
                        print("No matching records found.")

                except Exception as e:
                    print(e)

            def create_tar_file(base_dir, save_path, tar_file_name):
                with tarfile.open(save_path, "w:gz") as tar:
                    tar.add(base_dir, os.path.basename(base_dir))

            def cleanup():
                shutil.rmtree(temp_dir)
                os.remove(save_path)

            # Copy the contents of source_dir to temp_dir
            files_to_process = []

            for root, dirs, files in os.walk(source_dir):

                # Filter remaining datasets based on user's entered criteria
                if not data["download_options"]["aod"]:
                    if "AOD" in dirs:
                        dirs.remove("AOD")

                if not data["download_options"]["sda"]:
                    if "SDA" in dirs:
                        dirs.remove("SDA")

                if not data["download_options"]["lev10"]:
                    files = [file for file in files if not file.endswith("10")]

                if not data["download_options"]["lev15"]:
                    files = [file for file in files if not file.endswith("15")]

                if not data["download_options"]["lev20"]:
                    files = [file for file in files if not file.endswith("20")]

                if not data["download_options"]["series"]:
                    files = [file for file in files if "series" not in file]

                if not data["download_options"]["daily"]:
                    files = [file for file in files if "daily" not in file]

                if not data["download_options"]["all_points"]:
                    files = [file for file in files if "all_points" not in file]

                # ------- end of filtering

                for file in files:
                    if (sites is not None and any(site in file for site in sites)) or any(
                            kf in file for kf in keep_files):
                        source_file = os.path.join(root, file)
                        dest_file = os.path.join(temp_dir, os.path.relpath(source_file, source_dir))
                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                        files_to_process.append((source_file, dest_file, file))

            # Create the temp directory
            os.makedirs(temp_dir, exist_ok=True)

            # Create the concurrent executor
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Create dupe of files that need to be
                futures = [executor.submit(move_accepted_files, file_pair) for file_pair in files_to_process]

                # Process the results as they complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        # print("Task completed successfully:", result)
                    except Exception as e:
                        print("Task encountered an error:", str(e))

            create_tar_file(temp_dir, save_path, tar_file_name)

            with open(save_path, "rb") as file:
                response = HttpResponse(file, content_type="application/x-tar")
                response["Content-Disposition"] = f"attachment; filename=\"{tar_file_name}\""

                # Set CORS headers
                response["Access-Control-Allow-Origin"] = "*"
                response["Access-Control-Allow-Methods"] = "OPTIONS, GET, HEAD, POST"
                response["Access-Control-Allow-Headers"] = "*"

                return response

        except Exception as e:
            print(e)

        finally:
            cleanup()

    if request.method == "OPTIONS":
        try:
            # Validate Post request
            response = HttpResponse()
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "OPTIONS, GET, HEAD, POST"
            response["Access-Control-Allow-Headers"] = "*"

            return response

        except json.decoder.JSONDecodeError:
            return HttpResponse("Invalid JSON data in the request body.")  # sites = data.get("sites", [])
