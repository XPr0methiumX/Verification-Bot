import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.default()
intents.members = True
client = commands.AutoShardedBot(command_prefix= '!' , pm_help=True, case_insensitive=True, intents=intents, owner_id=547322851146072086, activity=discord.Game(name="Verifying people in your server!"), status=discord.Status.online)

for filename in os.listdir('./Cogs'):
    if filename.endswith('.py'):
        try:
            client.load_extension(f'Cogs.{filename[:-3]}')
        except Exception:
            raise Exception
            
async def verifier():
  await client.wait_until_ready()
  dbconnect = sqlite3.connect("verification.db")
  client.db = dbconnect.cursor()
  client.db.execute("CREATE TABLE IF NOT EXISTS data (guild_id int, channel_id int, role_id int, PRIMARY KEY (guild_id))")
  
client.loop.create_task(verifier())
client.run(TOKEN)
  
  
  
  
