from Utils.connection_postgres import ConnectionPostgres
from dateutil.parser import parse
from datetime import timedelta


class Utils:

    @staticmethod
    def create_connection(connection):
        return ConnectionPostgres.connect(
            f"postgresql+psycopg2://{connection.login}:{connection.password}@{connection.host}/{connection.schema}"
        )

    @staticmethod
    def str_format(value):
        if len(value.strip()) == 0:
            return None
        else:
            return value.strip()

    @staticmethod
    def format_date(value):
        value = parse(value)
        value = value - timedelta(hours=3)
        return value.strftime('%Y-%m-%d')

    @staticmethod
    def format_date_time(value):
        value = parse(value)
        value = value - timedelta(hours=3)
        return value.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def format_time(value):
        value = parse(value)
        return value.strftime('%H:%M:%S')
