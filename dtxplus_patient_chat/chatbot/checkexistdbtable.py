from django.db import connection
import psycopg
from langchain_postgres import PostgresChatMessageHistory

def create_table_if_not_exists(table_name):
    with connection.cursor() as cursor:
        # Check if the table exists in the database
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            );
        """)
        exists = cursor.fetchone()[0]

        # If the table does not exist, create it
        if not exists:
            PostgresChatMessageHistory.create_tables(connection, table_name)
            print(f"Table '{table_name}' created.")
        else:
            print(f"Table '{table_name}' already exists. Skipping creation.")
