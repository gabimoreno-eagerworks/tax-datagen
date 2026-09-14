import streamlit as st
from generators.data_import import (
    make_excel,
    load_subcategories,
    parse_locations_file,
)
from generators.locations import load_location, location_match_pools, load_zip_rows, us_file
from ui.location_fields import render_location_fields
from api_utils import validate_api
import os

sub_file = os.getenv("SUBCATEGORIES_PATH", "data/subcategories.csv")

def render_data_import_page():

# -----------------------------CATEGORIES AND SUBCATEGORIES SECTION--------------------------------

    st.write("Select Subcategories")

    final_list = load_subcategories(sub_file)


    if "subcategory_ids" not in st.session_state:
        first_category = list(final_list.keys())[0]
        st.session_state.subcategory_ids = [{
            "category": first_category,
            "subcategory": final_list[first_category][0],
        }]

    col1, col2,_ = st.columns([1, 1, 8])
    with col1:
        add_subcategory_id = st.button("➕", key="add_subcategory")
    with col2:
        remove_subcategory_id = st.button("➖", key="remove_subcategory")

    if add_subcategory_id:
        first_category = list(final_list.keys())[0]
        st.session_state.subcategory_ids.append({
            "category": first_category,
            "subcategory": final_list[first_category][0],})
    if remove_subcategory_id and len(st.session_state.subcategory_ids) > 1:
        st.session_state.subcategory_ids.pop()

    for i in range(len(st.session_state.subcategory_ids)):
        col_cat, col_sub = st.columns(2)
        with col_cat:
            category = st.selectbox(
                f"Category {i + 1}",
                list(final_list.keys()),
                key=f"category_{i}",
            )
        with col_sub:
            subcategory = st.selectbox(
                f"Subcategory {i + 1}",
                final_list[category],
                key=f"subcategory_{i}",
            )
        st.session_state.subcategory_ids[i] = {
            "category": category,
            "subcategory": subcategory,
        }

    st.divider()

    # -----------------------------NUMBER OF TRANSACTIONS SECTION--------------------------------

    num_transaction = st.number_input("Number of transactions", min_value=1, max_value=None, value=10)

    st.divider()

    # -----------------------------TRANSACTION TYPE SECTION--------------------------------

    st.write("Select Transaction Type")

    ecommerce = st.checkbox("E-commerce")
    outlet = st.checkbox("Outlet")

    if "location_list" not in st.session_state:
            st.session_state.location_list = load_location(us_file)

    if ecommerce:
        if "ecommerce_locations" not in st.session_state:
            st.session_state.ecommerce_locations = [{
                "ecommerce_state": "",
                "ecommerce_county": "",
                "ecommerce_city": "",
                "ecommerce_zip_code": "",
            }]

        col1, col2,_ = st.columns([1, 1, 8])
        with col1:
            add_ecommerce_location = st.button("➕", key="add_ecommerce_location")
        with col2:
            remove_ecommerce_location = st.button("➖", key="remove_ecommerce_location")
        
        if add_ecommerce_location:
            st.session_state.ecommerce_locations.append({
                "ecommerce_state": "",
                "ecommerce_county": "",
                "ecommerce_city": "",
                "ecommerce_zip_code": "",
            })
        if remove_ecommerce_location and len(st.session_state.ecommerce_locations) > 1:
            st.session_state.ecommerce_locations.pop()


        for i in range(len(st.session_state.ecommerce_locations)):
            location = render_location_fields(
                "ecommerce",
                i,
                st.session_state.location_list,
                f"Ecommerce {i + 1}",
            )
            st.session_state.ecommerce_locations[i] = {
                "ecommerce_state": location["state"],
                "ecommerce_county": location["county"],
                "ecommerce_city": location["city"],
                "ecommerce_zip_code": location["zip_code"],
            }


    
    outlet_rows = []
    if outlet:
        st.write("Upload outlet file (optional)")
        uploaded = st.file_uploader(
            "CSV or Excel with Store ID, State, County, City, and Zip Code",
            type=["csv", "xlsx"],
        )
        if uploaded is not None:
            try:
                outlet_rows = parse_locations_file(uploaded, uploaded.name)
                st.success(f"Loaded {len(outlet_rows)} store(s).")
                st.dataframe(outlet_rows)
            except (ValueError, KeyError, IndexError) as e:
                st.error(str(e))
        st.divider()

    if outlet:
        if (
            "store_ids" not in st.session_state 
            or not st.session_state.store_ids 
            or not isinstance(st.session_state.store_ids[0], dict)
        ):
            st.session_state.store_ids = [{
                "store_id": "",
                "state": "",
                "county": "",
                "city": "",
                "zip_code": "",
            }]

    if outlet and not outlet_rows:

        col1, col2,_ = st.columns([1, 1, 8])
        with col1:
            add_store_id = st.button("➕", key="add_store")
        with col2:
            remove_store_id = st.button("➖", key="remove_store")


        if add_store_id:
            st.session_state.store_ids.append({
                "store_id": "",
                "state": "",
                "county": "",
                "city": "",
                "zip_code": "",
            })
        if remove_store_id and len(st.session_state.store_ids) > 1:
            st.session_state.store_ids.pop()

        for i in range(len(st.session_state.store_ids)):
            store_id = st.text_input(
            f"Store ID {i + 1}",
            value=st.session_state.store_ids[i]["store_id"],
            key=f"store_id_{i}",
        )
            location = render_location_fields(
                "store",
                i,
                st.session_state.location_list,
                f"Store {i + 1}",
            )
            st.session_state.store_ids[i] = {
                "store_id": store_id,
                "state": location["state"],
                "county": location["county"],
                "city": location["city"],
                "zip_code": location["zip_code"],
            }
            st.divider()


