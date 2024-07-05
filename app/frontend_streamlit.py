import streamlit as st
import requests
import json

# FastAPI server URL
UPLOAD_URL = "http://localhost:8000/upload/"
RESULT_URL = "http://localhost:8000/result/"

st.title("Bill of Lading Processing App")

uploaded_file = st.file_uploader("Upload your Bill of Lading PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Uploading file..."):
        try:
            files = {"file": uploaded_file}
            response = requests.post(UPLOAD_URL, files=files)
            response.raise_for_status()
            result_id = response.text.strip('"')
            st.success(f"File uploaded successfully. Result ID: {result_id}")

            with st.spinner("Processing file..."):
                result_response = requests.get(f"{RESULT_URL}{result_id}")
                result_response.raise_for_status()
                result_data = result_response.json()

                st.write("Processed Data:")
                st.json(result_data)

        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

