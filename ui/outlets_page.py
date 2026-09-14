import os
import streamlit as st
from generators.locations import load_location, us_file
from ui.location_fields import render_location_fields
from generators.outlets import make_outlets_report, parse_locations_file, fill_outlets_for_rows

def render_outlets_page():
    upload_filing_calendar_checkbox = st.checkbox("Upload Filing Calendar")
    if upload_filing_calendar_checkbox:
        file_path = st.file_uploader("Upload Filing Calendar", type= ["csv", "xlsx"])
        if file_path:
            file_id = (file_path.name, file_path.size)
            try:
                if st.session_state.get("filing_calendar_file_id") != file_id:
                    parsed = parse_locations_file(file_path, file_path.name)
                    st.session_state.filing_calendar_data = fill_outlets_for_rows(parsed)
                    st.session_state.filing_calendar_file_id = file_id
                st.dataframe(st.session_state.filing_calendar_data)
            except (ValueError, KeyError, IndexError) as e:
                st.error(str(e))

    st.divider()

    if not upload_filing_calendar_checkbox:
        st.write("Add Outlet")

        if (
            "outlets" not in st.session_state
            or not st.session_state.outlets
            or not isinstance(st.session_state.outlets[0], dict)
            or "Entity Name" not in st.session_state.outlets[0]
        ):
            st.session_state.outlets = [{
                "Entity Name": "",
                "State": "",
                "County": "",
                "City": "",
                "Zip Code": "",
            }] 
        
        location_list = load_location(us_file)

        col1, col2,_ = st.columns([1, 1, 8])
        with col1:
            add_outlet = st.button("➕", key="add_outlet")
        with col2:
            remove_outlet = st.button("➖", key="remove_outlet")

        if add_outlet:
            st.session_state.outlets.append({
                "Entity Name": "",
                "State": None,
                "County": None,
                "City": None,
                "Zip Code": "",
            })
        if remove_outlet and len(st.session_state.outlets) > 1:
            st.session_state.outlets.pop()

        for i in range(len(st.session_state.outlets)):
        
            entity_name = st.text_input(
                f"Outlet {i + 1} Entity Name",
                value=st.session_state.outlets[i].get("Entity Name", ""),
                key=f"outlet_entity_name_{i}",
            )

            location = render_location_fields(
                "outlet",
                i,
                location_list,
                f"Outlet {i + 1}",
            )
            
            st.session_state.outlets[i] = {
                "Entity Name": entity_name,
                "State": location["state"], 
                "County": location["county"],
                "City": location["city"],
                "Zip Code": location["zip_code"],
            }
            st.divider()


# -----------------------------FILE NAME SECTION--------------------------------

    raw_name_outlets = st.text_input("File name", key="raw_name_outlets")

    if raw_name_outlets:
        file_name_outlets = raw_name_outlets.strip() + ".xlsx"
    else:
        file_name_outlets = "Outlet_Report.xlsx"

# -----------------------------GENERATE BUTTON SECTION--------------------------------

    generate_button_outlets = st.button("Generate Outlet Report", key="generate_button_outlets")
   

    if generate_button_outlets:
        if upload_filing_calendar_checkbox and st.session_state.get("filing_calendar_data"):
           outlets_to_generate = st.session_state.filing_calendar_data
        else:
            outlets_to_generate = st.session_state.outlets

        for outlet in outlets_to_generate:
            if not (outlet.get("Entity Name") or "").strip():
                st.error("Please add an entity name to the outlet.", icon="❌")
                st.stop()
            if not (outlet.get("State") or "").strip():
                st.error("Please add a state to the outlet.", icon="❌")
                st.stop()
    
   
        
        file_path = make_outlets_report(outlets_to_generate, file_name_outlets)
        st.success(file_name_outlets + " was generated successfully.", icon="✅")

        with open(file_path, "rb") as f:
            st.download_button(
                label="Download Outlet Report",
                data=f,
                file_name=os.path.basename(file_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )