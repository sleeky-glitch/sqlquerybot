import streamlit as st
import sqlite3
import pandas as pd
from langchain import SQLDatabase, SQLDatabaseChain
from langchain.llms import OpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

# Set up page configuration
st.set_page_config(page_title="SQL Data Chat Assistant", layout="wide")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def load_sql_database(sql_file):
    """Connect to the SQL database"""
    return SQLDatabase.from_uri(f"sqlite:///{sql_file}")

def initialize_agent(db):
    """Initialize the SQL agent"""
    llm = OpenAI(temperature=0, openai_api_key=st.secrets["OPENAI_API_KEY"])
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

# Main app
st.title("💬 Chat with Your SQL Database")

# File uploader for SQL file
sql_file = st.file_uploader("Upload your SQL file", type=['sql', 'db', 'sqlite'])

if sql_file:
    # Save the uploaded file
    with open("temp_database.db", "wb") as f:
        f.write(sql_file.getbuffer())

    try:
        # Initialize database and agent
        db = load_sql_database("temp_database.db")
        agent = initialize_agent(db)

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
                    response = agent.run(prompt)
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
    st.info("Please upload a SQL database file to begin chatting.")

# Created/Modified files during execution:
print("temp_database.db")
