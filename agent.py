"""
Personal AI Agent - Step 5: Overthinking Check-in Add Ki Gayi
--------------------------------------------------------------------
Memory commands (Step 2):
  /remember <fact>                        -> ek fact save karega
  /rememberall <fact1 | fact2 | fact3>    -> multiple facts ek saath save karega
  /memory                                 -> saari saved memory dikhayega
  /forget <number>                        -> memory se ek cheez hatayega

Reminder commands (Step 3):
  /remind <YYYY-MM-DD> <kaam>             -> ek reminder save karega
  /reminders                              -> saare upcoming reminders dikhayega
  /delreminder <number>                   -> ek reminder hatayega

Study Mode commands (Step 4):
  /studystart <topic ya notes>            -> quiz session shuru karega
  /studystop                              -> study mode band karega

Overthinking Check-in commands (Step 5 - NAYA):
  /checkin                                -> guided check-in shuru karega jab overthink kar rahe ho
  /checkinstop                            -> check-in mode band karega
  /checkins                               -> purane check-ins ki list dikhayega

exit                                       -> band karega
"""

import ollama
import json
import os
from datetime import datetime, date

MEMORY_FILE = "memory.json"
REMINDERS_FILE = "reminders.json"
CHECKINS_FILE = "checkins.json"
MODEL_NAME = "llama3.2"   # apna model naam yahan match karo


# ---------- MEMORY FUNCTIONS ----------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_memory(memory_list):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_list, f, indent=2)


