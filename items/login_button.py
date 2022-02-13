import discord

class LoginButton(discord.ui.Button):
    
    MY_API = 'http://discord.thinkland.ai/api/'
    AUTH_API = f'https://dev-mcy9agvp.jp.auth0.com/authorize?response_type=code&scope=openid%20profile&state=STATE&client_id=XHVbOGXvGnLbDPh8ZO1IraTNTfgXPF6i&redirect_uri={MY_API}?id='

    def __init__(self, member_id):
        super().__init__(style=discord.ButtonStyle.green, label='Login', url=self.AUTH_API+str(member_id))