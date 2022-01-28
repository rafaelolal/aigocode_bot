import os
import sys
from dotenv import load_dotenv
import requests

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

cogs_path = '/home/thinkland/bots/aigocode_bot/cogs'
if cogs_path not in sys.path:
    sys.path.insert(1, cogs_path)

from aigocode_bot.cogs.mongodb import MongoDB

@csrf_exempt
def auth_api(request):
    MY_API = 'https://triumph-lover-frequent-resume.trycloudflare.com'
    print('---------')
    print(f'https://dev-mcy9agvp.jp.auth0.com/authorize?response_type=code&scope=openid%20profile&state=STATE&client_id=XHVbOGXvGnLbDPh8ZO1IraTNTfgXPF6i&redirect_uri={MY_API}?id=123456',
        'user link')
    print('---------')

    if request.method == 'GET':
        code = request.GET.get('code')
        if code:
            url = "https://dev-mcy9agvp.jp.auth0.com/oauth/token"

            load_dotenv()
            payload= f'code={code}&grant_type=authorization_code&client_id=XHVbOGXvGnLbDPh8ZO1IraTNTfgXPF6i&client_secret={os.getenv("CLIENT_SECRET")}&redirect_uri={MY_API}/another_endpoint'
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.post(url, headers=headers, data=payload)

            ##################################################

            url = "https://dev-mcy9agvp.jp.auth0.com/userinfo"

            payload={}
            headers = {
            'Authorization': f'Bearer {response.json()["access_token"]}',
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            sub = response.json()["sub"].replace("|", "-")

    if request.GET.get('ID'):
        return HttpResponse("GO BACK TO DISCORD")

    return HttpResponse("AUTH API VIEW")

@csrf_exempt
def another_endpoint(request):
    return HttpResponse("ANOTHER ENDPOINT VIEW")