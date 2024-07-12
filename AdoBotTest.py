import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os


#load Discord Token
load_dotenv()

# Define intents
intents = discord.Intents.all()

# Set Prefix for AdoBot
AdoBot = commands.Bot(command_prefix='!', intents=intents)


########################## LAUNCH BOT ##########################
@AdoBot.event
async def on_ready():
  # Set Custom Status for AdoBot
  await AdoBot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name="Ado - Value"))
  print('Ado has awoken!')

  try:
    synced = await AdoBot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)


################# WELCOME NEW MEMBER / AUTOROLE #################

@AdoBot.event
async def on_member_join(member):
  # Auto Assign Fan Role For New Member
  # fanRole -> Role ID
  fanRole = member.guild.get_role(1228608829130801163)
  # Give new member fanRole
  await member.add_roles(fanRole)

  # Send Welcome Message
  # Welcome Party Role -> Role ID
  welcomePartyRole = member.guild.get_role(1228608647387418634)  
  # Specify channel to send message (Welcome Channel) -> Channel ID
  channel = AdoBot.get_channel(1228611063142944838)
  # Send welcome message:
  await channel.send(f'***{welcomePartyRole.mention}, {member.mention} has joined! Welcome {member.global_name} <:AdoHeart:871816452695531520>***')




# ################# KARAOKE SLASH COMMANDS #################

# Vars

KARAOKE_CHANNEL_ID = 1259271581155459073
# TEST SERVER KARAOKE CHANNEL ID: 1261120957670752296

ADMIN_ROLE_ID = 1259272408880381972
# TEST SERVER ADMIN ID: 1261120559836561458

# Array to hold users and their songs for the queue
karaoke_queue = []
queue_active = False

# Function to check if a user has admin role
def is_admin(user):
    return any(role.id == ADMIN_ROLE_ID for role in user.roles)

@AdoBot.tree.command(name="startqueue")
@app_commands.default_permissions()
async def startqueue(interaction: discord.Interaction):
    # if interaction.channel.id != KARAOKE_CHANNEL_ID:
    #     await interaction.response.send_message(
    #         "This command can only be used in the karaoke channel.", ephemeral=True)
    #     return

    global queue_active
    if(queue_active):
      await interaction.response.send_message(f"There is already an active queue")
    else:
      queue_active = True
      await interaction.response.send_message(f"{interaction.user.mention} has started Karaoke! Use /joinqueue to join!")


@AdoBot.tree.command(name='joinqueue')
@app_commands.describe(your_song="What song do you want to sing?")
async def joinqueue(interaction: discord.Interaction, your_song: str):
    if interaction.channel.id != KARAOKE_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the Karaoke channel in https://discord.com/channels/1228558392897962054/1261120957670752296.", ephemeral=True)
        return

    # Check if the queue is active
    if not queue_active:
        await interaction.response.send_message("The karaoke queue has not started yet.", ephemeral=True)
        return

    user = interaction.user

    # Check if the user is already in the queue
    if any(user == entry['user'] for entry in karaoke_queue):
        await interaction.response.send_message(f"{user.mention}, you are already in the karaoke queue.", ephemeral=True)
    else:
        karaoke_queue.append({'user': user, 'song': your_song})
        if len(karaoke_queue) == 1:
            await interaction.response.send_message(f"{user.mention} has joined the karaoke queue with the song: {your_song}!\n{user.mention}, you're up!")
        else:
            await interaction.response.send_message(f"{user.mention} has joined the karaoke queue with the song: {your_song}!")

@AdoBot.tree.command(name="leavequeue")
async def leavequeue(interaction: discord.Interaction):
    if interaction.channel.id != KARAOKE_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the Karaoke channel.", ephemeral=True)
        return

    user = interaction.user
    for entry in karaoke_queue:
        if entry['user'] == user:
            karaoke_queue.remove(entry)
            await interaction.response.send_message(f"{user.mention} has left the karaoke queue.")
            return
    await interaction.response.send_message(f"{user.mention}, you are not in the karaoke queue.", ephemeral=True)

@AdoBot.tree.command(name="queuenext")
async def queuenext(interaction: discord.Interaction):
    if interaction.channel.id != KARAOKE_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the Karaoke channel.", ephemeral=True)
        return


    if not is_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to advance the queue.", ephemeral=True)
        return

    if karaoke_queue:
        karaoke_queue.pop(0)
        if karaoke_queue:
            next_person = karaoke_queue[0]['user']
            await interaction.response.send_message(f"It's {next_person.mention}'s turn now with the song: {karaoke_queue[0]['song']}!")
        else:
            await interaction.response.send_message("The karaoke queue is empty.")
    else:
        await interaction.response.send_message("The karaoke queue is empty.", ephemeral=True)

@AdoBot.tree.command(name="clearqueue")
async def clearqueue(interaction: discord.Interaction):
    if interaction.channel.id != KARAOKE_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the Karaoke channel.", ephemeral=True)
        return


    if not is_admin(interaction.user):
        await interaction.response.send_message("You do not have permission to clear the queue.", ephemeral=True)
        return

    global karaoke_queue, queue_active
    karaoke_queue = []
    queue_active = False
    await interaction.response.send_message("Karaoke queue has been cleared.")

@AdoBot.tree.command(name="queue")
async def printqueue(interaction: discord.Interaction):
    if interaction.channel.id != KARAOKE_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the Karaoke channel.", ephemeral=True)
        return


    if karaoke_queue:
        currently_up = karaoke_queue[0]['user'].display_name
        current_song = karaoke_queue[0]['song']
        queue_list = '\n'.join([f"{index + 1}. {entry['user'].display_name} - {entry['song']}" for index, entry in enumerate(karaoke_queue[1:])])
        message = f">>> **Currently Up:** {currently_up} with the song: {current_song}\n\n**In Queue:**\n{queue_list}"
        await interaction.response.send_message(message)
    else:
        await interaction.response.send_message("The karaoke queue is empty.")


# Run Bot Using Token
AdoBot.run(os.getenv('api_key'))