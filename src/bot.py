import discord
from discord.ext import commands, tasks
from .constants import RANKS
from .commands import setup_commands, JoinVoiceChannelView
from datetime import datetime, timedelta



class LFGBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True
        super().__init__(command_prefix="/", intents=intents)
        self.add_listener(self.on_voice_state_update, 'on_voice_state_update')

        #self.lfg_queue = []
        #self.created_voice_channels = []
        self.voice_channels = {}
        self.lfg_queue = {}

    
    async def add_to_queue(self, player):
        self.lfg_queue[player.user_id] = {
            'player': player,
            'joined_at': datetime.now()
        }

    @tasks.loop(seconds=60)
    async def check_queue_timeouts(self):
        now = datetime.now()
        for user_id, info in list(self.lfg_queue.items()):
            if now - info['joined_at'] >= timedelta(minutes=60):
                del self.lfg_queue[user_id]
                #notify them that they've been removed?
                user = self.get_user(user_id)
                if user:
                    try:
                        await user.send("You have been removed from the LFG queue since no teammate was found.")
                    except discord.errors.Forbidden:
                        pass # Can't send a DM to this user
    
    async def create_voice_channel(self, guild, name, category=None):
        channel = await guild.create_voice_channel(name, category=category)
        self.voice_channels[channel.id] = {
            'channel': channel,
            'created_at': datetime.now(),
            'last_empty_at': None
        }
        return channel
    
    @tasks.loop(seconds=10)
    async def check_empty_voice_channels(self):
        now = datetime.now()
        for channel_id, info in list(self.voice_channels.items()):
            channel = info['channel']
            if len(channel.members) == 0:
                if info['last_empty_at'] is None:
                    info['last_empty_at'] = now
                elif now - info['last_empty_at'] >= timedelta(seconds=60):
                    await channel.delete()
                    del self.voice_channels[channel_id]
            else:
                info['last_empty_at'] = None
    
    async def on_voice_state_update(self, member, before, after):
        if before.channel and before.channel.id in self.voice_channels:
            if len(before.channel.members) == 0:
                self.voice_channels[before.channel.id]['last_empty_at'] = datetime.now()
        if after.channel and after.channel.id in self.voice_channels:
            self.voice_channels[after.channel.id]['last_empty_at'] = None

    async def setup_hook(self):
        #await self.tree.sync()
        setup_commands(self)
        self.check_empty_voice_channels.start()
        self.check_queue_timeouts.start()
        #self.reset_queue.start()

    async def on_ready(self):
        #await self.wait_until_ready()
        await self.tree.sync()  # Sync commands
        print(f"Bot is ready. Logged in as {self.user}")

    async def check_queue(self):
        # Implement queue checking logic here
        if len(self.lfg_queue) < 2:
            return

        players = list(self.lfg_queue.values())
        for i, info1 in enumerate(players):
            for j, info2 in enumerate(players[i+1:], start=i+1):
                player1 = info1['player']
                player2 = info2['player']
                if i != j and abs(RANKS[player1.rank.lower()] - RANKS[player2.rank.lower()]) <= 1 and set(player1.servers) & set(player2.servers):
                    server_list = list(set(player1.servers) & set(player2.servers))
                    del self.lfg_queue[player1.user_id]
                    del self.lfg_queue[player2.user_id]
                    await self.match_players(player1, player2, server_list)
                    return

    async def match_players(self, player1, player2, server_list):
        
        # Implement player matching logic here
        guild = discord.utils.get(self.guilds)
        category = discord.utils.get(guild.categories, name="LFG Matches")
        channel_name = f"match-{player1.name}-{player2.name}"

        voice_channel = await self.create_voice_channel(guild, channel_name, category=category)
        #self.created_voice_channels.append(voice_channel)
        # for player in [player1, player2]:                     uncomment to re-enable permissions
        #     user = await bot.fetch_user(player.user_id)
        #     await voice_channel.set_permissions(user, connect=True)

        # await voice_channel.set_permissions(guild.default_role, connect=False)
        await voice_channel.set_permissions(guild.default_role, connect=True)

        user_ids = [player1.user_id, player2.user_id]
        view = JoinVoiceChannelView(voice_channel, user_ids)

        #LFG-SPAM channel

        await self.get_channel(1291417090640707655).send(f"{self.get_user(player1.user_id).mention} and {self.get_user(player2.user_id).mention}, click the button below to join the voice channel!\n\n**Tags:**\n{player1.tag or ''}\n{player2.tag or ''}\n\n**Servers: {server_list}**", view=view)
        



    # @tasks.loop(minutes=60)
    # async def reset_queue(self):
    #     self.lfg_queue = []
