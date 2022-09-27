from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os


class ConfigSelenium:

    def __init__(self):
        self.chrome_options = None
        self.driver = None

    def configure_chrome_options(self):
        self.chrome_options = Options()
        user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.114 Safari/537.36")
        # self.chrome_options.headless = True
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument(f'user-agent={user_agent}')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--allow-running-insecure-content')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--verbose')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-software-rasterizer')
        prefs = {
            "download.default_directory": os.path.join(os.getcwd(), 'files')}
        self.chrome_options.add_experimental_option("prefs", prefs)

    def enable_driver(self):
        path = os.path.join(os.getcwd(), 'files')
        self.driver = webdriver.Chrome(options=self.chrome_options,
                                       executable_path='/media/dieinimy/hd_data/MASSELA ASSESSORIA ESPORTIVA LTDA/get-and-process-data-massela/get_and_process_data_massela/webscraping/chromedriver/chromedriver')

    def initialize_configuration(self):
        self.configure_chrome_options()
        self.enable_driver()
