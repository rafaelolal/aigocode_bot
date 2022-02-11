import os
from dotenv import load_dotenv
import requests

import pymongo
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse


load_dotenv()
class MongoDB:

    client = pymongo.MongoClient(
        f"mongodb://aigocode:{os.getenv('MONGO_SECRET')}==@aigocode.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@aigocode@") \
        ['CodingComp']

@csrf_exempt
def auth_api(request):
    MY_API = 'https://rosa-mechanical-transsexual-reed.trycloudflare.com'

    if request.method == 'GET':
        code = request.GET.get('code')
        if code:
            url = "https://dev-mcy9agvp.jp.auth0.com/oauth/token"

            payload= f'code={code}&grant_type=authorization_code&client_id=XHVbOGXvGnLbDPh8ZO1IraTNTfgXPF6i&client_secret={os.getenv("CLIENT_SECRET")}&redirect_uri={MY_API}/another_endpoint'
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded'}

            response = requests.post(url, headers=headers, data=payload)

            ##################################################

            if "access_token" in response.json():
                url = "https://dev-mcy9agvp.jp.auth0.com/userinfo"

                payload={}
                headers = {
                'Authorization': f'Bearer {response.json()["access_token"]}'}

                response = requests.request("POST", url, headers=headers, data=payload)
                sub = response.json()["sub"]
                
                MongoDB.client['Users'].update_one({'token': sub}, {'$set': {'discordid': request.GET.get('id')}})

                return HttpResponseRedirect(reverse('api:discord'))

    return HttpResponse("AUTH API VIEW")

@csrf_exempt
def another_endpoint(request):
    return HttpResponse("ANOTHER ENDPOINT VIEW")

def discord(request):
    return HttpResponse("GO BACK TO DISCORD")