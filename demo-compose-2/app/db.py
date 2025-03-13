import psycopg2
import os
import logging
from psycopg2 import pool
import time

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("PG_DATABASE")

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=5,
    maxconn=10,
    user=PG_USER,
    host=PG_HOST,
    port=PG_PORT,
    password=PG_PASSWORD,
    database=PG_DATABASE
)

def create_table_if_not_exist():
    """Create the predictions table if it does not exist."""
    time.sleep(3)
    conn = None
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                loan_usd FLOAT,
                person_age INT,
                total_income_usd FLOAT,
                has_high_education BOOLEAN,
                has_children BOOLEAN,
                default_probability FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
        logging.info("Table 'predictions' ensured to exist.")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
    finally:
        if conn:
            connection_pool.putconn(conn)

def insert_prediction(loan_usd: float, person_age: int, total_income_usd: float,
                      has_high_education: bool, has_children: bool,
                      default_probability: float):
    """
    Insert a new prediction into the predictions table.
    Returns the ID of the inserted row.
    """
    conn = None
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()
        insert_sql = """
            INSERT INTO predictions 
            (loan_usd, person_age, total_income_usd, has_high_education, has_children, default_probability)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cur.execute(insert_sql, (loan_usd, person_age, total_income_usd,
                                 has_high_education, has_children, default_probability))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        logging.info(f"Inserted prediction with id {inserted_id}.")
        return inserted_id
    except Exception as e:
        logging.error(f"Error inserting prediction: {e}")
        return None
    finally:
        if conn:
            connection_pool.putconn(conn)

def read_all_predictions():
    """
    Read all predictions from the table.
    Returns a list of dictionaries containing the prediction data.
    """
    conn = None
    predictions = []
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT id, loan_usd, person_age, total_income_usd, has_high_education, has_children, default_probability, created_at FROM predictions ORDER BY created_at DESC;")
        rows = cur.fetchall()
        for row in rows:
            prediction = {
                "id": row[0],
                "loan_usd": row[1],
                "person_age": row[2],
                "total_income_usd": row[3],
                "has_high_education": row[4],
                "has_children": row[5],
                "default_probability": row[6],
                "created_at": row[7].isoformat() if row[7] else None
            }
            predictions.append(prediction)
        cur.close()
        logging.info("Fetched all predictions from the database.")
        return predictions
    except Exception as e:
        logging.error(f"Error reading predictions: {e}")
        return predictions
    finally:
        if conn:
            connection_pool.putconn(conn)
