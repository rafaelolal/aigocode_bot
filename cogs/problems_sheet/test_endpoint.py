# Here is a sample JSON post that you might do:
# {
#     "key": "7e8e71c8-0308-4dcc-b09e-2b00dbec60c9",
#     "title": "a test problem",
#     "description": "test description",
#     "points": 100,
#     "difficulty": "hard",
#     "tags": "calculus, olympics, cool",
#     "answer": [[[0,1], [5,6], [7,8]], [[-2,-1], [-5, -4]]]
# }
 
# the endpoint is https://codingcomp.netlify.app/api/bot/postProblem
# If your request is valid and everything with the db goes well, the api will send you a 200 code as well as two objects, the message and the objectId. This objectId can be used for your spreadsheet and is the UID of the problem in the database.
# Here is a sample response.

# {
#     "message": "post successful",
#     "objectId": "61d10e71e651db0008d81233"
# }

import os
from dotenv import load_dotenv
import requests
from faker import Faker
import random

f = Faker()

load_dotenv()
url = 'https://codingcomp.netlify.app/api/bot/postProblem'

for i in range(40):
    problem = {
        "key": os.getenv("POST_API_KEY"),
        "title": str(i) + " " + f.paragraph(nb_sentences=1),
        "description": f.paragraph(nb_sentences=10),
        "points": random.choice([25, 50, 75, 100]),
        "difficulty": random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
        "tags": "USACO, " + random.choice(['recursive', 'divide and conquer', 'greedy', 'dynamic', 'brute force', 'backtracking']),
        "answer": [[[0,"1"], [5,"6"], [7,"8"]], [[-2,"-1"], [-5, "-4"]]]
    }

    response = requests.post(url, json=problem)
    print(response)