import requests

problems = requests.get("https://www.aigocode.org/api/queries/allproblems")
print(problems.json()[-1])