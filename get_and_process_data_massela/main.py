from get_and_process_data_massela.process_files.Process_files import \
    ProcessFiles
from get_and_process_data_massela.webscraping.app_sis_run import AppSisRun


def main():
    process_files = ProcessFiles()
    run = AppSisRun()
    run.initialize_configuration()
    run.navigate_page_login()
    run.login()
    run.get_list_students()
    run.navitegate_page_detail()
    run.download_data_students(list_students=process_files.get_list_students())


main()
