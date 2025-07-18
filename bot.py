import discord
from discord.ext import commands
import time
import logging
import asyncio
from anki_controller import AnkiController
from discord_views import ReviewView
from utils import invoke
from config import DISCORD_TOKEN, DECK_NAME

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")


@bot.command(name="ping")
async def ping(ctx):
    logger.debug("Ping command received")
    start_time = time.time()
    await ctx.send("Pong! Bot is online.")
    logger.info(f"Ping command completed in {time.time() - start_time:.2f} seconds")


@bot.command(name="review")
async def review_deck(ctx, deck_name=DECK_NAME):
    logger.debug(f"Review command received for deck: {deck_name}")
    start_time = time.time()

    destination = ctx.author  # Use DMs
    # destination = ctx.channel  # Use channel

    anki = AnkiController()

    # Batch fetch all due card IDs and fields
    count_start = time.time()
    card_ids = invoke("findCards", {"query": f"deck:\"{deck_name}*\" is:due"})["result"]
    total = len(card_ids)
    logger.info(f"card_count took {time.time() - count_start:.2f} seconds")
    if total == 0:
        logger.debug("No cards due")
        await destination.send("🎉 No cards due today!")
        logger.info(f"Review command completed (no cards) in {time.time() - start_time:.2f} seconds")
        return

    # Cache all card fields upfront
    cache_start = time.time()
    card_cache = {}
    if card_ids:
        result = invoke("cardsInfo", {"cards": card_ids})
        if not result.get("error"):
            for card in result["result"]:
                card_cache[card["cardId"]] = card["fields"]
    logger.info(f"card_cache population took {time.time() - cache_start:.2f} seconds")

    await destination.send(f"📚 {total} cards ready for review.")

    # Start review
    review_start = time.time()
    use_gui = anki.start_review(deck_name)
    logger.info(f"start_review took {time.time() - review_start:.2f} seconds")

    for i in range(total):
        logger.debug(f"Processing card {i + 1}/{total}")
        card_start = time.time()

        if use_gui:
            question_start = time.time()
            question_data = anki.show_question(card_cache=card_cache)
            logger.info(f"show_question took {time.time() - question_start:.2f} seconds")
            card = anki.get_current_card()
        else:
            if not card_ids:
                logger.error("No card IDs available")
                await destination.send("❌ No card IDs available. Stopping review.")
                break
            card_id = card_ids[i]
            question_start = time.time()
            question_data = anki.show_question(card_id, card_cache)
            logger.info(f"show_question took {time.time() - question_start:.2f} seconds")
            card = {"cardId": card_id}

        if not question_data or not card or "cardId" not in card:
            logger.error(f"Failed to load card {i + 1}: question_data={question_data}, card={card}")
            await destination.send("⚠️ Failed to load card. Skipping to next.")
            continue

        embed = discord.Embed(
            title=f"Card #{i + 1} of {total} - Question",
            description=f"**Term:** {question_data['main_term']} ({question_data.get('furigana', 'No furigana')})\n"
                        f"**Kana:** {question_data.get('kana', 'No kana')}\n\n"
                        f"**Example:** {question_data['example_sentence'] or 'No example'}\n\n"
                        f"**Type:** {question_data['part_of_speech'] or 'Unknown'}",
            color=discord.Color.blue()
        )
        view = ReviewView(anki, card, i + 1, total, ctx.author)
        await destination.send(embed=embed, view=view)
        logger.debug(f"Sent card {i + 1} embed")

        try:
            await asyncio.wait_for(view.wait(), timeout=300.0)
        except asyncio.TimeoutError:
            logger.warning(f"Card {i + 1} timed out after 300 seconds")
            await destination.send("🛑 Review timed out due to inactivity. Ending session.")
            return

        logger.info(f"Card {i + 1} took {time.time() - card_start:.2f} seconds")

    await destination.send("🎯 Review complete!")
    logger.info(f"Review command completed in {time.time() - start_time:.2f} seconds")

bot.run(DISCORD_TOKEN)