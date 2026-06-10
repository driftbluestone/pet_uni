import discord, random, time
from discord import app_commands
from discord.ext import commands
from api import config, users
CONFIG = config.get()
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent

emojis = ["🐈‍⬛","🐱","😾","😿","🙀","😽","😼","😻","😹","😸","😺","🐈"]
too_fast = [
    "Woah there, hot stuff! You can't pet Uni twice in a row, wait for someone else to pet her first!",
    "Slow down buddy. Wait for someone else to pet Uni first.",
    "Fastest fingers in all the server, huh? Take it down a notch.",
]
friendliness_fail = [
    "Your touch was insufficiently gentle. Uni ran away. :(",
    "Uni doesn't want to be pet by you right now."
]

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PetUni(bot=bot))

class PetUni(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        if CONFIG["last_interaction"] == 0:
            return
        channel = await self.bot.fetch_channel(CONFIG["last_interaction_channel"])
        message = await channel.fetch_message(CONFIG["last_interaction"])
        await message.edit(view=Petter())

    uni = app_commands.Group(name="uni", description=".")

    @uni.command(name="pet", description="pspspspsps heeeeere kitty")
    async def pet(self, interaction: discord.Interaction):
        if CONFIG["last_interaction"] != 0:
            channel = await self.bot.fetch_channel(CONFIG["last_interaction_channel"])
            message = await channel.fetch_message(CONFIG["last_interaction"])
            await message.delete()
        
        view = Petter()
        message = await interaction.response.send_message(view = view, embed = view.embed)
        CONFIG["last_interaction_channel"] = interaction.channel.id
        CONFIG["last_interaction"] = message.message_id
        config.overwrite(CONFIG)
    
    @uni.command(name="image", description="Upload a new image for uni to have a chance to display on pet")
    async def image(self, interaction: discord.Interaction, image_link: str):
        if not await users.has_permission(interaction.user.id, "pet_uni:add_uni_images"):
            return await interaction.response.send_message(":warning: No permission.", ephemeral=True)
        CONFIG["images"].append(image_link)
        config.overwrite(CONFIG)
        await interaction.response.send_message(f"New image added!")
        
class Petter(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.embed = discord.Embed(title="Pet Uni!")
        self.embed.set_image(url=random.choice(CONFIG["images"]))
        self.message = ""
        self.stats = ""
        self.update_stats()
        self.embed.description = self.stats
        self.button = discord.ui.Button(label="Pet Uni!", style=discord.ButtonStyle.primary, emoji=random.choice(emojis), custom_id="pat")
        self.button.callback = self.pet
        self.add_item(self.button)
    
    async def pet(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False, ephemeral=True)
        
        # if user double clicks
        if CONFIG["last_interaction_user"] == interaction.user.id:
            self.set_embed_description(random.choice(too_fast))
            return await interaction.message.edit(embed=self.embed)
        
        user = users.get(interaction.user.id)

        # friendliness update
        if user["pet_uni:last_friendliness_update"] < int(time.time() // 3600):
            user["pet_uni:friendliness"] = random.randint(1,100)
            user["pet_uni:last_friendliness_update"] = int(time.time() // 3600)

        CONFIG["last_interaction_user"] = interaction.user.id
        if user["pet_uni:friendliness"] < random.randint(1, 100):
            self.set_embed_description(random.choice(friendliness_fail))
            await interaction.message.edit(view=self, embed=self.embed)
        else:
            # update stats
            CONFIG["last_pet"] = int(time.time())
            CONFIG["times_pet"] += 1
            user["pet_uni:times_pet"] += 1

            # update message
            self.button.emoji = random.choice(emojis)
            self.embed.set_image(url=random.choice(CONFIG["images"]))
            self.update_stats()
            self.set_embed_description("Uni has been pet!")
            await interaction.message.edit(view=self, embed=self.embed)
        
        config.overwrite(CONFIG)
        users.overwrite(user)

    def set_embed_description(self, message: str, stats: str | None = None) -> None:
        if stats is None:
            self.embed.description = f"{message}\n{self.stats}"
        else:
            self.embed.description = f"{message}\n{stats}"

    def update_stats(self) -> None:
        self.stats = f"Times pet: {CONFIG["times_pet"]}\nLast pet: <t:{CONFIG["last_pet"]}:R> by <@{CONFIG["last_interaction_user"]}>"
        