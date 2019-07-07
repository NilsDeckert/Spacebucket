import mysql.connector
from mysql.connector import errorcode
login = mysql.connector.connect(         #MySQL login details
        host="188.**.**.***",
        port="3306",
        user="*****63_pi",
        passwd="************",
        database="*****63_test"
)
