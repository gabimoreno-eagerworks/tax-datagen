import random
import os
import re
import string
from generators.locations import fill_location
from openpyxl import Workbook



us_file = os.getenv("USZIPS_PATH", "data/uszips.csv")


BANK_NAMES = [
    "Chase",
    "Bank of America",
    "Wells Fargo",
    "Citibank",
    "U.S. Bank",
    "PNC Bank",
    "Capital One",
    "TD Bank",
    "Truist",
    "Fifth Third Bank",
    "First National Bank",
]

STREET_NAMES = [
    "Main St",
    "Oak Ave",
    "Maple Dr",
    "Commerce Blvd",
    "Industrial Pkwy",
    "Market St",
    "Cedar Ln",
    "Pine Rd",
    "Highland Ave",
    "River Rd",
    "Broadway",
    "Park Ave",
    "Lakeview Dr",
    "Hillside Rd",
    "Forest Ave",
    "Mountain Rd",
    "Valley Rd",
    "River Rd",
    "Highland Ave",
]

DBA_SUFFIXES = [
    "Stores",
    "Retail",
    "Trading",
    "Group",
    "Market",
    "Shop",
    "Company",
    "Enterprises",
    "Corporation",
]

OFFICER_TITLES = [
    "President",
    "Vice President",
    "Secretary",
    "CEO",
    "CFO",
    "COO",
    "CTO",
]

SECURITY_QUESTIONS = {
    "What is the name of your first pet?": ["Max", "Luna", "Fido", "Buddy", "Spot", "Buddy"],
    "What is the name of your first car?": ["Ford", "Mustang", "Camaro", "Corvette", "Porsche", "Tesla"],
    "What is the name of your first school?": ["Harvard", "Harvard University", "Yale University", "MIT", "Stanford University"],
    "What is the name of your first teacher?": ["Mr. Smith", "Mr. Smith", "Mrs. Smith", "Mrs. Johnson", "Mr. Williams"],
    "What is the name of your first friend?": ["John Doe", "John Doe", "Jane Doe", "Jim Smith", "Jill Johnson"],
}

FIRST_NAMES = [
    "John",
    "Jane",
    "Jim",
    "Jill",
    "Jack",
]

LAST_NAMES = [
    "Doe",
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Davis",
    "Miller",
    "Wilson",
    "Moore",
    "Taylor",
    "Anderson",
    "Thomas",
    "Jackson",
]


FILING_FREQUENCIES = [
    "Monthly",
    "Quarterly",
    "Annually",
]

SKIP_WORDS = {"llc", "inc", "corp", "co", "ltd", "the", "of", "and", "dba", "lp", "pc"}


def entity_words(entity_name):
    words = re.findall(r"[A-Za-z0-9]+", entity_name or "")
    meaningful = [word for word in words if word.lower() not in SKIP_WORDS]
    return meaningful or words

def make_short_name(entity_name):
    words = entity_words(entity_name)
    if not words:
        return "ENT"

    if len(words) == 1:
        return words[0][:8].upper()

    return "".join(word[0] for word in words).upper()[:8]


def make_dba(entity_name):
    words = entity_words(entity_name)
    if not words:
        base_name = "Entity"
    else:
        base_name = words[0].title()

    return f"{base_name} {random.choice(DBA_SUFFIXES)}"


def random_fein():
    return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"


def random_routing_number():
    digits = [random.randint(0, 9) for _ in range(8)]
    checksum = (
        3 * (digits[0] + digits[3] + digits[6])
        + 7 * (digits[1] + digits[4] + digits[7])
        + (digits[2] + digits[5])
    ) % 10
    digits.append((10 - checksum) % 10)
    return "".join(str(digit) for digit in digits)

def random_account_number():
    length = random.randint(8, 12)
    return "".join(str(random.randint(0, 9)) for _ in range(length))

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_officer_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_officer_title():
    return random.choice(OFFICER_TITLES)

def random_officer_ssn():
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

def random_officer_dob():
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = random.randint(1960, 2000)
    return f"{month:02d}/{day:02d}/{year}"

def random_officer_drivers_license():
    return f"{random.randint(100000000, 999999999)}"

def random_address(entity_state):

    number = random.randint(100, 9999)
    street_name = random.choice(STREET_NAMES)

    location = fill_location(us_file, state=entity_state)

    if not location:
        address =  f"{number} {street_name}"
    else:
        state, county, city, zip_code = location
        address = f"{number} {street_name}, {city}, {state} {zip_code}"

    return address


