import os
import streamlit as st
from generators.locations import load_location, us_file
from generators.filing_calendar import make_filing_calendar

location_list = load_location(us_file)
def render_filing_calendar_page():

# -----------------------------ENTITIES SECTION--------------------------------
    st.write("Add Entity to Filing Calendar")

    if (
        "entities" not in st.session_state
        or not st.session_state.entities
        or not isinstance(st.session_state.entities[0], dict)):
        st.session_state.entities = [{"name": "", "states": []}]


    col1, col2,_ = st.columns([1, 1, 8])
    with col1:
        add_filing_calendar_entity = st.button("➕", key="add_filing_calendar_entity")
    with col2:
        remove_filing_calendar_entity = st.button("➖", key="remove_filing_calendar_entity")

    if add_filing_calendar_entity:
        st.session_state.entities.append({"name": "", "state": []})


    if remove_filing_calendar_entity and len(st.session_state.entities) > 1:
        st.session_state.entities.pop()

    for i in range(len(st.session_state.entities)):

            entity_name = st.text_input(
                f"Entity {i + 1} Name",
                value=st.session_state.entities[i]["name"],
                key=f"filing_calendar_entity_{i}",
            )

            all_states = sorted(list(location_list.keys()))
            state_key = f"filing_calendar_state_{i}"
            select_all = st.checkbox("Select all states", key=f"filing_calendar_select_all_{i}")

            if select_all:
                st.session_state[state_key] = all_states
            filing_calendar_states = st.multiselect(
                f"Filing Calendar {i + 1} State",
                options=all_states,
                key=state_key,
            )
            st.session_state.entities[i] = {
            "name": entity_name,
            "states": filing_calendar_states,
            }

            st.divider()


# -----------------------------FILE NAME SECTION--------------------------------

    raw_name_filing_calendar = st.text_input("File name", key="raw_name_filing_calendar")

    if raw_name_filing_calendar:
        file_name_filing_calendar = raw_name_filing_calendar.strip() + ".xlsx"
    else:
        file_name_filing_calendar = "Filing_Calendar.xlsx"


# -----------------------------GENERATE BUTTON SECTION--------------------------------

    entity_names = [entity["name"] for entity in st.session_state.entities]
    entity_states = [entity["states"] for entity in st.session_state.entities]

    generate_button_filing_calendar = st.button("Generate Filing Calendar", key="generate_button_filing_calendar")

    if generate_button_filing_calendar:

        file_path = make_filing_calendar(entity_names, entity_states, file_name_filing_calendar)
        st.success(file_name_filing_calendar + " was generated successfully.", icon="✅")

# -----------------------------DOWNLOAD BUTTON SECTION--------------------------------

        with open(file_path, "rb") as f:
            st.download_button(
                label="Download Filing Calendar",
                data=f,
                file_name=os.path.basename(file_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )