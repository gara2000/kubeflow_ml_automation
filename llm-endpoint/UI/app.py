import streamlit as st
import requests
import os

# Set up the Streamlit app
st.title("LLM Text Generation")
st.write("Enter a question and context to get a response from the LLM.")

# Input fields for the user
question = st.text_input("Question:", placeholder="Enter your question here")
context = st.text_area("Context:", placeholder="Provide the relevant context here")

# API URL
api_url = os.getenv("API_URL", "http://127.0.0.1:5000/generate")  # Adjust if Flask API runs on a different host/port

# Button to generate a response
if st.button("Generate Response"):
    if not question.strip() or not context.strip():
        st.error("Both 'Question' and 'Context' are required.")
    else:
        # Send a POST request to the API
        payload = {"question": question, "context": context}
        try:
            headers = {"X-Frontend-Access": "true"}
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                st.success("Response generated successfully!")
                st.text_area("AI Response:", value=response.json().get("response"), height=200)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {e}")
