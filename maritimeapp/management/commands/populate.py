import concurrent.futures
import logging
import os
import io
import numpy as np
import tarfile
import requests
from django.core.management.base import BaseCommand
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
# format_three = [
#
# ]


class Command(BaseCommand):
    help = 'Download and process file from static URL'

    @classmethod
    def validate_data(cls, row_fields, row, type_of_data):
        if type_of_data is float:
            for field_name in row_fields:
                field_value = getattr(row, field_name)
                if not isinstance(field_value, float) and not isinstance(field_value, np.float64):
                    raise ValidationError(f'{field_name} must be a number')
                elif np.isnan(field_value):
                    raise ValidationError(f'{field_name} cannot be NaN')
            print("RAN SUCCESSFULLY")
            return True

    @classmethod
    def process_chunk(cls, chunk, filetype, site, file):
        if filetype in format_two:

            model_classes = {
                format_two[0]: SiteMeasurementsDaily15,
                format_two[1]: SiteMeasurementsDaily20,
            }
            model = model_classes[filetype]
            # print(model, site)
            daily_header = ['Date(dd:mm:yyyy)', 'Time(hh:mm:ss)', 'Air Mass', 'Latitude', 'Longitude', 'AOD_340nm',
                            'AOD_380nm', 'AOD_440nm', 'AOD_500nm', 'AOD_675nm', 'AOD_870nm', 'AOD_1020nm',
                            'AOD_1640nm', 'Water Vapor(cm)', '440-870nm_Angstrom_Exponent', 'STD_340nm',
                            'STD_380nm', 'STD_440nm', 'STD_500nm', 'STD_675nm', 'STD_870nm', 'STD_1020nm',
                            'STD_1640nm', 'STD_Water_Vapor(cm)', 'STD_440-870nm_Angstrom_Exponent',
                            'Number_of_Observations', 'Last_Processing_Date(dd:mm:yyyy)', 'AERONET_Number',
                            'Microtops_Number']
            chunk.columns = daily_header
            for index, row in chunk.iterrows():
                print(row)
                try:
                    full_file_name = file+filetype

                    latlng = Point(float(row['Longitude']), float(row['Latitude']))
                    date_str = row['Date(dd:mm:yyyy)'].split(':')
                    date = f'{date_str[2]}-{date_str[1]}-{date_str[0]}'

                    # date = datetime.strptime(date_str + ' ' + time_str, '%d:%m:%Y %H:%M:%S')
                    last_processing = row['Last_Processing_Date(dd:mm:yyyy)'].split(':')
                    last_processing_date = f'{last_processing[2]}-{last_processing[1]}-{last_processing[0]}'

                    row_floats = ['Air Mass', 'Latitude', 'Longitude', 'AOD_340nm',
                                  'AOD_380nm', 'AOD_440nm', 'AOD_500nm', 'AOD_675nm', 'AOD_870nm', 'AOD_1020nm',
                                  'AOD_1640nm', 'Water Vapor(cm)', '440-870nm_Angstrom_Exponent', 'STD_340nm',
                                  'STD_380nm', 'STD_440nm', 'STD_500nm', 'STD_675nm', 'STD_870nm', 'STD_1020nm',
                                  'STD_1640nm', 'STD_Water_Vapor(cm)', 'STD_440-870nm_Angstrom_Exponent']

                    data_validated = cls.validate_data(row_floats, row, float)
                    print(data_validated)
                    if data_validated:
                        site_obj, created = Site.objects.get_or_create(name=site, description='')
                        model_classes[filetype].objects.get_or_create(
                            site=site_obj,
                            filename=full_file_name,
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

                except Exception as e:
                    print("Error on ", index)
                    print(row)
                    print(e)

    def process_file(self, args):
        member = args[0]
        lev_file = args[1]
        file_name = args[2]
        file_type = args[3]

        print('FILENAME: ', file_name)
        site = None
        try:
            site = file_name
            if site.endswith('_'):
                site = site.rstrip('_')

        except Exception as e:
            print("Site Name change error occured", e)

        chunk_size = 50

        reader = pd.read_csv(lev_file, nrows=chunk_size, skiprows=5, header=None, chunksize=chunk_size,
                             encoding='latin-1')

        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = [executor.submit(self.process_chunk, chunk, file_type, site, file_name) for chunk in reader]
            concurrent.futures.wait(futures)

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
        with tarfile.open(fileobj=io.BytesIO(tar_contents), mode='r:gz') as tar:
            tar.extractall(path=r'D:\DevOps\Active\mandatabase\SRC')
            # logging.log("Download Completed")

        # Read the folder contents
        folder_path = r'D:\DevOps\Active\mandatabase\SRC'
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = []
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:

                    # Insert/Update Daily Level 15
                    if file_name.endswith(file_endings[4]):
                        # print(file_name)
                        file_path = os.path.join(root, file_name)
                        file_name = file_name[:-len(file_endings[4])]
                        print(f"Submitting file {file_name} to thread pool")
                        futures.append(
                            executor.submit(self.process_file, (file_path, file_path, file_name, file_endings[4]))
                        )

                    # Insert/Update Daily Level 20
                    if file_name.endswith(file_endings[5]):
                        # print(file_name)
                        file_path = os.path.join(root, file_name)
                        file_name = file_name[:-len(file_endings[5])]
                        print(f"Submitting file {file_name} to thread pool")
                        futures.append(
                            executor.submit(self.process_file, (file_path, file_path, file_name, file_endings[5]))
                        )

            # Wait for all futures to finish
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print(f"Exception occurred: {exc}")
