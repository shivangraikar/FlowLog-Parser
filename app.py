import streamlit as st

st.title("Flow Log Tagging Application")
flow_log_file = st.file_uploader("Upload Flow Log File", type=["txt"])
lookup_table_file = st.file_uploader("Upload Lookup Table", type=["csv"])