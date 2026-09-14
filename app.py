import streamlit as st
from ui.data_import_page import render_data_import_page
from ui.outlets_page import render_outlets_page
from ui.filing_calendar_page import render_filing_calendar_page

st.title("Tax DataGen")
st.write("Generate BasicAvalara test data")

tab_data_import, tab_filing_calendar, tab_outlets = st.tabs(["Data Import", "Filing Calendar", "Outlets"])

with tab_data_import:
    render_data_import_page()

with tab_filing_calendar:
    render_filing_calendar_page()

with tab_outlets:
    render_outlets_page()


