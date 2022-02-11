import requests

json = {
    # TODO replace this with a env variable
    "key": '7e8e71c8-0308-4dcc-b09e-2b00dbec60c9',
    "icode": "print('hello')",
    "ilanguage": "python3",
    "iversion": "3.9.4",
    "idiscordid": "250782339758555136",
    "problemid": "61fe72fe83d30c0009a33899",
    "iextension": "py"
}

response = requests.post("https://codingcomp.netlify.app/api/bot/solve", json=json)
print(response.text)