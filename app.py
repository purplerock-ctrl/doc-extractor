import tempfile
from pathlib import Path

import streamlit as st

from checks import check
from extract import extract

st.title("Receipt extractor")

password = st.text_input("Password", type="password")
if password != st.secrets["APP_PASSWORD"]:
    st.stop()                       # nothing below runs until the password is right

@st.cache_data(show_spinner="Reading the document...")
def run_extraction(file_bytes, suffix):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
    receipt, usage = extract(tmp.name)
    return receipt

uploaded = st.file_uploader("Upload a receipt", type=["pdf", "jpg", "jpeg", "png"])

if uploaded is not None:
    try:
        receipt = run_extraction(uploaded.getvalue(), Path(uploaded.name).suffix)
    except Exception:
        st.error("Sorry, that file could not be read. Try a clearer photo or a PDF.")
        st.stop()

    problems = check(receipt)
    if problems:
        st.warning("Please check: " + "; ".join(problems))
    else:
        st.success("No problems found")

    with st.form("review"):
        vendor = st.text_input("Vendor", receipt.vendor or "")
        day = st.text_input("Date (YYYY-MM-DD)", receipt.date or "")
        total = st.number_input("Total", value=receipt.total or 0.0)
        saved = st.form_submit_button("Save")

    if saved:
        # write vendor, day and total to your database here
        st.success("Saved")