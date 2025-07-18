import requests
import time
import logging
from bs4 import BeautifulSoup
from utils import invoke, clean_card_data

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ANKI_URL = "http://localhost:8765"

class AnkiController:
    def start_review(self, deck_name="Core 2000"):
        logger.debug(f"Starting review for deck: {deck_name}")
        start_time = time.time()
        result = invoke("guiDeckReview", {"name": deck_name})
        if result.get("error"):
            logger.error(f"guiDeckReview failed: {result.get('error')}")
            return False
        logger.debug(f"guiDeckReview response: {result}")
        result = invoke("guiReviewActive")
        logger.debug(f"guiReviewActive response: {result}")
        if result.get("error") or not result.get("result", False):
            logger.error(f"Review not active: error={result.get('error')}, result={result.get('result')}")
            return False
        logger.info(f"start_review took {time.time() - start_time:.2f} seconds")
        return True

    def get_current_card(self):
        logger.debug("Fetching current card")
        start_time = time.time()
        result = invoke("guiCurrentCard")
        if result.get("error"):
            logger.error(f"guiCurrentCard failed: {result.get('error')}")
            return None
        card = result.get("result", {})
        logger.debug(f"guiCurrentCard response: cardId={card.get('cardId')}")
        logger.info(f"get_current_card took {time.time() - start_time:.2f} seconds")
        return card

    def show_question(self, card_id=None, card_cache=None):
        logger.debug(f"Showing question: card_id={card_id}, card_cache={'set' if card_cache else 'unset'}")
        start_time = time.time()
        if card_id:  # Non-GUI mode
            result = invoke("cardsInfo", {"cards": [card_id]})
            if result.get("error"):
                logger.error(f"cardsInfo failed for card_id={card_id}: {result.get('error')}")
                return None
            fields = result["result"][0]["fields"]
            logger.debug(f"cardsInfo fields: {fields}")
            question_data = {
                "main_term": fields.get("Vocabulary-Kanji", {}).get("value", ""),
                "furigana": fields.get("Vocabulary-Furigana", {}).get("value", ""),
                "kana": fields.get("Vocabulary-Kana", {}).get("value", ""),
                "example_sentence": fields.get("Expression", {}).get("value", ""),
                "part_of_speech": fields.get("Vocabulary-Pos", {}).get("value", ""),
                "images": []
            }
            soup = BeautifulSoup(question_data["example_sentence"], "html.parser")
            question_data["images"] = [img["src"] for img in soup.find_all("img") if "src" in img.attrs]
            question_data["example_sentence"] = clean_card_data(question_data["example_sentence"])["example_sentence"]
            logger.info(f"show_question (non-GUI) took {time.time() - start_time:.2f} seconds")
            return question_data
        # GUI mode
        invoke_start = time.time()
        invoke("guiShowQuestion")  # Ensure GUI advances to next question
        logger.info(f"guiShowQuestion took {time.time() - invoke_start:.2f} seconds")
        card = self.get_current_card()
        if not card:
            logger.error("No card returned from get_current_card")
            return None
        card_id = card["cardId"]
        logger.debug(f"Current card ID: {card_id}")
        fields = card_cache.get(card_id) if card_cache else None
        if not fields:
            cards_info_start = time.time()
            result = invoke("cardsInfo", {"cards": [card_id]})
            logger.info(f"cardsInfo took {time.time() - cards_info_start:.2f} seconds")
            if result.get("error"):
                logger.error(f"cardsInfo failed for card_id={card_id}: {result.get('error')}")
                return None
            fields = result["result"][0]["fields"]
            if card_cache is not None:
                card_cache[card_id] = fields
            logger.debug(f"cardsInfo fields: {fields}")
        question_data = clean_card_data(card.get("question", ""))
        question_data.update({
            "furigana": fields.get("Vocabulary-Furigana", {}).get("value", ""),
            "kana": fields.get("Vocabulary-Kana", {}).get("value", "")
        })
        logger.info(f"show_question (GUI) took {time.time() - start_time:.2f} seconds")
        return question_data

    def show_answer(self, card_id=None, card_cache=None):
        logger.debug(f"Showing answer: card_id={card_id}, card_cache={'set' if card_cache else 'unset'}")
        start_time = time.time()
        if card_id:  # Non-GUI mode
            result = invoke("cardsInfo", {"cards": [card_id]})
            if result.get("error"):
                logger.error(f"cardsInfo failed for card_id={card_id}: {result.get('error')}")
                return None
            fields = result["result"][0]["fields"]
            logger.debug(f"cardsInfo fields: {fields}")
            answer_data = {
                "main_term": fields.get("Vocabulary-English", {}).get("value", ""),
                "example_sentence": fields.get("Sentence-English", {}).get("value", ""),
                "part_of_speech": fields.get("Vocabulary-Pos", {}).get("value", ""),
                "images": []
            }
            logger.info(f"show_answer (non-GUI) took {time.time() - start_time:.2f} seconds")
            return answer_data
        # GUI mode
        invoke_start = time.time()
        result = invoke("guiShowAnswer")
        logger.info(f"guiShowAnswer took {time.time() - invoke_start:.2f} seconds")
        if result.get("error"):
            logger.error(f"guiShowAnswer failed: {result.get('error')}")
            return None
        card = self.get_current_card()
        if not card:
            logger.error("No card returned from get_current_card")
            return None
        card_id = card["cardId"]
        logger.debug(f"Current card ID: {card_id}")
        fields = card_cache.get(card_id) if card_cache else None
        if not fields:
            cards_info_start = time.time()
            result = invoke("cardsInfo", {"cards": [card_id]})
            logger.info(f"cardsInfo took {time.time() - cards_info_start:.2f} seconds")
            if result.get("error"):
                logger.error(f"cardsInfo failed for card_id={card_id}: {result.get('error')}")
                return None
            fields = result["result"][0]["fields"]
            if card_cache is not None:
                card_cache[card_id] = fields
            logger.debug(f"cardsInfo fields: {fields}")
        answer_data = clean_card_data(card.get("answer", ""))
        answer_data.update({
            "main_term": fields.get("Vocabulary-English", {}).get("value", ""),
            "example_sentence": fields.get("Sentence-English", {}).get("value", "")
        })
        logger.info(f"show_answer (GUI) took {time.time() - start_time:.2f} seconds")
        return answer_data

    def answer_card(self, ease=3):
        logger.debug(f"Answering current GUI card with ease={ease}")
        show_result = invoke("guiShowAnswer")
        if show_result.get("error"):
            logger.error(f"guiShowAnswer failed: {show_result['error']}")
            return False
        time.sleep(0.5)
        result = invoke("guiAnswerCard", {"ease": ease})
        if result.get("error"):
            logger.error(f"guiAnswerCard failed: {result['error']}")
            return False
        elif result["result"] is False:
            logger.warning("guiAnswerCard returned False. Possibly no card was active or not showing answer.")
            return False
        logger.info("✓ Card answered successfully!")
        return True

    def card_count(self, deck_name="Core 2000"):
        logger.debug(f"Counting due cards for deck: {deck_name}")
        start_time = time.time()
        result = invoke("findCards", {"query": f"deck:\"{deck_name}*\" is:due"})
        if result.get("error"):
            logger.error(f"findCards failed: {result.get('error')}")
            return 0
        logger.debug(f"findCards response: {result}")
        logger.info(f"card_count took {time.time() - start_time:.2f} seconds")
        return len(result.get("result", []))
