# # backend/db.py

# import mysql.connector
# from mysql.connector import Error

# def get_connection():
#     try:
#         connection = mysql.connector.connect(
#             host='rdbs-step4-south-india.mysql.database.azure.com',
#             user='tech0sql1',
#             password='step4pos-5', 
#             database='step4pos',
#             ssl_ca='/Users/~/Downloads/DigiCertGlobalRootCA.crt.pem' #あってるか要確認
#         )
#         return connection
#     except Error as e:
#         print(f"DB接続エラー: {e}")
#         return None

from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error

# .env 読み込み
load_dotenv()

# .env から環境変数取得
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SSL_CA = os.getenv('DB_SSL_CA')

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            ssl_ca=DB_SSL_CA
        )
        return connection
    except Error as e:
        print(f"DB接続エラー: {e}")
        return None
