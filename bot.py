import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand # pip install -U discord-py-slash-command
from discord_slash.utils.manage_commands import create_option
from keep_alive import keep_alive
from db.db import db

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

activity = discord.Activity(
	name="calm music", 
	type=discord.ActivityType.listening
	)
bot = commands.Bot(
	command_prefix='~',
	activity=activity,
	status=discord.Status.idle,
	afk=False,
    help_command=None
    )

slash = SlashCommand(bot, sync_commands=True) # Declares slash commands through the client.

@bot.event
async def on_ready():
    bot.load_extension('jishaku')
    print('We have logged in as {0.user}'.format(bot))

def guild_ids():
    return db.get("", "guilds", []) # Put your server ID in this array.

@bot.command(
	name='help', 
	help="Shows the bot's help command."
	)
async def help(ctx):
	embed = discord.Embed(
		title = 'Anon Help', 
		description = """Anon uses slash commands!
		To start using slash commands, use `/setup`.
		A list of commands will appear when using `/`"""
	)
	await ctx.send(embed=embed)

@bot.command(
	name='setup', 
	help="Sets up the server for Anon."
	)
async def setup(ctx):
	guilds = guild_ids
	if str(ctx.guild.id) not in guilds:
		guilds.append(str(ctx.guild.id))
		db.set("", "guilds", guilds)
		await ctx.send("Added guild to Anon! You can now start using slash commands.")
	else:
		await ctx.send("This guild is already set up with Anon!")


@slash.slash(
    name="ping", 
    description="Displays the bot's latency in ms.",
    guild_ids=guild_ids)
async def _ping(ctx): # Defines a new "context" (ctx) command called "ping."
    latency = round(bot.latency * 1000, 2)
    await ctx.send(f"Pong! ({latency} ms)", hidden=True)

@slash.slash(
    name="anon", 
    description="Sends an anonymous message.",
    guild_ids=guild_ids,
    options=[
                create_option(
                    name="message",
                    description="The message you want to send.",
                    option_type=3,
                    required=True
                ),
                create_option(
                    name="name",
                    description="The username you want to use.",
                    option_type=3,
                    required=False
                )
            ]
    )
async def _anon(ctx, message : str, name : str = None):
    if name != None:
        v_name = name
    else:
        v_name = db.get(f"users/{ctx.author.id}", "name", "Anonymous")

    await ctx.send(f"Message sent as **{v_name}**!", hidden=True)
    await ctx.channel.send(f"**{v_name}:** {message}")

@slash.slash(
    name="name", 
    description="Sets your default anonymous name.",
    guild_ids=guild_ids,
    options=[
                create_option(
                    name="name",
                    description="The new default name you want.",
                    option_type=3,
                    required=True
                )
            ]
    )
async def _name(ctx, name : str):
    db.set(f"users/{ctx.author.id}", "name", name)

    await ctx.send(f"Set your anonymous name to **{name}**!", hidden=True)

# ctx.channel.send = anonymous
# .send(*message, **hidden=True) = hide msg

keep_alive()
bot.run(TOKEN)