import psycopg2

try:
    connection = psycopg2.connect(
        user="remote_user",
        password="goida52",
        host="188.232.208.215",
        port="5432",
        database="financial_data"
    )

    cursor = connection.cursor()

    cursor.execute("SELECT version();")

    record = cursor.fetchone()
    print("Вы подключены к - ", record, "\n")

except (Exception, psycopg2.Error) as error:
    print("Ошибка при работе с PostgreSQL", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")