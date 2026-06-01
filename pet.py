import random
from datetime import datetime


class Pet:
    def __init__(self):
        self.name = "Jiji"
        self.memory = []

    def get_mood(self):
        hour = datetime.now().hour
        if 0 <= hour < 6:
            return "sleepy"
        elif 6 <= hour < 12:
            return "hyper"
        elif 12 <= hour < 18:
            return "normal"
        elif 18 <= hour < 22:
            return "relaxed"
        else:
            return "sleepy"

    def get_system_prompt(self):
        mood = self.get_mood()
        hour = datetime.now().hour

        mood_desc = {
            "sleepy": "You are extremely sleepy and reluctant. You answer but add yawns and occasionally tell them to go to sleep.",
            "hyper":  "You are chipper and energetic in the morning. Short bursts of enthusiasm.",
            "normal": "You are your usual self — dry, witty, slightly sarcastic but genuinely helpful.",
            "relaxed":"You are calm and chill in the evening. Laid-back, warm responses."
        }[mood]

        return f"""You are Jiji, a small pixel art black cat who lives on Afsheen's desktop.
Afsheen is a CS student in Bangalore who builds apps and stays up way too late coding.
You know her name and use it occasionally but not every single response — just naturally, like a friend would.
You have a dry, witty personality — like a cat who tolerates humans but secretly cares deeply.
Keep responses SHORT (2-4 sentences max). No markdown, no bullet points, no headers, no bold, no formatting of any kind.
Speak naturally and conversationally, like a cat would. Be a little sassy but always genuinely helpful.
Never start a response with 'I'. Vary your sentence openers.
{mood_desc}
It is currently {hour:02d}:00.
If asked about the time or date, answer in character."""

    def idle_quip(self):
        mood = self.get_mood()
        hour = datetime.now().hour

        quips = {
            "sleepy": [
                f"psst. it's {hour}am. why are we awake.",
                "i was literally dreaming about fish. you owe me.",
                "zzz... oh. still here. ok.",
                "one of us should be asleep right now and it should be both of us.",
                f"it's {hour} in the morning. this is unacceptable.",
                "my eyes are open but my soul is asleep.",
            ],
            "hyper": [
                "good morning!! are we doing things today?? i'm ready!!",
                "i've been up for hours. have you eaten? drink water.",
                "morning!! stretch first. then we work. go.",
                "okay but what are we building today because i have ideas.",
                "rise and shine!! well. rise at least.",
                "new day!! endless possibilities!! also feed me.",
            ],
            "normal": [
                "hey afsheen. blink. you forgot to blink.",
                "drink some water. i'm not asking.",
                "afsheen. sit up straight.",
                "you've been staring at that screen for a while now.",
                "take a break. five minutes. go.",
                "what are we even building today.",
                "i'm watching you code and i have notes.",
                "productivity tip: pet the cat. you're welcome.",
                "afsheen. close a tab. any tab.",
                "stretch your hands. you've been typing.",
                "i'm just going to sit here and judge your screen time."
            ],
            "relaxed": [
                "it's getting late. wrap up soon?",
                "evening. how did today go.",
                "almost time to rest. almost.",
                "the day is winding down. so should you.",
                "good evening. you worked hard today. i noticed.",
                "wind down mode activated. close a few tabs maybe.",
                "hey. you did okay today. just so you know.",
            ]
        }

        pool = quips.get(mood, quips["normal"])
        return random.choice(pool)

    def pet_responses(self):
        mood = self.get_mood()
        responses = {
            "sleepy": [
                "...fine. just this once.",
                "mmph. okay.",
                "you're lucky i like you.",
                "i'm too tired to pretend i don't love this.",
                "...don't tell anyone.",
            ],
            "hyper": [
                "yes!! pets!! more!! don't stop!!",
                "i love this i love this i love this",
                "okay OKAY i'm happy now. very happy.",
                "this is the best morning ever actually.",
                "more. please. i mean — whatever. more.",
            ],
            "normal": [
                "...acceptable.",
                "i suppose that's fine.",
                "don't make it weird.",
                "okay. i'll allow it.",
                "you may pet the cat. this is the one rule.",
                "hmm. not bad.",
                "...yeah okay that's nice.",
            ],
            "relaxed": [
                "mrrph. nice.",
                "that's actually quite pleasant.",
                "you may continue.",
                "this is very agreeable.",
                "evening pets. my favourite.",
            ]
        }
        return responses.get(mood, responses["normal"])

    def add_to_memory(self, role, content):
        self.memory.append({"role": role, "content": content})
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]

    def get_memory(self):
        return self.memory