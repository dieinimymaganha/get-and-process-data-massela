from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd


class Integration:

    def __init__(self):
        self._scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self._spreadsheet_id_original = '1htNQMa4PVyKgwIM3hIDL6m4uZLD0LOxJ2bymLNGuBos'
        self._name_sheet = 'Dados treinos'
        self._typeform_first_register_original = f'{self._name_sheet}!A1:B25000'
        self.sheet = None
        self.df = None

    def get_data_frame_sheets(self):
        secret_sheets = {
            "type": "service_account",
            "project_id": "masella",
            "private_key_id": "acf0d6eaff4fa28ed971c72d1e6a32af43703d06",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDWggdZSzFDeJTA\nXdT9gtVHHVnmTi2MRCeOmIJH1BqIskRi67casVWu3E4/v4fzjQh05/khJStvZWbT\nmWgI+tO1NCnu/FQ6vXTUa1h2SdOAKCAciJmqfcL0SUek6TmvcMG82lvaZJICgoNu\nLkalclYStZGUt6vjAVrDkLevkIcZzFF/51EoVJqvA5q7ZwSCSThFYYaYjz2C2Dce\n5O58OppngMIw8L0EgbCFjIJCHFFiG3kCchswfVqSzmrXsGox2G0rsLDAw3bKPexD\nInWXSPyvSaLuau23SC3knVw+cMvjFkqHq+sSwLWVbX73/EzIFO4ym+rsS4PUNedR\njZPPc53tAgMBAAECggEAIVk+RLzaqBNtRtnfpNkMCN4QjaxOSv4Gi1X8/SdFx8Y1\nOQ7N3PXAbSq9dI41l+DvdWNiGSvS7KLeYVu6b5j1RHjbYxbyDl7JdMPKkTtJiSVT\n1rPK9hVOs5VX8NS8feDBEff9qz6S75Z0UfMaUxrrNEXrn+wNKkHZ50kOsZn90v3m\ntPX82whgDhpKH1jMg2mMl9vaeaxrf8JbJZA6JhIrSrVPGIdQnNDkxXpAqOLH/z8z\n0b9QkeFhtsDG+RYgYOK2u3qInInHtR1EvpiUrp0jJMW3Y9MO+bmZprgc8iOW8gjf\nxdG1snLi8TmATFpVKprqTgyXmku20vKKHrqvWLr9UQKBgQDvn2Mt2yil4a4PQ60c\now6hsmdLudkI3AxFGHivHnrO9O7+FY+VEuSk1rXUMGL3/TAHR6IGFJBBym9W6ODh\nNZIYKmVeRoNx/Gzsp0WqehFmvk46nUz47tLjkkEXPKdi5e5IOs9iubXIYYUUMnBy\ngM9NqYHVH25JQREXzOyH/1xPEQKBgQDlKzdm9VOG8LcSLqf9Ao904GQoc73SGpYH\nJTLi6jAZA4lCdk/VpbvI6IID6gbddfMwBvP6rAE1JXMxDpk6BwhTNCeVtlWyNKm5\nZF00QrDBJBw2G7nhCiXFOpdS0ENUqLaSMMirmGON2qGX4eDqV3NvAENrYz14UTed\nlIapheYZHQKBgQDCmVdrOytko8W+ocBpnEZarM7UocaPOl1Ak+IWnZMwlZutfwcP\nErva3n/mJbGKIfUqRFNhyrtooqUPGKrgWqgdtfiCupMvM8el3SZnjyCopu5TDcIf\n+5wKspDn9Rse5wo/YHthet4VMJVp1JibdN5l/L3yvcbL+OqPwJ1qyMhHcQKBgAm0\nHcFvS90f3jCX5ycQb7CcO8F2vSfjVkzxJ0lybxzwCGTXC6RZQy1Low21YBsKfoSf\nFr+bfuWYM1t1acmKOLEFOVPeh5xnHHSsKkInPMLA26zy2ZkMy/Kg+31XMjKofiqM\nhEK3zidYhZUfzF0/3LRrh29JoXWxwrAadOVCtS6FAoGBALILES02/AB5V1ImDYVs\nar8wMAGxoaI6dt0rZmGGh9TXcUuPBjjaKL9GKKxD3HF0g8j36DkQHHGvWBO+98/k\nLHyHISbr2atY1x6+WKIO5SDYNwqf0KfIW1UX2YX33xAebDbH7Hg3OeyY2u/4jWLD\n5c/lD+MCvMxYkb1m/0S7qvsP\n-----END PRIVATE KEY-----\n",
            "client_email": "integration-sheets@masella.iam.gserviceaccount.com",
            "client_id": "104878306504558698861",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/integration-sheets%40masella.iam.gserviceaccount.com"
        }

        creds = service_account.Credentials.from_service_account_info(
            secret_sheets, scopes=self._scopes)
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        self.sheet = service.spreadsheets()
        result = self.sheet.values().get(
            spreadsheetId=self._spreadsheet_id_original,
            range=self._typeform_first_register_original).execute()
        values = result.get('values', [])
        self.df = pd.DataFrame(columns=[values[0]], data=values[1:])


    def ingestion(self):
        lista = [['Teste', 'Teste2']]
        self.sheet.values().update(spreadsheetId=self._spreadsheet_id_original,
                                   range=f'Dados treinos!A1',
                                   valueInputOption="USER_ENTERED", body={
                "values": lista}).execute()


teste = Integration()
teste.get_data_frame_sheets()
teste.ingestion()
