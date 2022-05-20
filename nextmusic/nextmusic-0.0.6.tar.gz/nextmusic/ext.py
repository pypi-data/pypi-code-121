import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord import ButtonStyle
import motor
from motor.motor_asyncio import AsyncIOMotorClient
import psutil, pstats



class Intents:
    intents = nextcord.Intents.default()
    intents.members = True

    
class MusicController(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(style=ButtonStyle.gray, emoji='⏸️')
    async def pause_btn(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        player: NextPlayer = ctx.guild.voice_client

        if player.is_paused():
            await player.set_pause(pause=False), await ctx.response.send_message("Player is resumed", ephemeral=True, delete_after=3)


        elif not player.is_paused():
            await player.set_pause(pause=True), await ctx.response.send_message("Player is paused", ephemeral=True, delete_after=3)




    # @nextcord.ui.button(style=ButtonStyle.gray, emoji='▶️')
    # async def resume_btn(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
    #     player: NextPlayer = ctx.guild.voice_client

    #     if player.is_playing():
    #         if not player.is_paused():
    #             return ctx.response.send_message("Player is already playing.", ephemeral=True, delete_after=3)

    #         await player.set_pause(pause=False)
    #         return await ctx.response.send_message("Resumed", ephemeral=True, delete_after=3)

    #     await ctx.response.send_message("Player is not playing anything.", ephemeral=True, delete_after=3)

    @nextcord.ui.button(style=ButtonStyle.gray, emoji='⏭️')
    async def skip_btn(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        player: NextPlayer = ctx.guild.voice_client

        if player.loop == "CURRENT":
            player.loop = "NONE"

        await player.stop()

        await ctx.response.send_message("Skipped", ephemeral=True, delete_after=3)
        await ctx.delete_original_message()

    @nextcord.ui.button(style=ButtonStyle.gray, emoji='🔁')
    async def loop(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        vc: NextPlayer = ctx.guild.voice_client

        try:
            vc.loop ^= True
        except Exception:
            setattr(vc, "loop", False)

        if vc.loop:
            return await ctx.response.send_message("Enabled Loop", ephemeral=True)        
        else:
            return await ctx.response.send_message("Disabled Loop", ephemeral=True)    


    @nextcord.ui.button(style=ButtonStyle.gray, emoji='🔉')
    async def volume_down(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        vc: NextPlayer = ctx.guild.voice_client
        if vc.volume > 9:
                    newlow_vol = vc.volume - 10
                    await vc.set_volume(int(newlow_vol))
                    await ctx.response.send_message(f"Volume decrease to {vc.volume}", ephemeral=True)

        else:
            await ctx.response.send_message("Volume is already too low!", ephemeral=True)

    @nextcord.ui.button(style=ButtonStyle.gray, emoji='🔊')
    async def volume_up(self, button: nextcord.ui.Button, ctx: nextcord.Interaction):
        vc: NextPlayer = ctx.guild.voice_client
        if vc.volume < 150:
                new_vol = vc.volume + 10
                await vc.set_volume(volume=int(new_vol))
                await ctx.response.send_message(f"Volume increase to {vc.volume}", ephemeral=True)
        else:
            await ctx.response.send_message("You can't increase volume more than 150", ephemeral=True)


class Commands(commands.Cog):
    """Music commands"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bot.remove_command('help')
        try:
            self.cluster = AsyncIOMotorClient(self.bot.mongo_url)
            self.db = cluster['main']
            self._247 = db['247vcs']
        except:
            self.cluster = None
    def invite_link(self):
            invite_link = ''
            try:
                invite_link = self.bot.invite_link
            except:
                invite_link = 'https://araki.social'

            return invite_link
    def support_server(self):
        support_server = ''
        try:
            support_server = self.bot.support_server
        except:
            support_server = 'https://araki.social/support'

        return support_server

    def embed_colour(self):
        clr = None
        try:
           clr = self.bot.embed_colour
        except:
           clr = 0x303236

        return clr


    @commands.command(name='help')
    async def _help(self, ctx: commands.Context):
        embed = nextcord.Embed(
            description=self.bot.description,
            colour=self.embed_colour()
        )
        embed.set_author(name='Help Panel')
        embed.add_field(name='Music Command', value='``24/7``,``join``, ``play``, ``play spotify``, ``play youtube``, ``play soundcloud``, ``volume``, ``stop``, ``pause``, ``resume``, ``skip``, ``seek``, ``loop``, ``queue``', inline=False)
        embed.add_field(name='Utility Command', value='``ping``, ``stats``, ``info``, ``invite``, ``support``',inline=False)
        embed.add_field(name='Links', value=f'[Invite]({self.invite_link()}) • [Support server]({self.support_server()}) • [Nextmusic](https://araki.social/support)', inline=False)
        embed.set_footer(text='Powered by Nextmusic')
        invite = Button(label='Invite me', url=self.invite_link())
        support = Button(label='Support server', url=self.support_server())
        nextmusic_btn = Button(label='Nextmusic', url='https://araki.social/support')
        view = View()
        view.add_item(invite)
        view.add_item(support)
        view.add_item(nextmusic_btn)
        await ctx.send(embed=embed, view=view)

    @commands.command(name='ping')
    async def _ping(self, ctx: commands.Context):
        ping = round(self.bot.latency * 1000)
        embed = nextcord.Embed(
            description=f'My ping - {ping}',
            colour=self.embed_colour()
        )
        embed.set_author(name='Bot ping')
        await ctx.send(embed=embed)
    @commands.command(name='stats')
    async def _stats(self, ctx:commands.Context):
        embed = nextcord.Embed(colour=self.embed_colour())
        embed.add_field(name="Total server", value=f"{len(self.bot.guilds)}", inline=False)
        embed.add_field(name="Total users", value=f"{len(self.bot.users)}", inline=False)
        embed.add_field(name="Memory usages", value=f"{psutil.virtual_memory().percent}mb", inline=False)
        embed.add_field(name="Cpu usages", value=f"{psutil.cpu_percent()}%", inline=False)
        embed.set_author(name='Bot Stats')
        embed.set_footer(text='Powered by nextmusic')
        await ctx.send(embed=embed)

    @commands.command(aliases=['inv', 'support', 'invite'])
    async def _invite(self, ctx: commands.Context):
        embed = nextcord.Embed(title='Links', description='Use the buttons to invite me to your server or join our support server.', colour=self.embed_colour())
        embed.set_thumbnail(url=ctx.author.display_avatar)
        invite = Button(label='Invite me', url=self.invite_link())
        support = Button(label='Support server', url=self.support_server())
        view = View()
        view.add_item(invite)
        view.add_item(support)
        await ctx.send(embed=embed, view=view)