# -----------------------------FILE NAME SECTION--------------------------------

    raw_name = st.text_input("File name")
    if raw_name:
        file_name = raw_name.strip() + ".xlsx"
    else:
        file_name = "BasicAvalara_test.xlsx"

# -----------------------------GENERATE BUTTON SECTION--------------------------------

    generate_button = st.button("Generate")

    if generate_button:
        locations = []
        if outlet_rows:
            for row in outlet_rows:
                locations.append({
                    "store_id": row["store_id"],
                    "state": row["state"],
                    "county": row["county"],
                    "city": row["city"],
                    "zip_code": row["zip_code"],
                })
        elif outlet:
            for store in st.session_state.store_ids:
                locations.append({
                    "store_id": store["store_id"],
                    "state": store["state"],
                    "county": store["county"],
                    "city": store["city"],
                    "zip_code": store["zip_code"],
                })
        if ecommerce:
            for location in st.session_state.ecommerce_locations:
                locations.append({
                    "store_id": "",
                    "state": location["ecommerce_state"],
                    "county": location["ecommerce_county"],
                    "city": location["ecommerce_city"],
                    "zip_code": location["ecommerce_zip_code"],
                })

# -----------------------------VALIDATION SECTION--------------------------------

        if not locations:
            st.error("Select E-commerce and/or Outlet, and enter at least one location.", icon="🚨")
            st.stop()

        for loc in locations:
            state = loc["state"]
            county = loc["county"]
            city = loc["city"]
            zip_code = loc["zip_code"]

            if not state and not county and not city and not zip_code:
                st.error("At least one valid location input is required.", icon="🚨")
                st.stop()

            if zip_code and not validate_api(zip_code, state):
                st.error("Zip does not exist or does not match state.", icon="🚨")
                st.stop()

        zip_rows = load_zip_rows(us_file)
        pools = location_match_pools(zip_rows, locations)
        if pools is None:
            st.error("Input values do not match on the list.", icon="🚨")
            st.stop()

# -----------------------------GENERATION SECTION--------------------------------

        file_path = make_excel(st.session_state.subcategory_ids, num_transaction, pools, file_name)

        st.success(file_name + " was generated successfully.", icon="✅")

# -----------------------------DOWNLOAD BUTTON SECTION--------------------------------

        with open(file_path, "rb") as f:
            st.download_button(
                label="Download Excel file",
                data=f,
                file_name=os.path.basename(file_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
