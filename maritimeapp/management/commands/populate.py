import concurrent.futures
from multiprocessing import Pool
from datetime import datetime
from django.contrib.gis.geos import Point
import io
import re
import numpy as np

import tarfile
import requests
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSException
from rest_framework.exceptions import ValidationError
from maritimeapp.models import *
from django.contrib.gis.geos import Point
import pandas as pd

NUM_WORKERS = 5

format_one = [
    'all_points.lev10',
    'all_points.lev15',
    'all_points.lev20',
]
format_two = [
    'daily.lev15',
    'daily.lev20',
    'series.lev15',
    'series.lev20',
]
format_three = [

]


class Command(BaseCommand):
    help = 'Download and process file from static URL'

    def validate_data(self, row_fields, row, type):
        if type is float:
            for field_name in row_fields:
                field_value = getattr(row, field_name)
                if not isinstance(field_value, float) and not isinstance(field_value, np.float64):
                    raise ValidationError(f'{field_name} must be a number')
                else:
                    print("RAN SUCCESSFULLY")
                    return True

    def process_chunk(self, chunk, filetype, site, file):
        # print(chunk.head(10))
        # print(filetype)


        if filetype in format_one:
            pass



        if filetype in format_two:
            # print('running')
            # print('running')
            # site_measurements_list = []
            # Process the data in the chunk as needed
            model_classes = {
                format_two[0]: SiteMeasurementsSeries15,
                format_two[1]: SiteMeasurementsSeries20,
                format_two[2]: SiteMeasurementsDaily15,
                format_two[3]: SiteMeasurementsDaily20,
            }
            model = model_classes[filetype]
            for index, row in chunk.iterrows():
                # print(file)
                # print(row)
                latlng = Point(float(row['Longitude']), float(row['Latitude']))
                date_str = row['Date(dd:mm:yyyy)'].split(':')
                date = f'{date_str[2]}-{date_str[1]}-{date_str[0]}'

                # date = datetime.strptime(date_str + ' ' + time_str, '%d:%m:%Y %H:%M:%S')
                last_processing = row['Last_Processing_Date(dd:mm:yyyy)'].split(':')
                last_processing_date = f'{last_processing[2]}-{last_processing[1]}-{last_processing[0]}'
                print(model)
                # print(site_measurement, file)
                float_fields = [
                    'air_mass', 'aod_340nm', 'aod_380nm', 'aod_440nm', 'aod_500nm',
                    'aod_675nm', 'aod_870nm', 'aod_1020nm', 'aod_1640nm', 'water_vapor',
                    'angstrom_exponent_440_870', 'std_340nm', 'std_380nm', 'std_440nm',
                    'std_500nm', 'std_675nm', 'std_870nm', 'std_1020nm', 'std_1640nm', 'std_water_vapor',
                    'std_angstrom_exponent_440_870'
                ]
                row_floats = ['Air Mass', 'AOD_340nm', 'AOD_380nm', 'AOD_440nm', 'AOD_500nm', 'AOD_675nm', 'AOD_870nm',
                              'AOD_1020nm', 'AOD_1640nm', 'Water Vapor(cm)', 'STD_340nm', 'STD_380nm', 'STD_440nm',
                              'STD_500nm', 'STD_675nm', 'STD_870nm', 'STD_1020nm', 'STD_1640nm', 'STD_Water_Vapor(cm)',
                              'Longitude', 'Latitude']

                data_validated = self.validate_data(row_floats, row, float)
                print(data_validated)
                if data_validated:
                    print("OBJECT PUT INTO DB")
                    site_obj, created = Site.objects.get_or_create(name=site, description='')
                    model_classes[filetype].objects.get_or_create(
                        site=site_obj,
                        date=date,
                        time=row['Time(hh:mm:ss)'],
                        air_mass=float(row['Air Mass']),
                        latlng=latlng,
                        aod_340nm=float(row['AOD_340nm']),
                        aod_380nm=float(row['AOD_380nm']),
                        aod_440nm=float(row['AOD_440nm']),
                        aod_500nm=float(row['AOD_500nm']),
                        aod_675nm=float(row['AOD_675nm']),
                        aod_870nm=float(row['AOD_870nm']),
                        aod_1020nm=float(row['AOD_1020nm']),
                        aod_1640nm=float(row['AOD_1640nm']),
                        water_vapor=float(row['Water Vapor(cm)']),
                        angstrom_exponent_440_870=float(row['440-870nm_Angstrom_Exponent']),
                        std_340nm=float(row['STD_340nm']),
                        std_380nm=float(row['STD_380nm']),
                        std_440nm=float(row['STD_440nm']),
                        std_500nm=float(row['STD_500nm']),
                        std_675nm=float(row['STD_675nm']),
                        std_870nm=float(row['STD_870nm']),
                        std_1020nm=float(row['STD_1020nm']),
                        std_1640nm=float(row['STD_1640nm']),
                        std_water_vapor=float(row['STD_Water_Vapor(cm)']),
                        std_angstrom_exponent_440_870=float(row['STD_440-870nm_Angstrom_Exponent']),
                        num_observations=int(row['Number_of_Observations']),
                        last_processing_date=last_processing_date,
                        aeronet_number=int(row['AERONET_Number']),
                        microtops_number=int(row['Microtops_Number']))
                else:
                    print("NO ITEMS IN DB")
                # print(site_measurements_list)

            # Do something with the value...
            # print(model)

    def process_file(self, args):
        member = args[0]
        lev_file = args[1]
        file_name = args[2]
        file_type = args[3]
        site = re.sub(r'[_-]\d+', '', file_name.split('/')[1])[:-1]
        chunk_size = 50
        # version, name_file_type, disclaimer, authors_contact, headers = lines[:5]
        # with open(lev_file, 'r', encoding='ISO-8859-1') as f:
        #     next(f)  # skip the first 4 rows (header)
        reader = pd.read_csv(lev_file, nrows=chunk_size, skiprows=4, header=0, chunksize=chunk_size,
                             encoding='latin-1')
        # for row in reader:
        # print(row)
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = [executor.submit(self.process_chunk, chunk, file_type, site, file_name) for chunk in reader]
            concurrent.futures.wait(futures)
            # print("HELLOW WORLD")
        # print(start_index)
        # if file_type in format_one:
        #     for i, line in enumerate(lines[start_index:]):
        #         fields = line.strip().split(',')
        #         if len(fields) == 18:
        #             (
        #                 date,
        #                 time,
        #                 air_mass,
        #                 lat, lng,
        #                 aod_340nm,
        #                 aod_380nm,
        #                 aod_440nm,
        #                 aod_500nm,
        #                 aod_675nm,
        #                 aod_870nm,
        #                 aod_1020nm,
        #                 aod_1640nm,
        #                 water_vapor,
        #                 angstrom_exponent,
        #                 last_processing_date,
        #                 aeronet_number,
        #                 microtops_number
        #             ) = line.split(',')
        #
        #             date = date.split(':')
        #             date = f'{date[2]}-{date[1]}-{date[0]}'
        #             last_processing_date = last_processing_date.split(':')
        #             last_processing_date = f'{last_processing_date[2]}-{last_processing_date[1]}-{last_processing_date[0]}'
        #             try:
        #                 site_obj, created = Site.objects.get_or_create(name=site, description='')
        #                 if created:
        #                     print(f"Created new site: {site_obj}")
        #
        #                 latlng = Point(float(lng), float(lat))
        #                 model_classes = {
        #                     format_one[0]: SiteMeasurementsAllPoints10,
        #                     format_one[1]: SiteMeasurementsAllPoints15,
        #                     format_one[2]: SiteMeasurementsAllPoints20,
        #                 }
        #
        #                 site_measurements_obj, created = model_classes[file_type].objects.get_or_create(
        #                     site=site_obj,
        #                     date=date,
        #                     time=time,
        #                     air_mass=float(air_mass),
        #                     latlng=latlng,
        #                     aod_340nm=float(aod_340nm),
        #                     aod_380nm=float(aod_380nm),
        #                     aod_440nm=float(aod_440nm),
        #                     aod_500nm=float(aod_500nm),
        #                     aod_675nm=float(aod_675nm),
        #                     aod_870nm=float(aod_870nm),
        #                     aod_1020nm=float(aod_1020nm),
        #                     aod_1640nm=float(aod_1640nm),
        #                     water_vapor=float(water_vapor),
        #                     angstrom_exponent=float(angstrom_exponent),
        #                     last_processing_date=last_processing_date,
        #                     aeronet_number=int(aeronet_number),
        #                     microtops_number=int(microtops_number)
        #                 )
        #                 if created:
        #                     print(f"Created new site measurement: {site_measurements_obj}")
        #             except (GEOSException, ValueError) as e:
        #                 print(f"Error creating SiteMeasurementsAllPoints10 object: {e}")
        #                 raise ValidationError("Invalid geometry provided.")
        #
        # if file_type in format_two:
        #     for i, line in enumerate(lines[start_index:]):
        #         (
        #             date,
        #             time,
        #             air_mass,
        #             latitude,
        #             longitude,
        #             aod_340nm,
        #             aod_380nm,
        #             aod_440nm,
        #             aod_500nm,
        #             aod_675nm,
        #             aod_870nm,
        #             aod_1020nm,
        #             aod_1640nm,
        #             water_vapor,
        #             angstrom_exponent,
        #             std_340nm,
        #             std_380nm,
        #             std_440nm,
        #             std_500nm,
        #             std_675nm,
        #             std_870nm,
        #             std_1020nm,
        #             std_1640nm,
        #             std_water_vapor,
        #             std_angstrom_exponent,
        #             number_of_observations,
        #             last_processing_date,
        #             aeronet_number,
        #             microtops_number,
        #         ) = line.split(',')
        #         print(date,
        #               time,
        #               air_mass,
        #               latitude,
        #               longitude,
        #               aod_340nm,
        #               aod_380nm,
        #               aod_440nm,
        #               aod_500nm,
        #               aod_675nm,
        #               aod_870nm,
        #               aod_1020nm,
        #               aod_1640nm,
        #               water_vapor,
        #               angstrom_exponent,
        #               std_340nm,
        #               std_380nm,
        #               std_440nm,
        #               std_500nm,
        #               std_675nm,
        #               std_870nm,
        #               std_1020nm,
        #               std_1640nm,
        #               std_water_vapor,
        #               std_angstrom_exponent,
        #               number_of_observations,
        #               last_processing_date,
        #               aeronet_number,
        #               microtops_number)

        #
        # x = ['29:01:2016', '14:52:34', '1.778074', '-70.510600', '-8.180200', '-999.000000', '0.043827',
        #      '0.039175',
        #      '0.031645', '0.022100', '0.021680', '-999.000000', '-999.000000', '-999.000000', '0.922785',
        #      '0.000000', '0.009605', '0.007698', '0.005012', '0.002449', '0.002369', '4990005.000000',
        #      '4990005.000000', '0.000000', '0.185696', '5', '21:06:2019', '893', '19749']
        # date = date.split(':')
        # date = f'{date[2]}-{date[1]}-{date[0]}'
        # last_processing_date = last_processing_date.split(':')
        # last_processing_date = f'{last_processing_date[2]}-{last_processing_date[1]}-{last_processing_date[0]}'
        # try:
        #     site_obj, created = Site.objects.get_or_create(name=site, description='')
        #     if created:
        #         print(f"Created new site: {site_obj}")
        #     print(longitude)
        #     latlng = Point(float(longitude), float(latitude))
        #     model_classes = {
        #         format_two[0]: SiteMeasurementsSeries15,
        #         format_two[1]: SiteMeasurementsSeries20,
        #         format_two[2]: SiteMeasurementsDaily15,
        #         format_two[3]: SiteMeasurementsDaily20,
        #     }
        #     site_measurements_obj, created = model_classes[file_type].objects.get_or_create(
        #         site=site_obj,
        #         date=date,
        #         time=time,
        #         air_mass=float(air_mass),
        #         latlng=latlng,
        #         aod_340nm=float(aod_340nm),
        #         aod_380nm=float(aod_380nm),
        #         aod_440nm=float(aod_440nm),
        #         aod_500nm=float(aod_500nm),
        #         aod_675nm=float(aod_675nm),
        #         aod_870nm=float(aod_870nm),
        #         aod_1020nm=float(aod_1020nm),
        #         aod_1640nm=float(aod_1640nm),
        #         water_vapor=float(water_vapor),
        #         angstrom_exponent_440_870=float(angstrom_exponent),
        #         std_340nm=float(std_340nm),
        #         std_380nm=float(std_380nm),
        #         std_440nm=float(std_440nm),
        #         std_500nm=float(std_500nm),
        #         std_675nm=float(std_675nm),
        #         std_870nm=float(std_870nm),
        #         std_1020nm=float(std_1020nm),
        #         std_1640nm=float(std_1640nm),
        #         std_water_vapor=float(std_water_vapor),
        #         std_angstrom_exponent_440_870=float(std_angstrom_exponent),
        #         num_observations=float(number_of_observations),
        #         last_processing_date=last_processing_date,
        #         aeronet_number=int(aeronet_number),
        #         microtops_number=int(microtops_number)
        #     )
        #     if created:
        #         print(f"Created new site measurement: {site_measurements_obj}")
        # except (GEOSException, ValueError) as e:
        #     print(f"Error creating SiteMeasurementsDaily15 object: {e}")
        #     raise ValidationError("Invalid geometry provided.")

        # except Exception as e:
        #     print(e)
        #     print(i)
        #     print(line.split(','))
        #     print(len(line.split(',')))
        #     print(len(line.split(',')))
        #     print(file_type)

    def handle(self, *args, **options):

        file_endings = [
            'all_points.lev10',
            'all_points.lev15',
            'all_points.lev20',
            'series.lev15',
            'series.lev20',
            'daily.lev15',
            'daily.lev20',

        ]
        # Download the file from the static URL
        url = 'https://aeronet.gsfc.nasa.gov/new_web/All_MAN_Data_V3.tar.gz'
        response = requests.get(url)
        tar_contents = response.content
        # Extract the contents of the .tar.gz file
        with tarfile.open(fileobj=io.BytesIO(tar_contents)) as tar:
            # Process each CSV file in parallel using a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                # Submit the CSV files to the thread pool for processing
                futures = []
                for member in tar.getmembers():
                    if member.isfile() and member.name.endswith(file_endings[0]):
                        file_name = member.name[:-len(file_endings[0])]
                        print(f"Submitting file {file_name} to thread pool")
                        futures.append(executor.submit(self.process_lev, (member, tar, file_name, file_endings[0])))
                    if member.isfile() and member.name.endswith(file_endings[1]):
                        file_name = member.name[:-len(file_endings[1])]
                        print(f"Submitting file {file_name} to thread pool")
                        futures.append(executor.submit(self.process_lev, (member, tar, file_name, file_endings[1])))
                    if member.isfile() and member.name.endswith(file_endings[2]):
                        file_name = member.name[:-len(file_endings[2])]
                        print(f"Submitting file {file_name} to thread pool")
                        futures.append(executor.submit(self.process_lev, (member, tar, file_name, file_endings[2])))
                    # if member.isfile() and member.name.endswith(file_endings[3]):
                    #     lev_file = tar.extractfile(member)
                    #
                    #     file_name = member.name[:-len(file_endings[3])]
                    #     print(f"Submitting file {file_name} to thread pool")
                    #     futures.append(
                    #         executor.submit(self.process_file, (member, lev_file, file_name, file_endings[3])))
                    # if member.isfile() and member.name.endswith(file_endings[4]):
                    #     lev_file = tar.extractfile(member)
                    #
                    #     file_name = member.name[:-len(file_endings[4])]
                    #     print(f"Submitting file {file_name} to thread pool")
                    #     futures.append(
                    #         executor.submit(self.process_file, (member, lev_file, file_name, file_endings[4])))
                    if member.isfile() and member.name.endswith(file_endings[5]):
                        lev_file = tar.extractfile(member)

                        file_name = member.name[:-len(file_endings[5])]
                        print(f"Submitting file {file_name} to thread pool")
                        futures.append(
                            executor.submit(self.process_file, (member, lev_file, file_name, file_endings[5])))
                    if member.isfile() and member.name.endswith(file_endings[6]):
                        lev_file = tar.extractfile(member)
                        file_name = member.name[:-len(file_endings[6])]
                        print(f"Submitting file {file_name} to thread pool")
                        futures.append(
                            executor.submit(self.process_file, (member, lev_file, file_name, file_endings[6])))
                # Wait for all futures to finish
                for future in concurrent.futures.as_completed(futures):
                    try:
                        # print("STARTING")
                        future.result()
                        # print("STOPPING")
                    except Exception as exc:
                        print(f"Exception occurred: {exc}")

        # pool.close()
        # pool.join()  # print(line)
        # file_name = member.name.split('/')[-1]
        # Get or create the Site object for the current site name
        #                 site, created = Site.objects.get_or_create(name=site_name)
        #                 # Create a new MyModel instance with the Site object
        #                 obj, created = Site.objects.get_or_create(name=site_name, description="")
        #                 if not created:
        #
        # SiteMeasurementsAllPoints10.objects.get_or_create(site=site_name, file_name=file_name, file_content=line)
        #
        #         if member.isfile() and member.name.endswith('.lev15'):
        #             csv_file = tar.extractfile(member)
        #             csv_contents = csv_file.read()
        #             # Split the CSV contents into lines
        #             lines = csv_contents.decode('utf-8').splitlines()
        #             # Get the site name from the CSV file name
        #             site_name = member.name.split('/')[0]
        #             # Create a new MyModel instance for each line in the CSV file
        #             for line in lines:
        #                 file_name = member.name.split('/')[-1]
        #                 # Get or create the Site object for the current site name
        #                 site, created = Site.objects.get_or_create(name=site_name)
        #                 # Create a new MyModel instance with the Site object
        #                 MyModel.objects.create(site=site, file_name=file_name, file_content=line)
        #
        #         if member.isfile() and member.name.endswith('.lev20'):
        #             csv_file = tar.extractfile(member)
        #             csv_contents = csv_file.read()
        #             # Split the CSV contents into lines
        #             lines = csv_contents.decode('utf-8').splitlines()
        #             # Get the site name from the CSV file name
        #             site_name = member.name.split('/')[0]
        #             # Create a new MyModel instance for each line in the CSV file
        #             for line in lines:
        #                 file_name = member.name.split('/')[-1]
        #                 # Get or create the Site object for the current site name
        #                 site, created = Site.objects.get_or_create(name=site_name)
        #                 # Create a new MyModel instance with the Site object
        #                 MyModel.objects.create(site=site, file_name=file_name, file_content=line)
