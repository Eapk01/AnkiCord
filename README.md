# AnkiCord 

**AnkiCord** is a Discord bot that lets you review your Anki flashcards *directly through Discord*. Powered by [AnkiConnect](https://foosoft.net/projects/anki-connect/), it integrates with the Anki GUI for an interactive review experience.

---

## ✨ Features

* 📩 Sends flashcards in DMs when you run `!review`
* 🔄 Flip the card and view the answer
* ✅ Choose your ease: Again / Hard / Good / Easy
* 🔗 Fully synced with your Anki deck through AnkiConnect
* 🔊 Optional sound playback

---

## ⚖️ Requirements

* **Anki Desktop** (must be open)
* **AnkiConnect** plugin
* **Python 3.10+**

---

## 📚 How to Install

### 1. Install AnkiConnect

* Open Anki
* Go to `Tools` > `Add-ons`
* Click `Get Add-ons...`
* Enter this code:

  ```
  2055492159
  ```


- Click "OK" and restart Anki

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/AnkiCord.git
cd AnkiCord
````

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure

Edit `config.py` with your settings:

```python
# config.py
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
DECK_NAME = "Your Deck Name Here"
```

**TIP:** To disable automatic sound playback (recommended for speed):

* Open Anki
* Go to `Tools` > `Deck Options`
* Under the `Audio` tab, check: `Don't play audio automatically`

### 5. Run the Bot

```bash
python bot.py
```

Then DM your bot on Discord with `!review` and start studying.

---

## 🌀 Future Plans

* 👥 Multi-user support via per-user deck snapshots
* 🏢 Host-ready Docker version
* 📊 Progress stats and review history
* 🛃 Upload custom decks via Discord

---

## 🚀 Contributing

PRs and ideas welcome! If you have suggestions, feel free to fork and share.

---

📚 Built by Marwan Alghamdi
