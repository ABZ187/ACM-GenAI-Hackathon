import os
import time
from collections import Counter

import numpy as np
import pandas as pd
import sqlalchemy
from groq import Groq
from openai import OpenAI

engine = sqlalchemy.create_engine("sqlite:///data.db")
api_key = api_key
client = Groq(api_key=api_key)
MODEL_INFERENCES_TIMES = 3

def read_sql(query):
    print(pd.read_sql(query, engine))
def get_query_from_llm(question):
    start = time.time()
    prompt = """
    ### INSTRUCTION: You are provided two sql tables. It is an sqlite3 RDBMS. You have to write a sql query to read the tables according to the query. Do not join the tables unless a relation is explicitly mentioned between 'political_party_name' and 'name_of_purchaser'. Only output the SQL query not any other text. Refer the examples.  ###SQL_TABLES: TABLE_1_SUMMARY: Database of denominations/money, encashed by the political parties. TABLE_1_SCHEMA: table name:'bonds_encashed_by_political_parties', columns['date_of_encashment': the day on which denominations are encashed by political party, 'political_party_name' : name of the political party, 'bond_number' : bond number,'denominations': amount or money. TABLE_2_SUMMARY: Database of denominations/money, paid/donated by individual and comapanies to political parties. TABLE_2_SCHEMA: table name:'bonds_purchased_by_individuals', columns['date_of_purchase': the day on which denominations are purchased by the company, 'name_of_purchaser' : name of the company who purchased the bond, 'bond_number' : bond number,'denominations': amount or money. ###EXAMPLE_1:[Input- 'What is the total bond amount enchased by TELUGU DESAM PARTY on 12th April 2019?'; Output- SELECT SUM(denominations) FROM bonds_encashed_by_political_parties WHERE date_of_encashment = '2019-04-12' AND political_party_name = 'TELUGU DESAM PARTY';] ###EXAMPLE_2:[Input- What is the total amount received by AAM AADMI PARTY from DR. MANDEEP SHARMA in the year 2022?  Output- SELECT SUM(denominations) AS total_amount_received FROM ( SELECT denominations FROM bonds_encashed_by_political_parties WHERE political_party_name = 'AAM AADMI PARTY' AND strftime('%Y', date_of_encashment) = '2022' INTERSECT SELECT denominations FROM bonds_purchased_by_individuals WHERE name_of_purchaser = 'DR. MANDEEP SHARMA'   AND strftime('%Y', date_of_purchase) = '2022') AS combined_data;]
    """
    print(question.upper())
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"###INPUT: {question.upper()}. ###OUTPUT: "},
        ],
        model="llama3-70b-8192",
    )
    print("Time to complete query: ", time.time() - start)
    print()
    output = chat_completion.choices[0].message.content
    return output


def chat_response(question):
    model_ans = []
    for count in range(MODEL_INFERENCES_TIMES):
        try:
            model_answers = []
            query = get_query_from_llm(question)
            
            response = pd.read_sql(query, engine)
            print(query,response)
            model_ans.append(response.values[0][0])
        except Exception as e:
            print(f"Error: syntax incorrect, generating again:")
            if count == 3:
                return e
    model_ans = dict(Counter(model_ans))
    max_occurence_index = list(model_ans.values()).index(max(list(model_ans.values())))
    max_occurence_key = list(model_ans.keys())[max_occurence_index]
    return max_occurence_key


if __name__ == "__main__":
    get_query_from_llm("", [])
