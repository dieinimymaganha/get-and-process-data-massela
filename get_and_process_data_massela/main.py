import os
from datetime import datetime

from get_and_process_data_massela.process_files.Process_files import \
    ProcessFiles
from get_and_process_data_massela.webscraping.app_sis_run import AppSisRun

start_time = datetime.now()
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
URL_POSTGRES = os.getenv('URL_POSTGRES')


def download_files(process_files: ProcessFiles):
    run = AppSisRun()
    run.initialize_configuration()
    run.navigate_page_login()
    run.login(email=EMAIL, password=PASSWORD)
    run.get_list_students()
    run.navitegate_page_detail()
    run.download_data_students(list_students=process_files.get_list_students())


def execute_process_files(process_files: ProcessFiles):
    process_files.run_pipeline()


def main_pipeline():
    process_files = ProcessFiles(
        uri_connection=URL_POSTGRES)
    try:
        download_files(process_files=process_files)
    except Exception as e:
        print(f'ERROR DOWNLOAD ------{e}')
    execute_process_files(process_files=process_files)


if __name__ == '__main__':
    main_pipeline()
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
