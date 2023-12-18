import psycopg2
from os import getenv
from dotenv import load_dotenv

load_dotenv()

host = getenv("LOCALHOST")
user = getenv("MYBOTUSER")
password = getenv("MYPASSWORD")
database = getenv("MYNAMEDB")

def connect():
    return psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )


def close(conn):
    if conn:
        conn.close()


def add_payment(telegram_user_id, unique_payload, amount, currency):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO payments (telegram_user_id, unique_payload, amount, currency, status)
        VALUES (%s, %s, %s, %s, 'Pending')
        """, (telegram_user_id, unique_payload, amount, currency))
        conn.commit()
    finally:
        cursor.close()
        close(conn)


def update_payment_status(unique_payload, status, error_message=None):
    conn = connect()
    cursor = conn.cursor()
    try:
        if error_message:
            cursor.execute("""
            UPDATE payments SET status=%s, error_message=%s WHERE unique_payload=%s
            """, (status, error_message, unique_payload))
        else:
            cursor.execute("""
            UPDATE payments SET status=%s WHERE unique_payload=%s
            """, (status, unique_payload))
        conn.commit()
    finally:
        cursor.close()
        close(conn)