from query import chat_response

questions_filename = "files/questions.txt"
output_filename = "files/answers.txt"

with open(questions_filename, "rb") as f:
    questions = f.read().decode().strip()

response = ""
questions = questions.split("\n")
for count,question in enumerate(questions):
    response += str(count+1)+") " + str(chat_response(question)) + "\n"

with open(output_filename, "w") as f:
    f.write(response)
