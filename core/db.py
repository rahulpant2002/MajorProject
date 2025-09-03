import os
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database
    using credentials from environment variables.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None