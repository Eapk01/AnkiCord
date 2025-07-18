import requests
from bs4 import BeautifulSoup

ANKI_URL = "http://localhost:8765"
session = requests.Session()

def invoke(action, params=None):
    response = session.post(ANKI_URL, json={
        "action": action,
        "version": 6,
        "params": params or {}
    })
    return response.json()

def clean_card_data(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup(["style", "script"]):
        tag.decompose()

    main_term = None
    for div in soup.find_all("div", class_="japanese"):
        if "font-size:60px" in div.get("style", ""):
            main_term = div.get_text(strip=True)
            break

    example_sentence = None
    example_div = soup.find("div", id="example-sentence")
    if example_div:
        for b in example_div.find_all("b"):
            b.unwrap()
        example_sentence = example_div.get_text(strip=True)

    part_of_speech = None
    for div in soup.find_all("div", style=lambda value: value and "font-size:16px" in value):
        part_of_speech = div.get_text(strip=True)
        break

    return {
        "main_term": main_term or "",
        "example_sentence": example_sentence or "",
        "part_of_speech": part_of_speech or ""
    }