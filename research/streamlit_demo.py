import streamlit as st

st.title("VideoMind : AI Powered Video Intelligence Platform")

youtube_url = st.text_input("Analyze videos, extract insights, and chat with content")

if youtube_url:
    video_id = youtube_url.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get summary"):
    pass