import streamlit as st
import pandas as pd
import sqlite3
from io import StringIO

def init_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

def run_query(conn, query):
    return pd.read_sql_query(query, conn)

st.title('SQL Query Explorer')

# File uploader for SQL database
uploaded_file = st.file_uploader("Upload your SQLite database file", type=['db', 'sqlite', 'sqlite3'])

if uploaded_file is not None:
    # Create a connection to the database
    conn = init_connection()

    # Text area for SQL query input
    query = st.text_area("Enter your SQL query:", height=100)

    if st.button('Run Query'):
        try:
            # Execute query and display results
            results = run_query(conn, query)
            st.write("Query Results:")
            st.dataframe(results)

            # Download results as CSV
            csv = results.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name='query_results.csv',
                mime='text/csv',
            )
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")

    # Close connection
    conn.close()

# Add sidebar with instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload your SQLite database file
2. Enter your SQL query in the text area
3. Click 'Run Query' to execute
4. Download results as CSV if needed
""")
