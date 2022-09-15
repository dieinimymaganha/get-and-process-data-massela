import pandas as pd


class ProcessFiles:
    def __init__(self):
        self.filename_students = 'Alunos.xls'

    def get_list_students(self):
        return pd.read_excel(
            f'files/{self.filename_students}').Nome.to_list()


# a = ProcessFiles()
#
# alunos = a.get_list_students()
# print(alunos)