def add_memory(fact_text):
    memory = load_memory()
    memory.append({
        "fact": fact_text,
        "saved_on": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_memory(memory)


def remove_memory(index):
    memory = load_memory()
    if 1 <= index <= len(memory):
        removed = memory.pop(index - 1)
        save_memory(memory)
        return removed["fact"]
    return None


def memory_as_text():
    memory = load_memory()
    if not memory:
        return "Abhi tak koi memory saved nahi hai."
    lines = [f"- {item['fact']} (saved: {item['saved_on']})" for item in memory]
    return "\n".join(lines)


# ---------- REMINDER FUNCTIONS ----------

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as f:
            return json.load(f)
    return []


def save_reminders(reminder_list):
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminder_list, f, indent=2)


def add_reminder(date_str, task_text):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False

    reminders = load_reminders()
    reminders.append({"date": date_str, "task": task_text})
    reminders.sort(key=lambda r: r["date"])
    save_reminders(reminders)
    return True


def remove_reminder(index):
    reminders = load_reminders()
    if 1 <= index <= len(reminders):
        removed = reminders.pop(index - 1)
        save_reminders(reminders)
        return removed
    return None


def get_upcoming_reminders():
    today = date.today()
    reminders = load_reminders()
    upcoming = []
    for r in reminders:
        r_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
        if r_date >= today:
            days_left = (r_date - today).days
            upcoming.append((r, days_left))
    return upcoming


def reminders_as_text():
    upcoming = get_upcoming_reminders()
    if not upcoming:
        return "Koi upcoming reminder nahi hai."
    lines = []
    for r, days_left in upcoming:
        if days_left == 0:
            when = "AAJ"
        elif days_left == 1:
            when = "KAL"
        else:
            when = f"{days_left} din baad"
        lines.append(f"- {r['date']} ({when}): {r['task']}")
    return "\n".join(lines)


def urgent_reminders_alert():
    upcoming = get_upcoming_reminders()
    urgent = [r for r, days_left in upcoming if days_left <= 1]
    if not urgent:
        return None
    lines = []
    for r in urgent:
        r_date = datetime.strptime(r["date"], "%Y-%m-%d").date()
        days_left = (r_date - date.today()).days
        when = "AAJ" if days_left == 0 else "KAL"
        lines.append(f"⏰ {when}: {r['task']}")
    return "\n".join(lines)


# ---------- CHECK-IN (OVERTHINKING) FUNCTIONS ----------

def load_checkins():
    if os.path.exists(CHECKINS_FILE):
        with open(CHECKINS_FILE, "r") as f:
            return json.load(f)
    return []


def save_checkin(note_text):
    checkins = load_checkins()
    checkins.append({
        "note": note_text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    with open(CHECKINS_FILE, "w") as f:
        json.dump(checkins, f, indent=2)


def checkins_as_text():
    checkins = load_checkins()
    if not checkins:
        return "Abhi tak koi check-in nahi hua hai."
    lines = [f"- {c['date']}: {c['note']}" for c in checkins[-10:]]
    return "\n".join(lines)


# ---------- AGENT SETUP ----------

def build_system_prompt():
    study_instructions = ""
    if study_mode_active:
        study_instructions = f"""

STUDY MODE ACTIVE - topic/notes: "{study_topic}"
Tum abhi user ko is topic par quiz kar rahe ho. Rules:
- Ek time pe sirf EK question pucho (multiple choice ya short answer)
- User ke jawaab ka evaluation karo - sahi hai to confirm karo aur thodi si extra detail do
- Galat hai to politely batao sahi jawaab kya tha aur chhota sa explanation do
- Har jawaab ke baad seedha agla question pucho, bina zyada lambi baat kiye
- Encouraging tone rakho, mazaak mat udao galti par"""

    checkin_instructions = ""
    if checkin_mode_active:
        checkin_instructions = """

OVERTHINKING CHECK-IN MODE ACTIVE
Tum abhi user ko ek chhota, calm guided check-in de rahe ho. Rules:
- Ek time pe sirf EK sawaal pucho, chhota aur simple
- Sabse pehle pucho: "kya soch rahe ho abhi?"
- Fir pucho: "ye cheez tumhare control me hai ya nahi?"
- Fir pucho: "iske liye ek chhota sa agla step kya ho sakta hai?"
- Tone hamesha calm, warm, bina judge kiye rakho
- Lambi advice mat do, sirf gently guide karo
- Agar user genuinely bahut distressed lage, to gently suggest karo ki kisi
  trusted insaan ya professional se baat karein"""

    return f"""Tum ek personal AI assistant ho jo user ko:
- unka schedule aur reminders yaad rakhne me
- padhai (study) me
- overthinking kam karne me
madad karte ho. Tum dost jaisa tone rakhte ho - friendly, supportive, seedha baat karte ho.

Yahan user ke baare me tumhe pehle se pata hai (memory):
{memory_as_text()}

Yahan user ke upcoming reminders/deadlines hain:
{reminders_as_text()}

Is memory aur reminders ko use karo taaki tum user ko personally jaanne wale dost jaise lago,
aur agar koi reminder aaj ya bahut jald hai to usko proactively mention karo.{study_instructions}{checkin_instructions}"""


conversation_history = []

# Study mode state
study_mode_active = False
study_topic = ""

# Check-in mode state
checkin_mode_active = False


def chat_with_agent(user_message):
    conversation_history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": build_system_prompt()}] + conversation_history
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    agent_reply = response["message"]["content"]
    conversation_history.append({"role": "assistant", "content": agent_reply})
    return agent_reply


# ---------- MAIN LOOP ----------

def main():
    global study_mode_active, study_topic, checkin_mode_active

    print("🤖 Aapka Personal AI Agent (Memory + Reminders + Study + Check-in) taiyar hai!")
    print("Memory: /remember, /rememberall, /memory, /forget <n>")
    print("Reminders: /remind <YYYY-MM-DD> <kaam>, /reminders, /delreminder <n>")
    print("Study: /studystart <topic>, /studystop")
    print("Check-in: /checkin, /checkinstop, /checkins")
    print("exit -> band karne ke liye\n")

    alert = urgent_reminders_alert()
    if alert:
        print("🔔 IMPORTANT REMINDERS:")
        print(alert)
        print()

    while True:
        user_input = input("Aap: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Agent: Theek hai, phir milte hain! 👋")
            break

        elif user_input.lower().startswith("/rememberall "):
            raw = user_input[len("/rememberall "):].strip()
            facts = [f.strip() for f in raw.split("|") if f.strip()]
            for fact in facts:
                add_memory(fact)
            print(f"Agent: ✅ {len(facts)} cheezein yaad rakh li:")
            for fact in facts:
                print(f"   - {fact}")
            print()

        elif user_input.lower().startswith("/remember "):
            fact = user_input[len("/remember "):].strip()
            add_memory(fact)
            print(f"Agent: ✅ Yaad rakh liya - \"{fact}\"\n")

        elif user_input.lower() == "/memory":
            print("\n📝 Ab tak ki saved memory:")
            print(memory_as_text())
            print()

        elif user_input.lower().startswith("/forget "):
            try:
                num = int(user_input[len("/forget "):].strip())
                removed = remove_memory(num)
                if removed:
                    print(f"Agent: 🗑️  Ye hata diya - \"{removed}\"\n")
                else:
                    print("Agent: Ye number memory me nahi mila. /memory likh ke list dekho.\n")
            except ValueError:
                print("Agent: Sahi format: /forget 2  (number /memory se lo)\n")

        elif user_input.lower().startswith("/studystart "):
            topic = user_input[len("/studystart "):].strip()
            study_mode_active = True
            study_topic = topic
            print(f"Agent: 📚 Study mode ON! Topic: \"{topic}\"")
            print("(Ab jo bhi likhoge, agent tumhe is par quiz karega. Band karne ke liye /studystop likho)\n")
            print("(sochna chal raha hai...)\n")
            reply = chat_with_agent(f"Mujhe '{topic}' par quiz karo, pehla question pucho.")
            print(f"Agent: {reply}\n")

        elif user_input.lower() == "/studystop":
            study_mode_active = False
            study_topic = ""
            print("Agent: 📚 Study mode band kar diya. Normal chat pe wapas!\n")

        elif user_input.lower() == "/checkin":
            checkin_mode_active = True
            print("Agent: 💙 Check-in shuru karte hain, thoda ruk ke sochte hain.\n")
            print("(sochna chal raha hai...)\n")
            reply = chat_with_agent("Main abhi overthink kar rahi/raha hoon, mera check-in shuru karo.")
            print(f"Agent: {reply}\n")

        elif user_input.lower() == "/checkinstop":
            if checkin_mode_active:
                last_user_msgs = [m["content"] for m in conversation_history if m["role"] == "user"]
                summary = last_user_msgs[-1] if last_user_msgs else "Check-in hua"
                save_checkin(summary)
            checkin_mode_active = False
            print("Agent: 💙 Check-in complete. Yaad rakh liya hai. Apna khayal rakhna!\n")

        elif user_input.lower() == "/checkins":
            print("\n💙 Pichle check-ins:")
            print(checkins_as_text())
            print()

        elif user_input.lower().startswith("/remind "):
            rest = user_input[len("/remind "):].strip()
            parts = rest.split(" ", 1)
            if len(parts) < 2:
                print("Agent: Sahi format: /remind 2026-07-20 AI exam hai\n")
            else:
                date_str, task = parts[0], parts[1]
                success = add_reminder(date_str, task)
                if success:
                    print(f"Agent: ⏰ Reminder set kar diya - {date_str}: \"{task}\"\n")
                else:
                    print("Agent: Date format sahi nahi hai. Use karo: YYYY-MM-DD (jaise 2026-07-20)\n")

        elif user_input.lower() == "/reminders":
            print("\n📅 Upcoming reminders:")
            print(reminders_as_text())
            print()

        elif user_input.lower().startswith("/delreminder "):
            try:
                num = int(user_input[len("/delreminder "):].strip())
                removed = remove_reminder(num)
                if removed:
                    print(f"Agent: 🗑️  Ye reminder hata diya - \"{removed['task']}\"\n")
                else:
                    print("Agent: Ye number reminders me nahi mila. /reminders likh ke list dekho.\n")
            except ValueError:
                print("Agent: Sahi format: /delreminder 2\n")

        else:
            print("\n(sochna chal raha hai...)\n")
            reply = chat_with_agent(user_input)
            print(f"Agent: {reply}\n")


if __name__ == "__main__":
    main()