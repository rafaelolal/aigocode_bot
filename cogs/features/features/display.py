import validators

from discord.ext import commands
from discord import Colour, Embed
import discord

from .feature_cog import Feature

# types
from typing import Union
from discord.message import Message
from discord.member import Member
from discord.channel import TextChannel

from ...db.db_management import DB

class DisplayCommands(Feature):
    def __init__(self, bot):
        super().__init__(bot, 'display', DisplayView)
    
class DisplayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.creating_now = []

    async def interaction_check(self, interaction) -> bool:
        if interaction.user in self.creating_now:
            await interaction.response.send_message("Finish creating before trying again", ephemeral=True)
            return False

        return True

    @discord.ui.button(label="Display a Project", style=discord.ButtonStyle.blurple, custom_id='project_display')
    async def display(self, button, interaction):
        await interaction.response.defer()

        self.creating_now.append(interaction.user)

        user = interaction.user
        embed = await self.ask_to(user)
        self.creating_now.remove(interaction.user)
        if not embed:
            return

        project_msg = await interaction.channel.send(embed=embed, view=EditProjectView())
        DB.add_project_to_user(user.id, project_msg.id)

        await interaction.delete_original_message()
        await interaction.channel.send(content="\u200b", view=self)

        await user.send("Project created succesfuly!")

    @staticmethod
    async def ask_to(user: Member, embed: Embed = None) -> Union[Embed, None]:
        user = User(user)

        title = await user.ask(TitlePrompt, embed=embed)
        if not title:
            return

        description = await user.ask(DescriptionPrompt, embed=embed)
        if not description:
            return

        image = await user.ask(ImagePrompt, embed=embed)
        if not image:
            return

        link = await user.ask(LinkPrompt, embed=embed)
        if not link:
            return

        embed = DisplayView.create_embed(user.user, title, description, image, link)
        return embed

    @staticmethod
    def create_embed(user: Member, title: str, description: str, image: str, link: str) -> Embed:
        embed = Embed(title=title,
            description=description,
            url=link)

        embed.set_author(name=user.nick, icon_url=user.display_avatar.url)
        embed.set_footer(text="Do not forget to click on the project title to visit it!")
        embed.set_image(url=image)

        return embed

class User:
    def __init__(self, user):
        self.user = user

    async def ask(self, PromptType, embed: Embed = None) -> str:
        prompt = PromptType(editing=True if embed else False)
        request_msg = await prompt.send_request_msg_to(self.user)
        
        await prompt.wait()
        if prompt.is_confirmed is True:
            response_msg = await prompt.get_response(request_msg.channel)
            await prompt.acknowledge(self.user, response_msg, request_msg)

        elif prompt.is_confirmed is None:
            if prompt.prompt_type == 'link':
                return embed.url

            elif prompt.prompt_type == 'image':
                return embed.image.url

            return eval(f'embed.{prompt.prompt_type}')

        else:
            return

        if isinstance(prompt, ImagePrompt):
            return response_msg.attachments[-1].url

        return response_msg.content

class EditProjectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.editing_now = []

    async def interaction_check(self, interaction) -> bool:
        owner = DB.get_user_by_project(interaction.message.id)
        
        ID = 0
        if interaction.user.id != owner[ID] and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Only the owner can do this", ephemeral=True)
            return False

        elif interaction.user in self.editing_now:
            await interaction.response.send_message("Finish editing before trying again", ephemeral=True)
            return False

        return True

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.grey, custom_id='edit_button')
    async def edit(self, button, interaction):
        await interaction.response.defer()

        self.editing_now.append(interaction.user)

        project_msg = interaction.message
        embed = interaction.message.embeds[0]

        embed = await DisplayView.ask_to(interaction.user, embed=embed)
        if not embed:
            return
        
        await project_msg.edit(embed=embed)
        await interaction.user.send("Project editted succesfuly!")

        self.editing_now.remove(interaction.user)

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger, custom_id=f'delete_button')
    async def delete(self, button, interaction):
        DB.remove_project_from_user(interaction.user.id, interaction.message.id)
        await interaction.message.delete()

class Prompt(discord.ui.View):
    def __init__(self, prompt_type: str, editing: bool):
        super().__init__(timeout=None)
        self.is_confirmed = None
        self.prompt_type = prompt_type
        self.error_msg = f"Send a {self.prompt_type} before confirming"

        if editing:
            self.add_item(KeepButton())

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        if not await self.is_valid(interaction):
            await self.add_error_field(interaction)

        else:
            self.is_confirmed = True
            await self.disable(interaction)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button, interaction):
        embed = interaction.message.embeds[0]
        embed.title = 'Process Canceled'
        embed.description = 'I hope to see you displaying other projects!'
        embed.remove_footer()
        embed.clear_fields()
        embed.colour = Colour.light_grey()
        await interaction.message.edit(embed=embed)

        self.is_confirmed = False
        await self.disable(interaction)
    
    @staticmethod
    async def is_valid(interaction) -> bool:
        msg = await Prompt.get_response(interaction.channel)
        return msg != interaction.message

    async def add_error_field(self, interaction) -> None:
        embed = interaction.message.embeds[0]
        if 'Error' not in [field.name for field in embed.fields]:
            embed.add_field(name='Error',
                value=self.error_msg)

            embed.colour = Colour.red()

            await interaction.message.edit(embed=embed)

    async def acknowledge(self, user: Member, response: Message, request: Message) -> None:
        embed = request.embeds[0]

        if self.prompt_type not in ('image', 'link'):
            embed.add_field(name="You Entered",
                value=response.content)
        
        else:
            embed.url = request.content if self.prompt_type == 'link' else response.attachments[-1].url
            embed.add_field(name="You Entered",
                value="Click on the title to preview your response")
        
        embed.set_footer(text='Remember you can always edit this later')
        embed.colour = Colour.green()

        await request.edit(embed=embed)

    @staticmethod
    async def get_response(channel: TextChannel) -> Message:
        msgs = await channel.history(limit=1).flatten()
        msg = msgs[0]

        return msg

    async def send_request_msg_to(self, user: Member) -> Message:
        embed = Embed(title=self.prompt_type.capitalize(),
            description=f'Respond with the {self.prompt_type} of your project')
        embed.set_footer(text='If you make a mistake, edit or send a new message then confirm')
        embed.colour = Colour.blue()

        return await user.send(embed=embed, view=self)

    async def disable(self, interaction) -> None:
        for child in self.children:
            child.disabled = True

        self.stop()
        await interaction.message.edit(view=None)

class KeepButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.blurple, label='Keep')

    async def callback(self, interaction):
        await self.view.disable(interaction)

class TitlePrompt(Prompt):
    def __init__(self, editing):
        super().__init__("title", editing)

class DescriptionPrompt(Prompt):
    def __init__(self, editing):
        super().__init__("description", editing)

class ImagePrompt(Prompt):
    def __init__(self, editing):
        super().__init__("image", editing)

        self.error_msg = "Attach and send an image before confirming"

    async def is_valid(self, interaction) -> bool:
        msg = await self.get_response(interaction.channel)
        return msg != interaction.message and len(msg.attachments) != 0

class LinkPrompt(Prompt):
    def __init__(self, editing):
        super().__init__("link", editing)

        self.error_msg = 'Enter a valid "http" link before confirming'

    async def is_valid(self, interaction) -> bool:
        msg = await self.get_response(interaction.channel)
        return validators.url(msg.content) and msg != interaction.message

def setup(bot):
    bot.add_cog(DisplayCommands(bot))
    