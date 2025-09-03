import os
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector # <-- Import here

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database
    that is pre-configured to handle the VECTOR type.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
            # Do not use RealDictCursor here, we will apply it per-query
        )
        # THIS IS THE FIX: Register the vector type adapter on the connection
        register_vector(conn)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None