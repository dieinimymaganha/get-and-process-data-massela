import json
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from get_and_process_data_massela.webscraping import ConfigSelenium

SLEEP = 5


class AppSisRun(ConfigSelenium):

    def __init__(self, current_date, last_date):
        super().__init__()
        self.url_home = 'https://appsisrun.com.br/sisrun/login.xhtml'
        self.url_detail = 'https://appsisrun.com.br/sisrun/pages/consulta/analiseTreinos/listaAnaliseTreinos.xhtml'
        self.students = None
        self.current_date = current_date
        self.last_date = last_date

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

    def download_list_students(self):
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, "#formGrafico\\3Aj_idt449_content img").click()
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, "#frmConsulta\\3AtabCadastro\\3Aj_idt403 > .ui-button-text").click()

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

    def download_data_students(self, list_students, active_modality):
        self.students = list_students
        print(f'Total de alunos encontrados: {len(list_students)}')

        for pos, student in enumerate(list_students):
            list_modality = []
            if student['Corrida'] != str(
                    self.current_date) and 'Corrida' in active_modality:
                list_modality.append('Corrida')
            if student['Ciclismo'] != str(
                    self.current_date) and 'Ciclismo' in active_modality:
                list_modality.append('Ciclismo')
            if student['Natacao'] != str(
                    self.current_date) and 'Natação' in active_modality:
                list_modality.append('Natação')
            if student['Musculacao'] != str(
                    self.current_date) and 'Musculação' in active_modality:
                list_modality.append('Musculação')
            if list_modality:
                print(f'LISTA DE MODALIDADES{list_modality}')
                self.select_students(student["Nome"])
                try:
                    self.driver.find_element(By.CSS_SELECTOR,
                                             ".ui-autocomplete-item").click()
                except Exception as e:
                    if 'Message: element not interactable' not in str(e):
                        print(f'DEU ERRO {e}')
                        continue
                self.driver.find_element(By.ID,
                                         "frmConsulta:console_label").click()
                time.sleep(SLEEP)
                self.driver.find_element(By.ID,
                                         "frmConsulta:console_2").click()
                time.sleep(SLEEP)

                self.driver.find_element(By.ID,
                                         "frmConsulta:filtroDataInicial_input").click()
                time.sleep(2)
                self.driver.find_element(By.ID,
                                         "frmConsulta:filtroDataInicial_input").send_keys(
                    self.format_date(self.last_date))
                time.sleep(SLEEP)
                self.driver.find_element(By.ID,
                                         "frmConsulta:filtroDataFinal_input").click()
                time.sleep(2)
                self.driver.find_element(By.ID,
                                         "frmConsulta:filtroDataFinal_input").send_keys(
                    self.format_date(self.current_date))
                time.sleep(SLEEP)

                for modality in list_modality:
                    print(f'Iniciando modalidade --> {modality}')
                    self.click_modality(modality=modality)
                    self.driver.find_element(By.XPATH,
                                             "//button[@id=\'frmConsulta:botaoConsultar\']/span[2]").click()

                    time.sleep(5)
                    html = self.driver.find_element_by_tag_name('html')
                    html.send_keys(Keys.END)
                    count_click_download = 0
                    while count_click_download <= 5:
                        try:
                            self.driver.find_element(By.ID,
                                                     "frmConsulta:viewGraficos:tablePlanilha:j_idt370").click()
                            break
                        except Exception as e:
                            print(f'ERRO CLICK ---::>>> {e}')
                            count_click_download += 1
                    time.sleep(5)
                    self.rename_file(student=student['Nome'],
                                     modality=modality)

                    print('--->> Concluido!')
                    if modality == 'Ciclismo':
                        student.update({'Ciclismo': str(self.current_date)})
                    if modality == 'Corrida':
                        student.update({'Corrida': str(self.current_date)})
                    if modality == 'Natação':
                        student.update({'Natacao': str(self.current_date)})
                    if modality == 'Musculação':
                        student.update({'Musculacao': str(self.current_date)})
                    self.students[pos] = student
                    with open('controller_download.json', 'w',
                              encoding='utf-8') as f:
                        f.write(json.dumps(self.students))
                    time.sleep(5)
                    html.send_keys(Keys.HOME)

    def select_students(self, student):
        # student = 'Adalberto Bernardo Carvalho'
        print(f'Baixando -- {student}')
        error = True
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

    def rename_file(self, student, modality):
        student = student.strip()
        student = student.replace(' ', '_')
        os.rename(os.path.join(os.getcwd(), 'files/planilha_evolucao.xls'),
                  os.path.join(os.getcwd(), f'files/{student}_{modality}.xls'))

    @staticmethod
    def format_date(date):
        return date.strftime("%d/%m/%Y")
