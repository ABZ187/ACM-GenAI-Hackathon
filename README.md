# ACM-hackathon: Development of a PDF reading application using LLMs
This repository contains submission code for the ACM'24 IIT'GN hackathon.
The code is divided into two phases:
1. **Parsing of the PDF contents to a RDBMS**
2. **Running the frontend to query from the PDF contents**

Before getting started, create a virtual environment and install the requirements from the `requirements.txt` (Python 3.8 or higher).

### 1. Parsing the PDF Files
The PDF files reside in the `files/` folder:
- `bonds_encashed_by_political_parties.pdf`
- `bonds_purchased_by_individuals.pdf`

Run the command:
```sh
python index.py
```
 it will parse the contents of the pdf file and store it a sqlite database
 
 ### 2. Querying the PDF Contents
 To start querying the PDF contents, run the command:
 ```sh
chainlit run chatbot.py
```
An internet browser will open (if it doesn't, type http://localhost:8000/). A chatbot interface will be displayed where you can start writing your queries.

## Bulk Questions
To get answers for bulk questions:

- Write all the questions in a questions.txt file in the files/ folder.
- Run the command:
 ```sh
python bulk_queries.py
```
The answers will be generated into an answers.txt file in the files/ folder.

