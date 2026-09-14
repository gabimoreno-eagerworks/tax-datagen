import streamlit as st
from generators.locations import fill_location, us_file


def apply_location_fields(key_prefix, i, state=None, county=None, city=None, zip_code=None):
    state = state or None
    county = county or None
    city = city or None
    zip_code = zip_code or None

    if state is None and county is None and city is None and zip_code is None:
        return

    location = fill_location(
        us_file,
        state=state,
        county=county,
        city=city,
        zip_code=zip_code,
    )
    if not location:
        return

    filled_state, filled_county, filled_city, filled_zip = location

    if state is None:
        st.session_state[f"{key_prefix}_state_{i}"] = filled_state
    if county is None:
        st.session_state[f"{key_prefix}_county_{i}"] = filled_county
    if city is None:
        st.session_state[f"{key_prefix}_city_{i}"] = filled_city
    if zip_code is None:
        st.session_state[f"{key_prefix}_zip_code_{i}"] = str(filled_zip or "")

def on_state_change(key_prefix, i):
    apply_location_fields(
        key_prefix,
        i,
        state=st.session_state.get(f"{key_prefix}_state_{i}"),
    )

def on_county_change(key_prefix, i):
    apply_location_fields(
        key_prefix,
        i,
        state=st.session_state.get(f"{key_prefix}_state_{i}"),
        county=st.session_state.get(f"{key_prefix}_county_{i}"),
    )

def on_city_change(key_prefix, i):
    apply_location_fields(
        key_prefix,
        i,
        state=st.session_state.get(f"{key_prefix}_state_{i}"),
        county=st.session_state.get(f"{key_prefix}_county_{i}"),
        city=st.session_state.get(f"{key_prefix}_city_{i}"),
    )

def on_zip_code_change(key_prefix, i):
    apply_location_fields(
        key_prefix,
        i,
        zip_code=st.session_state.get(f"{key_prefix}_zip_code_{i}"),
    )

def render_location_fields(key_prefix, i, location_list, label):
    state_key = f"{key_prefix}_state_{i}"
    county_key = f"{key_prefix}_county_{i}"
    city_key = f"{key_prefix}_city_{i}"
    zip_code_key = f"{key_prefix}_zip_code_{i}"

    state = st.session_state.get(state_key)
    county = st.session_state.get(county_key)
    city = st.session_state.get(city_key)
    zip_code = st.session_state.get(zip_code_key) or ""
    
    if (state or county or city or zip_code) and (
        not state or not county or not city or not zip_code
    ):
        apply_location_fields(
            key_prefix,
            i,
            state=state or None,
            county=county or None,
            city=city or None,
            zip_code=zip_code or None,
        )
        state = st.session_state.get(state_key)
        county = st.session_state.get(county_key)
        city = st.session_state.get(city_key)
        zip_code = st.session_state.get(zip_code_key) or ""

    if state:
        county_options = sorted(list(location_list[state].keys()))
    else:
        county_options = []

    if county not in county_options:
        st.session_state[county_key] = None
        county = None

    if state and county:
        city_options = sorted(list(location_list[state][county]))
    else:
        city_options = []

    if city not in city_options:
        st.session_state[city_key] = None
        city = None

    all_states = sorted(list(location_list.keys()))

    col_state, col_county = st.columns(2)
    col_city, col_zip = st.columns(2)

    with col_state:
        state = st.selectbox(
            f"{label} State",
            all_states,
            index=None,
            placeholder="Select State",
            key=state_key,
            on_change=on_state_change,
            args=(key_prefix, i),
        )
    with col_county:
        county = st.selectbox(
            f"{label} County",
            county_options,
            index=None,
            placeholder="Select County",
            key=county_key,
            on_change=on_county_change,
            args=(key_prefix, i),
        )
    with col_city:
        city = st.selectbox(
            f"{label} City",
            city_options,
            index=None,
            placeholder="Select City",
            key=city_key,
            on_change=on_city_change,
            args=(key_prefix, i),
        )
    with col_zip:
        zip_code = st.text_input(
            f"{label} Zip Code",
            key=zip_code_key,
            on_change=on_zip_code_change,
            args=(key_prefix, i),
        )

    return {
        "state": state,
        "county": county,
        "city": city,
        "zip_code": zip_code,
    }