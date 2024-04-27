import streamlit as st
import os

# Specify port for Heroku deployment
port = int(os.environ.get('PORT', 8501))

# Run Streamlit app
if __name__ == '__main__':
    st.run(port=port)
