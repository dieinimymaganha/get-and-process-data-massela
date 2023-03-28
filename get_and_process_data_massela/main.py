import os
import time
from datetime import datetime

from get_and_process_data_massela.process_files.process_files import \
    ProcessFiles
from get_and_process_data_massela.webscraping.app_sis_run import AppSisRun

start_time = datetime.now()
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
URL_POSTGRES = os.getenv('URL_POSTGRES')

# Opções de Download 'Natação', 'Ciclismo', 'Musculação', 'Corrida'
ACTIVE_MODALITYS = ['Musculação', 'Corrida']

from datetime import date, timedelta

CURRENT_DATE = date.today()
LAST_DATE = CURRENT_DATE - timedelta(days=1825)


def download_files(process_files: ProcessFiles):
    count = 0

    while count <= 500:
        run = AppSisRun(current_date=CURRENT_DATE, last_date=LAST_DATE)
        try:
            run.initialize_configuration()
            run.navigate_page_login()
            run.login(email=EMAIL, password=PASSWORD)
            run.download_list_students()
            json_students = process_files.get_list_controller()
            run.navitegate_page_detail()
            run.download_data_students(list_students=json_students,
                                       active_modality=ACTIVE_MODALITYS)
            break
        except Exception as e:
            print(f'ERROR ---> {e}')
            run.driver.quit()
            count += 1


def execute_process_files(process_files: ProcessFiles):
    process_files.run_pipeline()


def main_pipeline():
    process_files = ProcessFiles(
        uri_connection=URL_POSTGRES)
    # process_files.delete_files()
    download_files(process_files=process_files)
    # execute_process_files(process_files=process_files)


if __name__ == '__main__':
    main_pipeline()
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
