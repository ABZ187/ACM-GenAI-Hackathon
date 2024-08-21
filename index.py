import io
import os
import re

import pandas as pd
import sqlalchemy
from PyPDF2 import PdfReader

engine = sqlalchemy.create_engine("sqlite:///data.db")


def extract_name_of_purchaser(text):
    occurrences = [m.start() for m in re.finditer(r"/(\d{4})", text)]
    if len(occurrences) < 3:
        return None  # Less than 3 occurrences found

    # Get the position of the third occurrence of "/2019"
    third_occurrence_index = occurrences[2]

    # Extract text starting from the third occurrence
    text_from_third_occurrence = text[
        third_occurrence_index + 5 :
    ]  # +5 to skip "/2019"

    # Regex pattern to match text up to a two-letter word
    pattern = r"(.*?)(?=\b\d{1,5}\b)"
    match = re.search(pattern, text_from_third_occurrence)
    if match:
        return " ".join(match.group(1).strip().split(" ")[:-1])
    else:
        return None


def extract_party_name(text):
    # Regex pattern to match text between a number and '**'
    pattern = r"/(\d{4})(.*?)(\*\*)"
    matches = re.findall(pattern, text)
    # Extracting the text part (the second group in the pattern)
    extracted_texts = [match[1].strip() for match in matches]
    return extracted_texts


def pdf_bonds_encashed_by_political_parties_pdf():
    date_of_encashment = []
    political_party_name = []
    bond_number = []
    denominations = []

    with open("files/bonds_encashed_by_political_parties.pdf", "rb") as f:
        pdf_data = f.read()
    with io.BytesIO(pdf_data) as open_pdf_file:
        doc_reader = PdfReader(open_pdf_file)

        for page in doc_reader.pages:
            page_details = page.extract_text()
            page_details = page_details.split("\n")
            page_details = page_details[5:]  # skip the headers
            page_details = page_details[:-1]  # skip the last page details
            for row in page_details:
                party_name = extract_party_name(row)
                row = row.replace(party_name[0] + " ", "").split(" ")
                date_of_encashment.append(row[1])
                political_party_name.append(party_name[0])
                bond_number.append(row[4])
                denominations.append(int(row[5].replace(",", "")))

    df = pd.DataFrame(
        {
            "date_of_encashment": date_of_encashment,
            "political_party_name": political_party_name,
            "bond_number": bond_number,
            "denominations": denominations,
        }
    )
    df.to_csv("files/bonds_encashed_by_political_parties.csv")


def parse_bonds_purchased_by_individuals_pdf():
    date_of_purchase = []
    name_of_purchaser_list = []
    bond_number = []
    denominations = []
    with open("files/bonds_purchased_by_individuals.pdf", "rb") as f:
        pdf_data = f.read()
    with io.BytesIO(pdf_data) as open_pdf_file:
        doc_reader = PdfReader(open_pdf_file)
        for page in doc_reader.pages:
            page_details = page.extract_text()
            page_details = page_details.split("\n")
            page_details = page_details[3:]  # skip the headers
            page_details = page_details[:-1]  # skip the last page details
            try:
                for row_ in page_details:
                    name_of_purchaser = extract_name_of_purchaser(row_)
                    row = row_.replace(name_of_purchaser + " ", "").split(" ")
                    date_of_purchase.append(row[3])
                    name_of_purchaser_list.append(name_of_purchaser)
                    bond_number.append(row[6])
                    denominations.append(int(row[7].replace(",", "")))
                    status = row[10]
            except Exception as e:
                print("errror: ", e)
                print(row)

    df = pd.DataFrame(
        {
            "date_of_purchase": date_of_purchase,
            "name_of_purchaser_list": name_of_purchaser_list,
            "bond_number": bond_number,
            "denominations": denominations,
            "status": status,
        }
    )
    df.to_csv("files/bonds_purchased_by_individuals.csv")


def bonds_encashed_by_political_parties_to_db():
    df = pd.read_csv("files/bonds_encashed_by_political_parties.csv")
    df["bond_number"] = df["bond_number"].astype(int)
    df["denominations"] = df["denominations"].astype(str)
    df["denominations"] = df["denominations"].astype(float)
    # change datatype to date
    df["date_of_encashment"] = pd.to_datetime(df["date_of_encashment"])
    df["date_of_encashment"] = df["date_of_encashment"].dt.date
    # remove column
    df = df.drop("Unnamed: 0", axis=1)
    df.to_sql(
        "bonds_encashed_by_political_parties", engine, if_exists="replace", index=False
    )


def bonds_purchased_by_individuals_to_db():
    df2 = pd.read_csv("files/bonds_purchased_by_individuals.csv")
    df2.rename(columns={"name_of_purchaser_list": "name_of_purchaser"}, inplace=True)
    df2["bond_number"] = df2["bond_number"].astype(int)
    df2["denominations"] = df2["denominations"].astype(str)
    df2["denominations"] = df2["denominations"].astype(float)
    # change datatype to date
    df2["date_of_purchase"] = pd.to_datetime(df2["date_of_purchase"])
    df2["date_of_purchase"] = df2["date_of_purchase"].dt.date
    # remove column
    df2 = df2.drop("Unnamed: 0", axis=1)
    df2.to_sql(
        "bonds_purchased_by_individuals", engine, if_exists="replace", index=False
    )


if "bonds_purchased_by_individuals.csv" not in os.listdir(
    "files"
) or "bonds_encashed_by_political_parties.csv" not in os.listdir("files"):
    pdf_bonds_encashed_by_political_parties_pdf()
    parse_bonds_purchased_by_individuals_pdf()
    
# to db
bonds_encashed_by_political_parties_to_db()
bonds_purchased_by_individuals_to_db()