def make_entity_email(short_name):
    slug = re.sub(r"[^a-z0-9]", "", (short_name or "entity").lower()) or "entity"
    return f"info@{slug}.com"


def random_phone():
    area = random.randint(200, 999)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)
    return f"{area}-{prefix}-{line}"


def random_tax_id():
    prefix = random.choice(["ST", "UT", "SU", "REG"])
    return f"{prefix}-{random.randint(10000000, 99999999)}"


def normalize_states(entity_state):
    if not entity_state:
        return [""]
    if isinstance(entity_state, str):
        return [entity_state]
    return list(entity_state) or [""]

def naics_number():
    return f"{random.randint(100000, 999999)}"

def random_strn_account_user_id():
    return f"{random.randint(1000000000, 9999999999)}"

def random_strn_account_password():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(12))

def random_strn_account_pin():
    return f"{random.randint(1000000000, 9999999999)}"

def random_strn_account_security_question():
    question = random.choice(list(SECURITY_QUESTIONS.keys()))
    answer = random.choice(SECURITY_QUESTIONS[question])
    return question, answer

def random_outlet_number():
    return f"{random.randint(1000000000, 9999999999)}"


def create_filing_calendar_data(entity_name, entity_state):
    short_name = make_short_name(entity_name)
    dba = make_dba(entity_name)
    security_question, security_answer = random_strn_account_security_question()
    return [
        entity_name, # Entity Name
        short_name, # Short Name
        dba, # DBA
        random_fein(), # FEIN Number
        naics_number(), # NAICS Number
        random.choice(BANK_NAMES), # Bank Name
        random_routing_number(), # Routing Number
        random_account_number(), # Account Number
        random_name(), # Name on Account
        random_address(entity_state), # Bank Address
        random_address(entity_state), # Entity Address
        entity_state, # Entity State
        make_entity_email(short_name), # Entity Email
        random_phone(), # Entity Phone Number
        random_officer_name(), # Officer Name
        random_address(entity_state), # Officer Home Address
        random_officer_title(), # Officer Title
        random_phone(), # Officer Phone Number  
        random_officer_ssn(), # Officer SSN Number
        random_officer_dob(), # Officer DOB
        random_officer_drivers_license(), # Officer Drivers License
        entity_state, # State Name
        random_tax_id(), # Sales Tax Registration Number
        random_tax_id(), # Consumer Use Tax Number
        random_tax_id(), # Sellers Use Tax Number
        random_strn_account_user_id(), # STRN Account User ID
        random_strn_account_password(), # STRN Account Password
        random_strn_account_pin(), # STRN Account PIN
        security_question, # STRN Account Security Question
        security_answer, # STRN Account Security Answer
        random_outlet_number(), # Outlet Number
        random.choice(FILING_FREQUENCIES), # Filing Frequency
    ]


def make_filing_calendar(entity_names, entity_states, file_name=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Filing Calendar"

    headers = [
        "Entity Name",
        "Short Name",
        "DBA",
        "FEIN Number",
        "NAICS Number",
        "Bank Name",
        "Routing Number",
        "Account Number",
        "Name On Account",
        "Bank Address",
        "Entity Address",
        "Entity State",
        "Entity Email",
        "Entity Phone Number",
        "Officer Name",
        "Officer Home Address",
        "Officer Title",
        "Officer Phone Number",
        "Officer SSN Number",
        "Officer DOB",
        "Officer Drivers License",
        "State Name", # Entity State - This is the state that should be different for each row
        "Sales Tax Registration Number",
        "Consumer Use Tax Number",
        "Sellers Use Tax Number",
        "STRN Account User ID",
        "STRN Account Password",
        "STRN Account PIN",
        "STRN Account Security Question",
        "STRN Account Security Answer",
        "Outlet Number",
        "Filing Frequency",
    ]
    ws.append(headers)
    raw_list = []

    for i, entity_name in enumerate(entity_names):
        if i < len(entity_states):
            states = normalize_states(entity_states[i])
        else:
            states = [""]

        first_state = states[0]
        entity_row = create_filing_calendar_data(entity_name, first_state)

        for state in states:
            row = entity_row.copy()
            row[21] = state
            raw_list.append(row)

    ordered_list = sorted(raw_list, key=lambda x: (not x[0], str(x[0]).lower()))
    for row in ordered_list:
        ws.append(row)

    output_name = file_name 
    os.makedirs("output", exist_ok=True)
    path = os.path.join("output", output_name)
    wb.save(path)

    return path
