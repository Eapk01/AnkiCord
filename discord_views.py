import discord
from discord.ui import View, Button

class ReviewView(View):
    def __init__(self, anki, card, card_number, total_cards, user):
        super().__init__(timeout=300.0)
        self.anki = anki
        self.card = card
        self.card_number = card_number
        self.total_cards = total_cards
        self.user = user  # Store the command invoker

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("❌ You cannot interact with this review.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="🔄 Flip Card", style=discord.ButtonStyle.primary, custom_id="flip", row=0)
    async def flip_card(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        answer_data = self.anki.show_answer(self.card["cardId"])
        if not answer_data:
            await interaction.followup.send("❌ Failed to load answer.", ephemeral=True)
            return

        # Create answer embed
        embed = discord.Embed(
            title=f"Card #{self.card_number} of {self.total_cards} – Answer",
            color=discord.Color.green()
        )
        embed.add_field(name="Answer", value=answer_data.get("main_term", "N/A"), inline=False)
        embed.add_field(name="Translation", value=answer_data.get("example_sentence", "None"), inline=False)

        self.clear_items()
        self.add_item(EaseButton("1️⃣ Again", 1, discord.ButtonStyle.red, custom_id=f"again_{self.card_number}"))
        self.add_item(EaseButton("2️⃣ Hard", 2, discord.ButtonStyle.grey, custom_id=f"hard_{self.card_number}"))
        self.add_item(EaseButton("3️⃣ Good", 3, discord.ButtonStyle.green, custom_id=f"good_{self.card_number}"))
        self.add_item(EaseButton("4️⃣ Easy", 4, discord.ButtonStyle.blurple, custom_id=f"easy_{self.card_number}"))
        await interaction.followup.send(embed=embed, view=self)


class EaseButton(Button):
    def __init__(self, label, ease, style, custom_id):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.ease = ease

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.view.anki.answer_card(self.ease)
        await interaction.followup.send(
            f"✅ Marked as {self.label.split(' ')[1]}!",
            ephemeral=True
        )
        self.view.stop()
