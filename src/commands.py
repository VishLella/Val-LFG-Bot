import discord
from discord import app_commands, ui
from discord.ui import Button, View
from .constants import GAME_SERVERS
from .player import Player
from .utils import get_user_region, get_user_rank


class JoinVoiceChannelButton(Button):
    def __init__(self, channel: discord.VoiceChannel, user_ids):
        super().__init__(label="Join Voice Channel", style=discord.ButtonStyle.primary)
        self.channel = channel
        self.user_ids = user_ids

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
                f"To join the voice channel {self.channel.name}, click this link: "
                f"https://discord.com/channels/{interaction.guild.id}/{self.channel.id}",
                ephemeral=True
        )
        # if interaction.user.id in self.user_ids:                               # uncomment to restrict users in vc's
        #     await interaction.response.send_message(
        #         f"To join the voice channel {self.channel.name}, click this link: "
        #         f"https://discord.com/channels/{interaction.guild.id}/{self.channel.id}",
        #         ephemeral=True
        #     )
        # else:
        #     await interaction.response.send_message("This button is not for you.", ephemeral=True)

class JoinVoiceChannelView(View):
    def __init__(self, channel: discord.VoiceChannel, user_ids):
        super().__init__()
        self.add_item(JoinVoiceChannelButton(channel, user_ids))

class ServerSelect(ui.Select):
    def __init__(self, servers):
        options = [discord.SelectOption(label=server, value=server) for server in servers]
        super().__init__(placeholder="Please choose your preferred servers!", min_values=1, max_values=len(servers), options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_servers = self.values
        member = interaction.user
        region = get_user_region(member) # Gets the user's region
        rank = get_user_rank(member) #change to recieve the integer value from the RANKS const list

        player = Player(member.id, member.display_name, region, rank, selected_servers)

        bot = interaction.client
        #inQueue = any(p.name == member.display_name for p in bot.lfg_queue)
        if member.id in bot.lfg_queue:
            await interaction.response.send_message(f"{member.display_name} is already in the queue or has already chosen servers. To reselect servers, please /leave and rejoin the queue", ephemeral=True)
            return
        
        #bot.lfg_queue.append(player)
        await bot.add_to_queue(player)
        await interaction.response.send_message(f"{member.display_name} has joined the LFG queue!", ephemeral=True)
        await bot.check_queue()

class ServerSelectView(ui.View):
    def __init__(self, servers):
        super().__init__()
        self.add_item(ServerSelect(servers))

@app_commands.command(name="queue", description="Join the LFG queue!")
async def queue(interaction: discord.Interaction):
    member = interaction.user
    region = get_user_region(member)
    rank = get_user_rank(member)

    if not region and not rank:
        await interaction.response.send_message(f"You don't have a region and rank role. Please select one in <#{1289834896390357025}>.", ephemeral=True)
        return
    elif not region:
        await interaction.response.send_message(f"You don't have a region role. Please select one in <#{1289834896390357025}>.", ephemeral=True)
        return
    elif not rank:
        await interaction.response.send_message(f"You don't have a rank role. Please select one in <#{1289834896390357025}>.", ephemeral=True)
        return
    
    available_servers = GAME_SERVERS.get(region, [])

    view = ServerSelectView(available_servers)
    await interaction.response.send_message("Select your game servers:", view=view, ephemeral=True)

# Define Slash Command for leave
@app_commands.command(name="leave", description="Leave the LFG queue")
async def leave(interaction: discord.Interaction):
    bot = interaction.client
    user_id = interaction.user.id

    if user_id in bot.lfg_queue:
        del bot.lfg_queue[user_id]
        await interaction.response.send_message(f"{interaction.user.display_name} has left the LFG queue.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.display_name} is not in the LFG queue.", ephemeral=True)

    # bot.lfg_queue = [player for player in bot.lfg_queue if player.user_id != user_id]
    # await interaction.response.send_message(f"{interaction.user.display_name} has left the LFG queue.", ephemeral=True)

@app_commands.command(name="hi", description="Lists players in the LFG queue")
@app_commands.default_permissions(administrator=True)
async def hi(interaction: discord.Interaction):
    bot = interaction.client
    if not bot.lfg_queue:  # Check if the queue is empty
        await interaction.response.send_message("The queue is empty.", ephemeral=True)
    else:
        text = ""
        players = list(bot.lfg_queue.values())
        for player in players:
            text += f"{player['player'].name}: {player['player'].servers}: {player['player'].rank}"
        await interaction.response.send_message(text)
        # queue_list = ', '.join([player.name for player in lfg_queue])  # List the player names
        # await interaction.response.send_message(f"Queue: {queue_list}", ephemeral=True)

@app_commands.command(name="test_permissions", description="Test if the bot has permission to create voice channels")
@app_commands.default_permissions(administrator=True)
async def test_permissions(interaction: discord.Interaction):
    guild = interaction.guild
    try:
        voice_channel = await guild.create_voice_channel('Test VC')
        await interaction.response.send_message("Voice channel created successfully.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to create voice channels.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

# This function will be imported and called in bot.py
def setup_commands(bot):
    bot.tree.add_command(hi)
    bot.tree.add_command(test_permissions)
    bot.tree.add_command(queue)
    bot.tree.add_command(leave)
    # Add other commands here as you create them