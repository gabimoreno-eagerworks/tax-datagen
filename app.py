import streamlit as st
from generator import make_excel, load_subcategories, load_location, fill_location
from api_utils import validate_api
import os


us_file = os.getenv("USZIPS_PATH", "data/uszips.csv")
sub_file = os.getenv("SUBCATEGORIES_PATH", "data/subcategories.csv")

st.title("Tax DataGen")
st.write("Generate BasicAvalara test data")


st.divider()

final_list = load_subcategories(sub_file)
category = st.selectbox(
    "Select Category",
    final_list.keys())

subcategory = st.selectbox(
    "Select Subcategory",
    final_list[category])

st.divider()

num_transaction = st.number_input("Number of transactions", min_value=1, max_value=10000, value=10)

st.divider()

ecommerce = st.checkbox("E-commerce")
outlet = st.checkbox("Outlet")
if "store_ids" not in st.session_state:
    store_ids = st.session_state.store_ids = []


if outlet:

    col1, col2,_ = st.columns([1, 1, 8])
    with col1:
        add_store_id = st.button("➕")
    with col2:
        remove_store_id = st.button("➖")

    if add_store_id:
        st.session_state.store_ids.append("")
    if remove_store_id and len(st.session_state.store_ids) > 1:
        st.session_state.store_ids.pop()

    for i in range(len(st.session_state.store_ids)):
        st.session_state.store_ids[i] = st.text_input(
            f"Store ID {i + 1}",
            value=st.session_state.store_ids[i],
            key=f"store_id_{i}",
        )


st.divider()

location_list = load_location(us_file)

state = st.selectbox(
    "State", 
    sorted(list(location_list.keys())), 
    index = None, 
    placeholder = "Select State")

if state:
    county = st.selectbox(
            "County",  
            sorted(list(location_list[state].keys())), 
            index = None, 
            placeholder = "Select County")
else:
    county = st.text_input(
            "County",  
            placeholder = "Select County")

if county:
    city = st.selectbox(
            "City",  
            sorted(location_list[state][county]), 
            index = None, 
            placeholder = "Select City")
else:
    city = st.text_input(
            "City",  
            placeholder = "Select City")
zip_code = st.text_input("Zip Code")


st.divider()
raw_name = st.text_input("File name")
if raw_name:
    file_name = raw_name.strip() + ".xlsx"
else:
    file_name = "BasicAvalara_test.xlsx"

generate_button = st.button("Generate")

if generate_button:

    store_ids = st.session_state.store_ids
    if ecommerce and not outlet:
        store_ids = [""]
    elif outlet and not ecommerce:
        store_ids = st.session_state.store_ids
    elif ecommerce and outlet:
        store_ids = st.session_state.store_ids + [""]

    if not state and not county and not city and not zip_code:
        st.error("At least one valid location input is required.", icon="🚨")
        st.stop()

    if zip_code and not validate_api(zip_code, state):
        st.error("Zip does not exist or does not match state.", icon="🚨")
        st.stop()


    if fill_location(us_file, state, county, city, zip_code) is None:
        st.error("Input values do not match on the list.", icon="🚨")
        st.stop()

    state, county, city, zip_code = fill_location(us_file, state, county, city, zip_code)
                    
    file_path = make_excel(subcategory, num_transaction, state, file_name,
    store_ids, county, city, zip_code)

    st.success(file_name + " was generated successfully.", icon="✅")

    with open(file_path, "rb") as f:
        st.download_button(
            label="Download Excel file",
            data=f,
            file_name=os.path.basename(file_path),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
