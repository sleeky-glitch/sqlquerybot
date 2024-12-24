import streamlit as st
import sqlite3
import os
from langchain.llms import OpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

def create_database_from_sql(sql_file, db_file):
    """Create a SQLite database from a .sql file with proper encoding handling."""
    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()

                with open(sql_file, 'r', encoding=encoding) as f:
                    sql_script = f.read()

                # Split the script into individual statements
                # This handles both semicolon and GO statement separators
                statements = [statement.strip() for statement in sql_script.replace('\nGO', ';').split(';') if statement.strip()]

                # Execute each statement separately
                for statement in statements:
                    try:
                        cursor.execute(statement)
                        conn.commit()
                    except sqlite3.Error as e:
                        st.warning(f"Skipping statement due to error: {e}")
                        continue

                conn.close()
                st.success(f"Database created successfully using {encoding} encoding!")
                return True

            except UnicodeDecodeError:
                continue  # Try next encoding
            except Exception as e:
                st.warning(f"Failed with {encoding} encoding: {str(e)}")
                continue

        st.error("Failed to create database with any encoding")
        return False

    except Exception as e:
        st.error(f"Error creating database: {str(e)}")
        return False

# Set up page configuration
st.set_page_config(page_title="SQL Data Chat Assistant", layout="wide")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def load_sql_database(sql_file):
    """Connect to the SQL database."""
    return SQLDatabase.from_uri(f"sqlite:///{sql_file}")

# Main app
st.title("💬 Chat with Your SQL Database")

# File uploader for SQL file
uploaded_file = st.file_uploader("Upload your SQL file or SQLite database", type=['sql', 'db', 'sqlite'])

if uploaded_file:
    # Save the uploaded file
    file_name = uploaded_file.name
    with open(file_name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Check file type and process accordingly
    if file_name.endswith(".sql"):
        st.info("Detected a .sql file. Creating a SQLite database...")
        db_file = "temp_database.db"
        if create_database_from_sql(file_name, db_file):
            st.success("Database created successfully!")
            sql_file = db_file
        else:
            st.error("Failed to create database from the .sql file.")
            st.stop()
    else:
        sql_file = file_name

    try:
        # Initialize database and agent
        db = load_sql_database(sql_file)

        # Create the SQLDatabaseChain
        llm = OpenAI(temperature=0, openai_api_key=st.secrets["OPENAI_API_KEY"])
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

        # Display chat interface
        st.write("Chat with your data! Ask questions about your database.")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("What would you like to know about your data?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate AI response
            with st.chat_message("assistant"):
                try:
                    response = db_chain.run(prompt)
                    st.markdown(response)
                    # Add AI response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

    except Exception as e:
        st.error(f"Error loading database: {str(e)}")

else:
    st.info("Please upload a SQL database file or a .sql script to begin chatting.")
