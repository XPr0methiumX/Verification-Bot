import discord
import sqlite3
from discord.ext import commands
from discord import Embed
from multicolorcaptcha import CaptchaGenerator

class Verifier(commands.Cog):
    def __init__(self, bot):
      self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
      print("Verifier Cog Ready!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
      dbconnect = sqlite3.connect('verification.db')
      cursor = dbconnect.cursor()
      RECORDS = cursor.execute("SELECT guild_id FROM data WHERE guild_id = ?",(member.guild.id,)).fetchall()
      for record in RECORDS:
        if record[0] == member.guild.id:
          role = discord.utils.get(member.guild.roles, name = "Unverified")
          await member.add_roles(role)

    @commands.command(aliases=['cap', 'verify'])
    async def captcha(self, ctx):
      dbconnect = sqlite3.connect('verification.db')
      cursor = dbconnect.cursor()
      record = cursor.execute("SELECT role_id FROM data WHERE guild_id = ?",(ctx.guild.id,)).fetchall()
      for record in record:
        role_id = int(record[0])
      CAPCTHA_SIZE_NUM = 2
      generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)
      captcha = generator.gen_captcha_image(difficult_level=3) 
      image = captcha["image"] 
      characters = captcha["characters"]
      image.save("captcha.png", "png")
      f = discord.File("captcha.png", filename="captcha.png") 
      embed = discord.Embed(title='Captcha', description = f'Complete the captcha below to get verified.', color=ctx.author.color , timestamp=ctx.message.created_at) 
      embed.set_image(url="attachment://captcha.png")
      embed.set_footer(text=f"Requested by {ctx.message.author.display_name}")
      await ctx.send(file=f, embed=embed)
      def check(m):
       return m.author == ctx.message.author and m.channel == ctx.message.channel 
      try:
       verif = await self.bot.wait_for('message', timeout=40, check=check)
      except TimeoutError:
        await ctx.send("You didn't answer the captcha in Time. Please try again.")
        return
      if verif.content == characters: 
       role = discord.utils.get(ctx.guild.roles, name = "Unverified")
       await ctx.author.remove_roles(role)
       addrole = ctx.guild.get_role(role_id)
       await ctx.author.add_roles(addrole)
       await ctx.send("<a:success:858033393971232798> You have been verified.")
      elif verif.content != characters:
       await ctx.send("❌ You were not verified because your answer didn't match the captcha text, try again.")
    
    @commands.command(aliases=['sv', 'set-verifier'])
    async def set_verifier(self, ctx):
        dbconnect = sqlite3.connect('verification.db')
        cursor = dbconnect.cursor()
        questions=["Which channel would you like the members to view when they join the server?",
                    "What Role should I give on successful verification?"]
        answers = []
        def check(m):
              return m.author == ctx.author and m.channel == ctx.channel
          
        for i, question in enumerate(questions):
              embed = Embed(title=f"Question {i + 1}",
                            description=question, color = discord.Color.blurple())
              await ctx.send(embed=embed)
              try:
                  message = await self.bot.wait_for('message', timeout=120, check=check)
              except TimeoutError:
                  await ctx.send("You didn't answer the questions in Time. Please try again.") 
                  return
              answers.append(message.content)

        try:
              channel_id = int(answers[0][2:-1])
        except:
              await ctx.send(f"The Channel provided was wrong. The channel should be like {ctx.channel.mention}")
              return 
        try:
         chanel = self.bot.get_channel(channel_id)
        except:
          await ctx.send(f"The Channel provided was wrong. The channel should be like {ctx.channel.mention}")
          return 
        try:
          role_id = int(answers[1][3:-1])
        except:
          return await ctx.send(f"The Role provided was wrong.")
        process = await ctx.send("Setting everything up... :gear:")
        try:
         role = discord.utils.get(ctx.guild.roles, id = role_id)
        except:
          return await ctx.send("The Role provided was wrong.")
        cursor.execute('''INSERT OR REPLACE INTO data(channel_id, guild_id) VALUES(?,?)''', (int(chanel.id), ctx.guild.id))
        cursor.execute('''INSERT OR REPLACE INTO data(role_id, guild_id) VALUES(?,?)''', (int(role.id), ctx.guild.id))
        unverifiedRole = discord.utils.get(ctx.guild.roles, name="Unverified")
        if not unverifiedRole:
              await ctx.send("I wasn't able to find a Unverified role in this guild so I've created one! Please drag it to the top of the role list below my role.")
              unverifiedRole = await ctx.guild.create_role(name="Unverified")

              for channel in ctx.guild.channels:
                    await channel.set_permissions(unverifiedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
                    await chanel.set_permissions(unverifiedRole, speak=True, send_messages=True, read_message_history=True, read_messages=True, manage_messages=False)
        for channel in ctx.guild.channels:
                    await channel.set_permissions(unverifiedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
                    await chanel.set_permissions(unverifiedRole, speak=True, send_messages=True, read_message_history=True, read_messages=True, manage_messages=False)
        await process.edit(content = "<a:success:858033393971232798> I've set everything up for you!")
        dbconnect.commit()

    @commands.command(aliases=['disable-verifier', 'dv'])
    async def disable_verifier(self, ctx):
     unverifiedRole = discord.utils.get(ctx.guild.roles, name="Unverified")
     dbconnect = sqlite3.connect('verification.db')
     cursor = dbconnect.cursor()
     try:
      if not unverifiedRole:
        return await ctx.send("❌ The verifier has not been set up in this guild.")
      if unverifiedRole:
        cursor.execute("DELETE FROM data WHERE guild_id = ?", (ctx.guild.id,))
        await unverifiedRole.delete()
        await ctx.send("<a:success:858033393971232798> The verifier has been disabled in this guild.")
     except:
       return
     await dbconnect.commit()

def setup(bot):
  bot.add_cog(Verifier(bot))
