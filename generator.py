import csv
from openpyxl import Workbook
import random
import os
import re

def validate_text(value):
    if not value:
        return False

    return bool(re.fullmatch(r"[A-Za-z\s]+", value.strip()))

def load_subcategories(path):

    final_list = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            category = row["Category"]
            subcategory = row["Subcategory"]
            if category not in final_list:
                final_list[category] = [subcategory]
            else:
                final_list[category].append(subcategory)
    return final_list

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


def fill_location(path, state=None, county=None, city=None, zip_code=None):

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            match_state = (not state or row["state_name"] == state)
            match_county = (not county or row["county_name"] == county)
            match_city = (not city or row["city"] == city)
            match_zip = (not zip_code or row["zip"] == zip_code)

            if match_state and match_city and match_county and match_zip:
                state_output = state or row["state_name"]
                county_output = county or row["county_name"]
                city_output = city or row["city"]
                zip_output = zip_code or row["zip"]
                
                return state_output, county_output, city_output, zip_output
            
        return None



def random_number_amount(): 
    rate = round(random.uniform(0, 0.1), 4)
    gross = round(random.uniform(50, 100000), 2)
    exempt = round(random.uniform(0, gross), 2)
    taxable = round((gross - exempt), 2)
    st_collected = round((taxable * rate), 2)

    percentage = round(random.uniform(0, 0.6), 4)
    tax_purchases = round((gross * percentage), 2)
    use_tax_accrued = round((tax_purchases * rate), 2)

    return gross, exempt, taxable, st_collected, tax_purchases, use_tax_accrued

def make_excel(subcategory, num_transaction, state=None, file_name=None, store_ids=None, county=None, city=None, zip_code=None):

    wb = Workbook()
    ws = wb.active
    ws.title = "Data import"

    headers = [
        "Store Id",
        "State",
        "County",
        "City",
        "Zip Code",
        "Subcategory",
        "Gross Sales",
        "Exempt sales",
        "Taxable sales",
        "Tax Collected",
        "Taxable purchases",
        "Use tax accrued",
    ]
    ws.append(headers)

    for t in range(num_transaction):
        gross, exempt, taxable, st_collected, tax_purchases, use_tax_accrued = random_number_amount()
        row = [
            store_ids[t % len(store_ids)],
            state,
            county,
            city,
            zip_code,
            subcategory,
            gross,
            exempt,
            taxable,
            st_collected,
            tax_purchases,
            use_tax_accrued,
        ]
        ws.append(row)

    output_name = file_name

    os.makedirs("output", exist_ok = True)

    path = os.path.join("output", output_name)
    wb.save(path)

    return path

