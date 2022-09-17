import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from get_and_process_data_massela.webscraping import ConfigSelenium
from datetime import date, timedelta

SLEEP = 5

CURRENT_DATE = date.today()
LAST_DATE = CURRENT_DATE - timedelta(days=365)


class AppSisRun(ConfigSelenium):

    def __init__(self):
        super().__init__()
        self.url_home = 'https://appsisrun.com.br/sisrun/login.xhtml'
        self.url_detail = 'https://appsisrun.com.br/sisrun/pages/consulta/analiseTreinos/listaAnaliseTreinos.xhtml'

    def navigate_page_login(self):
        self.driver.get(self.url_home)

        time.sleep(SLEEP)

    def login(self, email, password):
        self.driver.find_element(By.ID, "frmLogin:email").click()
        self.driver.find_element(By.ID, "frmLogin:email").send_keys(
            email)
        time.sleep(SLEEP)
        self.driver.find_element(By.ID, "frmLogin:senha").click()
        self.driver.find_element(By.ID, "frmLogin:senha").send_keys(password)
        time.sleep(SLEEP)
        self.driver.find_element(By.XPATH,
                                 "//span[contains(.,\'Entrar\')]").click()

    def get_list_students(self):
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, ".fa-users").click()
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR,
                                 "#frmConsulta\\3AtabCadastro\\3Aj_idt401 > .ui-button-text").click()

        time.sleep(SLEEP)

    def navitegate_page_detail(self):
        self.driver.get(self.url_detail)
        time.sleep(3)

    def click_modality(self, modality):

        time.sleep(2)
        self.driver.find_element(By.ID,
                                 "frmConsulta:comboFiltroModalidade_input").click()
        self.driver.find_element(By.ID,
                                 "frmConsulta:comboFiltroModalidade_input").clear()
        self.driver.find_element(By.ID,
                                 "frmConsulta:comboFiltroModalidade_input").click()
        time.sleep(1)
        self.driver.find_element(By.ID,
                                 "frmConsulta:comboFiltroModalidade_input").send_keys(
            modality)
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR,
                                 ".ui-autocomplete-item").click()
        time.sleep(1)

    def download_data_students(self, list_students):
        print(f'Total de alunos encontrados: {len(list_students)}')
        for student in list_students:
            print(f'Baixando -- {student}')
            self.select_students(student)

            self.driver.find_element(By.ID,
                                     "frmConsulta:console_label").click()
            time.sleep(SLEEP)
            self.driver.find_element(By.ID, "frmConsulta:console_2").click()
            time.sleep(SLEEP)

            self.driver.find_element(By.ID,
                                     "frmConsulta:filtroDataInicial_input").click()
            time.sleep(2)
            self.driver.find_element(By.ID,
                                     "frmConsulta:filtroDataInicial_input").send_keys(
                self.format_date(LAST_DATE))
            time.sleep(SLEEP)
            self.driver.find_element(By.ID,
                                     "frmConsulta:filtroDataFinal_input").click()
            time.sleep(2)
            self.driver.find_element(By.ID,
                                     "frmConsulta:filtroDataFinal_input").send_keys(
                self.format_date(CURRENT_DATE))
            time.sleep(SLEEP)

            # list_modality = ['Ciclismo']
            list_modality = ['Ciclismo', 'Corrida', 'Musculação', 'Natação']

            for modality in list_modality:
                print(f'Iniciando modalidade --> {modality}')
                self.click_modality(modality=modality)
                self.driver.find_element(By.XPATH,
                                         "//button[@id=\'frmConsulta:botaoConsultar\']/span[2]").click()
                time.sleep(5)
                html = self.driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                time.sleep(3)

                self.driver.find_element(By.XPATH,
                                         "//img[@id=\'frmConsulta:viewGraficos:tablePlanilha:j_idt368\']").click()
                time.sleep(SLEEP)
                self.rename_file(student=student, modality=modality)
                print('--->> Concluido!')

                time.sleep(5)
                html.send_keys(Keys.HOME)

    def select_students(self, student):
        error = True
        while error:
            try:
                time.sleep(2)
                self.driver.find_element(By.ID,
                                         "frmConsulta:comboAluno_input").click()
                time.sleep(1)
                self.driver.find_element(By.ID,
                                         "frmConsulta:comboAluno_input").clear()
                self.driver.find_element(By.ID,
                                         "frmConsulta:comboAluno_input").click()
                self.driver.find_element(By.ID,
                                         "frmConsulta:comboAluno_input").send_keys(
                    student)
                time.sleep(10)
                error = False
            except Exception as e:
                self.driver.refresh()
                time.sleep(5)

    def rename_file(self, student, modality):
        student = student.strip()
        student = student.replace(' ', '_')
        os.rename(os.path.join(os.getcwd(), 'files/planilha_evolucao.xls'),
                  os.path.join(os.getcwd(), f'files/{student}_{modality}.xls'))

    @staticmethod
    def format_date(date):
        return date.strftime("%d/%m/%Y")
