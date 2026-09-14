
import csv
from openpyxl import Workbook, load_workbook
import random
import os
import re
import io

us_file = os.getenv("USZIPS_PATH", "data/uszips.csv")

def load_location(path):

    location_list = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            state = row["state_name"]
            county = row["county_name"]
            city = row["city"]

            if state not in location_list:
                location_list[state] = {}
            
            if county not in location_list[state]:
                location_list[state][county] = set()
               
            location_list[state][county].add(city)

    return location_list

def load_zip_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def matching_zip_rows(rows, state=None, county=None, city=None, zip_code=None):
    matches = []
    for row in rows:
        match_state = (not state or row["state_name"] == state)
        match_county = (not county or row["county_name"] == county)
        match_city = (not city or row["city"] == city)
        match_zip = (not zip_code or row["zip"] == zip_code)
        if match_state and match_city and match_county and match_zip:
            matches.append(row)
    return matches

def location_match_pools(zip_rows, locations):
    pools = []
    for loc in locations:
        matches = matching_zip_rows(
            zip_rows,
            state=loc.get("state") or None,
            county=loc.get("county") or None,
            city=loc.get("city") or None,
            zip_code=loc.get("zip_code") or None,
        )
        if not matches:
            return None
        pools.append({
            "store_id": loc.get("store_id", ""),
            "matches": matches,
        })
    return pools

def fill_location(path, state=None, county=None, city=None, zip_code=None):

        rows = load_zip_rows(path)
        matches = matching_zip_rows(rows, state, county, city, zip_code)

        if not matches:
            return None

        row = random.choice(matches)
        state_output = state or row["state_name"]
        county_output = county or row["county_name"]
        city_output = city or row["city"]
        zip_output = zip_code or row["zip"]
        return state_output, county_output, city_output, zip_output


def fill_locations_for_rows(path, num_rows, state=None, county=None, city=None, zip_code=None, zip_rows=None):

        rows = zip_rows if zip_rows is not None else load_zip_rows(path)
        matches = matching_zip_rows(rows, state, county, city, zip_code)

        if not matches:
            return None

        locations = []
        previous_location = None
        for _ in range(num_rows):
            if len(matches) > 1:
                pool = [candidate for candidate in matches if candidate != previous_location]
                selected = random.choice(pool or matches)
            else:
                selected = matches[0]

            locations.append({
                "state": selected["state_name"],
                "county": selected["county_name"],
                "city": selected["city"],
                "zip_code": selected["zip"],
            })
            previous_location = selected

        return locations

def fix_location_name(name):
    if not name:
        return name
    return re.sub(r'^(St\.|st\.|St|st)\s', 'Saint ', name)