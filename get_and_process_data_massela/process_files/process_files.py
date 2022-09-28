import glob
import os
import json

import numpy as np
import pandas as pd

from sqlalchemy import text

from get_and_process_data_massela.Utils.connection_postgres import \
    ConnectionPostgres


class ProcessFiles:
    def __init__(self, uri_connection):
        self.filename_students = 'Alunos.xls'
        self.connection = ConnectionPostgres.connect(uri_connection)
        self.df_modality = None
        self.df_students_postgresql = None
        self.df_workouts = None

    @staticmethod
    def delete_files():
        dir = 'files'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

    @staticmethod
    def identify_name_and_modality(filename):
        modality = None
        name_student = None
        if 'Musculação' in filename:
            modality = 'Musculação'
            name_student = filename.replace('_Musculação.xls', '')
        if 'Corrida' in filename:
            modality = 'Corrida'
            name_student = filename.replace('_Corrida.xls', '')
        if 'Ciclismo' in filename:
            modality = 'Ciclismo'
            name_student = filename.replace('_Ciclismo.xls', '')
        if 'Natação' in filename:
            modality = 'Natação'
            name_student = filename.replace('_Natação.xls', '')

        name_student = name_student.replace('_', ' ')

        return name_student, modality

    @staticmethod
    def convert_float(value):
        value = str(value)
        value = value.replace('.', '')
        value = value.replace(',', '.')
        try:
            value = float(value)
        except Exception as e:
            value = None
        return value

    @staticmethod
    def convert_to_preferred_format(sec):
        sec = sec % (24 * 3600)
        hour = sec // 3600
        sec %= 3600
        min = sec // 60
        sec %= 60
        return "%02d:%02d:%02d" % (hour, min, sec)

    @staticmethod
    def convert_pace(value):
        value = value.split(':')
        minutes = int(value[0])
        seconds = int(value[1])

        seconds = seconds + (minutes * 60)
        return ProcessFiles.convert_to_preferred_format(seconds)

    @staticmethod
    def convert_date(value):
        try:
            return parse(value)
        except:
            return '1999-01-01'

    def get_list_students(self):
        return pd.read_excel(
            f'files/{self.filename_students}').Nome.to_list()

    def get_list_controller(self):
        file_exists = os.path.exists('controller_download.json')
        df_students = pd.read_excel(
            os.path.join(f'files/{self.filename_students}'))
        df_students.drop(
            ['Telefone', 'CPF', 'RG', 'E-mail', 'Endereço', 'Data Entrada',
             'Tamanho da Camiseta', 'Status', 'Data de Nascimento',
             'Sexo'], axis=1, inplace=True)

        if file_exists:
            alunis = pd.read_json('controller_download.json')
            final = alunis.set_index('Nome').join(
                df_students.set_index('Nome'), how="right").reset_index()
            final = final.replace(np.nan, None)
            json_students = final.to_dict('records')
            with open('controller_download.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(json_students))
            return json_students

        else:
            df_students['Corrida'] = None
            df_students['Ciclismo'] = None
            df_students['Natacao'] = None
            df_students['Musculacao'] = None
            json_students = df_students.to_dict('records')
            with open('controller_download.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(json_students))
            return json_students

    def get_modalitys(self):
        self.df_modality = pd.read_sql('select id_modality as modality_id, '
                                       'description as modality from modality',
                                       con=self.connection.engine)
        self.df_modality.set_index('modality', inplace=True)

    def process_students(self):
        self.df_students = pd.read_excel(os.path.join(os.getcwd(),
                                                      'files/Alunos.xls'))
        self.df_students.drop(
            ['Telefone', 'CPF', 'RG', 'E-mail', 'Endereço', 'Data Entrada',
             'Tamanho da Camiseta', 'Status'], axis=1, inplace=True)
        self.df_students.rename(columns={"Nome": "name", "Sexo": "gender",
                                         "Data de Nascimento": 'birth_date'},
                                inplace=True)
        self.df_students.name = self.df_students.name.apply(lambda x: x.strip())

        self.df_students.birth_date = self.df_students.birth_date.apply(
            lambda x: self.convert_date(x))

        self.upsert_students()

    def upsert_students(self):
        query = text(""" 
                    INSERT INTO students(name, gender, birth_date)
                    VALUES %s
                    ON CONFLICT (name)
                    DO  UPDATE SET name= EXCLUDED.name,
                    gender = EXCLUDED.gender,
                    birth_date = EXCLUDED.birth_date

             """ % ','.join([str(i) for i in list(
            self.df_students.to_records(index=False))]).replace('"', "'"))
        self.connection.engine.execute(query)

    def get_students_postgres(self):
        self.df_students_postgresql = pd.read_sql(
            'select id_student as student_id, '
            'name as name_student '
            'from students',
            con=self.connection.engine)
        self.df_students_postgresql.set_index(
            'name_student', inplace=True)

    def process_workouts(self):
        self.create_data_frame_workouts()
        self.convert_type_columns_workouts()
        self.df_workouts = (
            self.df_workouts.query(
                "proposed_workouts >0 or workouts_done > 0"))

        df_final = self.join_workouts_modality_students()
        self.upsert_workouts(df_final=df_final)

    def create_data_frame_workouts(self):
        list_dfs = []
        local_files = glob.glob(
            f'{os.path.join(os.getcwd(), "files/")}*.xls')
        for file in local_files:
            filename = os.path.basename(file)
            if 'Alunos' not in filename:
                if filename != 'planilha_evolucao.xls':
                    name_student, modality = self.identify_name_and_modality(
                        filename=filename)
                    df = pd.read_excel(file)
                    df.rename(columns={df.columns[0]: "day_1",
                                       df.columns[1]: "training_date",
                                       df.columns[2]: "proposed_workouts",
                                       df.columns[3]: "workouts_done",
                                       df.columns[4]: "proposed_distance",
                                       df.columns[5]: "distance_done",
                                       df.columns[
                                           6]: "avg_distance_per_training",
                                       df.columns[7]: "minimum_proposed_time",
                                       df.columns[8]: "maximum_proposed_time",
                                       df.columns[9]: "time_done",
                                       df.columns[10]: "avg_time_per_training",
                                       df.columns[11]: "avg_speed",
                                       df.columns[12]: "avg_pace",
                                       df.columns[13]: "avg_fc",
                                       df.columns[14]: "accumulated_elevation",
                                       df.columns[15]: "calories",
                                       df.columns[16]: "day_2"
                                       }, inplace=True)
                    df.drop(['day_1', 'day_2', 'proposed_distance',
                             'avg_distance_per_training',
                             'minimum_proposed_time', 'maximum_proposed_time',
                             'avg_time_per_training'], axis=1,
                            inplace=True)
                    df['name_student'] = name_student
                    df['modality'] = modality
                    df = df[:-1]
                    list_dfs.append(df)
        if len(list_dfs) > 1:

            self.df_workouts = pd.concat(list_dfs, ignore_index=True)
            self.df_workouts.sort_values(by=['name_student', 'modality'])
        elif len(list_dfs) == 1:

            self.df_workouts = list_dfs[0]
            self.df_workouts.sort_values(by=['name_student', 'modality'])
        else:
            exit()

    def convert_type_columns_workouts(self):

        self.df_workouts.training_date = pd.to_datetime(
            self.df_workouts['training_date'], format='%d/%m/%Y')
        self.df_workouts.proposed_workouts = (
            self.df_workouts.proposed_workouts.apply(lambda x: int(x)))
        self.df_workouts.workouts_done = self.df_workouts.workouts_done.apply(
            lambda x: int(x))
        self.df_workouts.avg_pace = self.df_workouts.avg_pace.apply(
            lambda x: self.convert_pace(x))

        self.df_workouts.distance_done = (self.df_workouts.
                                          distance_done.
                                          apply(lambda x:
                                                self.convert_float(x)))

        self.df_workouts.avg_speed = (self.df_workouts.
                                      avg_speed.apply(lambda x:
                                                      self.convert_float(x)))
        self.df_workouts.accumulated_elevation = (self.df_workouts.
                                                  accumulated_elevation.
                                                  apply(lambda x:
                                                        self.convert_float(x)))
        self.df_workouts.avg_fc = (
            self.df_workouts.avg_fc.apply(lambda x: int(x)))
        self.df_workouts.calories = (self.df_workouts.
            calories.apply(
            lambda x: self.convert_float(x)))

    def join_workouts_modality_students(self):
        self.get_students_postgres()
        self.df_workouts.set_index('name_student', inplace=True)

        df_final = self.df_students_postgresql.join(self.df_workouts,
                                                    how="inner").reset_index()
        print(self.df_workouts)
        df_final.set_index('modality', inplace=True)

        df_final = df_final.join(self.df_modality, how='inner').reset_index()
        df_final.drop(['modality', 'name_student'], axis=1, inplace=True)
        return df_final

    def upsert_workouts(self, df_final):
        if not df_final.empty:
            query = text(""" 
                        INSERT INTO workouts(student_id, training_date, 
                        proposed_workouts, workouts_done, 
                        distance_done, time_done,
                        avg_speed, avg_pace, avg_fc, accumulated_elevation, 
                        calories, modality_id)
                        VALUES %s
                        ON CONFLICT (modality_id,student_id,training_date)
                        DO  UPDATE SET training_date = excluded.training_date,
                        proposed_workouts  = excluded.proposed_workouts  ,
                        workouts_done = excluded.workouts_done,
                        distance_done = excluded.distance_done,
                        time_done =  excluded.time_done,
                        avg_speed = excluded.avg_speed,
                        avg_pace =  excluded.avg_pace,
                        avg_fc = excluded.avg_fc,
                        accumulated_elevation =excluded.accumulated_elevation,
                        calories = excluded.calories
                 """ % ','.join(
                [str(i) for i in
                 list(df_final.to_records(index=False))]).replace(
                '"', "'"))
            self.connection.engine.execute(query)

    def run_pipeline(self):
        self.get_modalitys()
        self.process_students()
        self.process_workouts()
