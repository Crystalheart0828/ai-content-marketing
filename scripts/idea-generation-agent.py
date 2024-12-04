import streamlit as st
import openai
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import List, Dict, Any
import json

# OpenAI API Key Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load credentials from Streamlit secrets
gcp_credentials_json = st.secrets["GCP_CREDENTIALS_JSON"]
credentials = service_account.Credentials.from_service_account_info(json.loads(gcp_credentials_json))



# Google API Configuration (replace with your credentials file)
GOOGLE_CREDENTIALS = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["GCP_CREDENTIALS_JSON"]),
    scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]
)

# Function to interact with OpenAI API using chat completions
def query_openai(prompt: str, content: str, system_message: str, model: str = "gpt-4o-mini") -> str:
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{prompt}\n\n內容：{content}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Error querying OpenAI API: {e}")

# Functions for AI Tasks
def generate_buyer_personas(inputs: Dict[str, Any]) -> str:
    system_message = "You are an expert in creating detailed buyer personas for targeted marketing campaigns."
    prompt = "Generate 3 detailed buyer personas with demographics, interests, and pain points."
    content = f"""
    Brand: {inputs['brand']}
    Target Audience: {inputs['target_audience']}
    Business Goal: {inputs['business_goal']}
    Special Feature: {inputs['special_feature']}
    """
    return query_openai(prompt, content, system_message)

def create_content_strategy(inputs: Dict[str, Any]) -> str:
    system_message = "You are a marketing strategist specializing in crafting content strategies that align with business goals and audience preferences."
    prompt = "Develop a detailed content strategy to achieve the business goal."
    content = f"""
    Brand: {inputs['brand']}
    Target Audience: {inputs['target_audience']}
    Business Goal: {inputs['business_goal']}
    Special Feature: {inputs['special_feature']}
    """
    return query_openai(prompt, content, system_message)

def generate_content_topics(strategy: str) -> List[str]:
    system_message = "You are a creative marketing strategist brainstorming unique and impactful content topics."
    prompt = "Generate 10 unique content topics that align with the business goal."
    return query_openai(prompt, strategy, system_message).split("\n")

def suggest_content_types_and_platforms(inputs: Dict[str, Any]) -> str:
    system_message = "You are a creative marketer suggesting impactful content types and platforms for audience engagement."
    prompt = """
    Suggest preferred content types (e.g., blogs, videos, podcasts) and platforms (e.g., Instagram, LinkedIn, YouTube).
    """
    content = f"""
    Target Audience: {inputs['target_audience']}
    Business Goal: {inputs['business_goal']}
    """
    return query_openai(prompt, content, system_message)

# Google Docs Integration
def create_google_doc(content: str, title: str) -> str:
    service = build('docs', 'v1', credentials=GOOGLE_CREDENTIALS)
    doc = service.documents().create(body={"title": title}).execute()
    document_id = doc.get("documentId")
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": content
            }
        }
    ]
    service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
    return document_id

def export_to_google_drive(content: str, folder_id: str, title: str) -> None:
    service = build('drive', 'v3', credentials=GOOGLE_CREDENTIALS)
    document_id = create_google_doc(content, title)
    drive_service = build('drive', 'v3', credentials=GOOGLE_CREDENTIALS)
    file_metadata = {"name": title, "parents": [folder_id]}
    drive_service.files().update(fileId=document_id, addParents=folder_id).execute()
    

# Streamlit App
st.title("AI Content Marketing Idea Generator")
st.sidebar.title("Input Parameters")

# Input Fields
brand = st.sidebar.text_input("Brand, Product, Service, or Campaign")
target_audience = st.sidebar.text_area("Target Audience (multiple groups allowed)")
business_goal = st.sidebar.text_input("Business Goal")
special_feature = st.sidebar.text_input("What's Special (1 line)")
google_folder_id = st.sidebar.text_input("Google Drive Folder ID")

# Create a dictionary of inputs
inputs = {
    "brand": brand,
    "target_audience": target_audience,
    "business_goal": business_goal,
    "special_feature": special_feature,
}

# Generate Outputs
if st.button("Generate Buyer Personas"):
    if all(inputs.values()):
        with st.spinner("Generating Buyer Personas..."):
            personas = generate_buyer_personas(inputs)
        st.subheader("Buyer Personas")
        st.write(personas)
        # Add export button dynamically
        if st.button("Export Buyer Personas to Google Drive"):
            try:
                export_to_google_drive(personas, google_folder_id, "Buyer Personas")
                st.success("Buyer Personas exported successfully to Google Drive!")
            except Exception as e:
                st.error(f"Failed to export: {e}")

if st.button("Generate Content Strategy"):
    if all(inputs.values()):
        with st.spinner("Creating Content Strategy..."):
            strategy = create_content_strategy(inputs)
        st.subheader("Content Strategy")
        st.write(strategy)
        # Add export button dynamically
        if st.button("Export Content Strategy to Google Drive"):
            try:
                export_to_google_drive(strategy, google_folder_id, "Content Strategy")
                st.success("Content Strategy exported successfully to Google Drive!")
            except Exception as e:
                st.error(f"Failed to export: {e}")

if st.button("Generate Content Topics"):
    if all(inputs.values()):
        with st.spinner("Generating Content Topics..."):
            strategy = create_content_strategy(inputs)
            topics = "\n".join(generate_content_topics(strategy))
        st.subheader("Content Topics")
        st.write(topics)
        # Add export button dynamically
        if st.button("Export Content Topics to Google Drive"):
            try:
                export_to_google_drive(topics, google_folder_id, "Content Topics")
                st.success("Content Topics exported successfully to Google Drive!")
            except Exception as e:
                st.error(f"Failed to export: {e}")

if st.button("Suggest Content Types and Platforms"):
    if all(inputs.values()):
        with st.spinner("Suggesting Content Types and Platforms..."):
            suggestions = suggest_content_types_and_platforms(inputs)
        st.subheader("Content Types and Platforms")
        st.write(suggestions)
        # Add export button dynamically
        if st.button("Export Content Types and Platforms to Google Drive"):
            try:
                export_to_google_drive(suggestions, google_folder_id, "Content Types and Platforms")
                st.success("Content Types and Platforms exported successfully to Google Drive!")
            except Exception as e:
                st.error(f"Failed to export: {e}")