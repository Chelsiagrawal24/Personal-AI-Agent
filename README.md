# Personal AI Agent 🤖

A privacy-first, fully local personal assistant built with Python and [Ollama](https://ollama.com). It runs entirely on-device (no API keys, no cloud costs) and helps with daily memory, scheduling, studying, and mental well-being check-ins.

## Features

- 🧠 **Persistent Memory** — Remembers facts about the user (name, goals, preferences) across sessions using a local JSON store.
- ⏰ **Smart Reminders** — Tracks deadlines and exams, and proactively surfaces anything due today or tomorrow when the agent starts.
- 📚 **Study Mode** — Turns any topic or set of notes into an interactive quiz session with instant feedback.
- 💙 **Overthinking Check-in** — A guided, structured conversation flow to help the user process anxious thoughts (what's on your mind → is it in your control → what's one small next step).
- 🔒 **100% Local & Free** — Runs on [Ollama](https://ollama.com) with the `llama3.2` model. No API key, no internet dependency after setup, no usage costs.

## Tech Stack

- **Python 3.13**
- **Ollama** (local LLM inference)
- **JSON** for lightweight persistent storage (no external database needed)

## How It Works

The agent maintains three local data files:
- `memory.json` — long-term facts about the user
- `reminders.json` — dated tasks/deadlines
- `checkins.json` — history of overthinking check-in sessions

On every conversation turn, the agent dynamically builds a system prompt that injects the user's memory and upcoming reminders, so responses stay personalized without needing a heavier vector database.

## Setup

1. Install [Ollama](https://ollama.com) and pull a model:
   ```bash
   ollama pull llama3.2
   ```
2. Install the Python dependency:
   ```bash
   pip3 install ollama
   ```
3. Run the agent:
   ```bash
   python3 agent.py
   ```

## Commands

| Command | Description |
|---|---|
| `/remember <fact>` | Save a single fact to memory |
| `/rememberall <fact1 \| fact2 \| ...>` | Save multiple facts at once |
| `/memory` | View all saved memory |
| `/forget <number>` | Delete a memory item |
| `/remind <YYYY-MM-DD> <task>` | Set a reminder |
| `/reminders` | View upcoming reminders |
| `/delreminder <number>` | Delete a reminder |
| `/studystart <topic>` | Start a quiz session on a topic |
| `/studystop` | End the quiz session |
| `/checkin` | Start a guided overthinking check-in |
| `/checkinstop` | End the check-in and save a summary |
| `/checkins` | View past check-in history |
| `exit` | Quit the agent |

## Roadmap

- [ ] Telegram bot interface for mobile access
- [ ] Semantic memory search (vector embeddings) for larger memory sets
- [ ] Push notifications for reminders

## Why This Project

Built as a hands-on exploration of LLM tool-use patterns, persistent state management, and prompt engineering — using a fully local, cost-free stack so the project can be run and evaluated by anyone without needing an API key.

## Author

Chelsi — B.Tech CSE (AI/ML), building this as a personal learning + portfolio project.
