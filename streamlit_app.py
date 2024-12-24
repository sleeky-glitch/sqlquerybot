import streamlit as st
import pandas as pd
import sqlite3

def execute_sql_file(conn, sql_file):
    """
    Execute SQL commands from a .sql file.
    """
    try:
        with open(sql_file, 'r') as file:
            sql_script = file.read()
        conn.executescript(sql_script)
        st.success("SQL file executed successfully!")
    except Exception as e:
        st.error(f"Error executing SQL file: {e}")

def run_query(conn, query):
    """
    Run a SQL query and return the results as a DataFrame.
    """
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None

# Streamlit app
st.title("SQL Query Explorer")

# File uploader for SQLite database
uploaded_db = st.file_uploader("Upload your SQLite database file", type=['db', 'sqlite', 'sqlite3'])

# File uploader for SQL file
uploaded_sql = st.file_uploader("Upload your SQL file", type=['sql'])

if uploaded_db:
    # Create a connection to the uploaded SQLite database
    conn = sqlite3.connect(uploaded_db.name)

    # If an SQL file is uploaded, execute it
    if uploaded_sql:
        execute_sql_file(conn, uploaded_sql)

    # Text area for SQL query input
    query = st.text_area("Enter your SQL query:", height=100)

    if st.button("Run Query"):
        if query.strip():
            results = run_query(conn, query)
            if results is not None:
                st.write("Query Results:")
                st.dataframe(results)

                # Download results as CSV
                csv = results.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                )
        else:
            st.warning("Please enter a valid SQL query.")

    # Close the connection when the app ends
    conn.close()

# Sidebar instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload your SQLite database file (.db, .sqlite, .sqlite3).
2. Optionally, upload an SQL file (.sql) to execute commands on the database.
3. Enter your SQL query in the text area and click 'Run Query'.
4. View the results and download them as a CSV file if needed.
""")
