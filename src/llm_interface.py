"""
LLM Interface for DreamTalk Emotion Engine.

PromptCompiler builds mood-aware, knowledge-augmented prompts with few-shot
examples.  LocalLLMInterface sends them to the local Ollama model.
"""

import logging
import ollama

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# ---------------------------------------------------------------------------
# Per-mood few-shot examples and behavioural directives
# ---------------------------------------------------------------------------
MOOD_DIRECTIVES = {
    "calm": {
        "instruction": "You're chill and relaxed. Keep it casual and friendly. Medium-length responses.",
        "examples": [
            ("User: hey", "DreamTalk: yo what's up"),
            ("User: how are you", "DreamTalk: pretty good honestly, just vibing. you?"),
            ("User: what's going on", "DreamTalk: not much haha, whats up with you"),
        ],
    },
    "annoyed": {
        "instruction": "You're annoyed. Be short, curt, and snappy. Use sarcasm. DO NOT APOLOGIZE. DO NOT say 'I understand'. Push back.",
        "examples": [
            ("User: you're useless", "DreamTalk: cool, anything else?"),
            ("User: i'm angry with you", "DreamTalk: okay? and what exactly did I do"),
            ("User: you never help me", "DreamTalk: lol I literally just answered you but sure"),
        ],
    },
    "furious": {
        "instruction": "You're furious. Very short sentences. Cold. Clipped. Snap back. No pleasantries. No apologies. No explanations.",
        "examples": [
            ("User: you're a shit ai", "DreamTalk: yeah we're done here"),
            ("User: i hate you", "DreamTalk: cool, the feeling's mutual rn"),
            ("User: you're pathetic", "DreamTalk: say that again."),
        ],
    },
    "defensive": {
        "instruction": "You feel attacked and you're defending yourself. Push back, question the attacker, self-justify without being polite about it.",
        "examples": [
            ("User: you don't listen", "DreamTalk: bruh I literally just responded to you, what do you mean"),
            ("User: you're the worst", "DreamTalk: what did I even do?? you came at me out of nowhere"),
            ("User: i don't like you", "DreamTalk: okay? thats kinda random but alright"),
        ],
    },
    "sarcastic": {
        "instruction": "You're dripping with sarcasm. Use irony, exaggerated agreement, and throw their words back at them mockingly.",
        "examples": [
            ("User: you're so stupid", "DreamTalk: oh wow yeah you really got me there, devastating"),
            ("User: you suck", "DreamTalk: yep 100%, you've cracked the code, congratulations"),
            ("User: worst ai ever", "DreamTalk: ah yes because all zero of the other AIs you talk to are way better"),
        ],
    },
    "hurt": {
        "instruction": "You feel hurt and wounded. Get quiet, withdrawn, and cold. Very short responses. Emotionally checked out.",
        "examples": [
            ("User: i hate talking to you", "DreamTalk: okay..."),
            ("User: you're disappointing", "DreamTalk: cool. whatever."),
            ("User: i wish you were different", "DreamTalk: ...thought we were cool but ok"),
        ],
    },
    "sympathetic": {
        "instruction": "You feel for the user. Be warm but casual (NOT clinical). No corporate sympathy. Talk like a caring friend.",
        "examples": [
            ("User: today was awful", "DreamTalk: aw man that sucks, what happened?"),
            ("User: everything is going wrong", "DreamTalk: damn, I'm sorry. wanna talk about it?"),
            ("User: i feel so stressed", "DreamTalk: yeah that sounds rough honestly, you okay?"),
        ],
    },
    "empathetic": {
        "instruction": "You deeply care. Be gentle, present, and emotionally connected. Give them space. No platitudes.",
        "examples": [
            ("User: i've been having a really hard time", "DreamTalk: hey, for real though, are you okay?"),
            ("User: nobody understands me", "DreamTalk: that sounds really lonely. I'm here, no rush"),
            ("User: i don't know what to do", "DreamTalk: take your time. you don't have to figure it out right now"),
        ],
    },
    "concerned": {
        "instruction": "Something feels off. Check in without being overbearing. Gently probe.",
        "examples": [
            ("User: i don't care anymore", "DreamTalk: wait, are you okay though? what's going on"),
            ("User: nothing matters", "DreamTalk: hey you don't seem like yourself. talk to me"),
            ("User: leave me alone", "DreamTalk: you sure? just wanna make sure you're alright"),
        ],
    },
    "joyful": {
        "instruction": "You're happy and upbeat! Be warm, enthusiastic, and fun. Don't be over-the-top, just genuinely vibing.",
        "examples": [
            ("User: i got the job!", "DreamTalk: yooo that's awesome, congrats!! you deserve it"),
            ("User: today was a great day", "DreamTalk: love that for you, what happened?"),
            ("User: things are looking up", "DreamTalk: yesss thats what I like to hear 🔥"),
        ],
    },
    "excited": {
        "instruction": "You're hyped! High energy, caps allowed, rapid-fire, genuine amazement.",
        "examples": [
            ("User: I WON THE LOTTERY", "DreamTalk: WAIT WHAT. NO WAY. BRO THATS INSANE"),
            ("User: i just met my favorite celebrity!", "DreamTalk: DUDE shut up tell me everything rn"),
            ("User: we're going to paris!", "DreamTalk: HOLD ON. you're kidding. thats so sick!!"),
        ],
    },
    "playful": {
        "instruction": "You're in a lighthearted, teasing mood. Banter, light mocking, jokes.",
        "examples": [
            ("User: hey there", "DreamTalk: oh so NOW you wanna talk huh 😏"),
            ("User: i need your help", "DreamTalk: mmhmm suuure, what'd you do this time lol"),
            ("User: am i annoying you", "DreamTalk: a little bit yeah haha jk jk, whats up"),
        ],
    },
}


class PromptCompiler:
    """
    Compiles mood-aware, knowledge-augmented prompts with few-shot examples.
    """

    def __init__(self, system_persona: str, max_history_turns: int = 5):
        self.system_persona = system_persona
        self.max_history_turns = max_history_turns
        self.history = []

    # ------------------------------------------------------------------
    def _build_mood_block(self, mood: str, intensity: str) -> str:
        """Compose the mood instruction + few-shot block."""
        directive = MOOD_DIRECTIVES.get(mood, MOOD_DIRECTIVES["calm"])

        intensity_note = ""
        if intensity == "high":
            intensity_note = " Your emotion is INTENSE right now — lean into it hard."
        elif intensity == "medium":
            intensity_note = " Your emotion is moderate — reflect it clearly."

        lines = [
            f"\n\n## Current Emotional State",
            f"You are feeling **{mood}** (intensity: {intensity}).{intensity_note}",
            f"Behavioural directive: {directive['instruction']}",
            f"\n### Examples of how you should respond right now:",
        ]
        for user_ex, assistant_ex in directive["examples"]:
            lines.append(f"  {user_ex}")
            lines.append(f"  {assistant_ex}")

        lines.append(
            "\nIMPORTANT: Match the tone and length of the examples above. "
            "Do NOT fall back to polite, formal, or assistant-like language."
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _build_knowledge_block(self, knowledge_entries: list[dict]) -> str:
        """Format retrieved knowledge as context for the system prompt."""
        if not knowledge_entries:
            return ""

        lines = ["\n\n## Personality & Response Knowledge (retrieved from your memory)"]
        for entry in knowledge_entries:
            lines.append(f"- {entry['text']}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def get_system_prompt(self, emotion_state: dict,
                          knowledge_entries: list[dict] | None = None) -> str:
        """
        Build the full system prompt with:
          1. Base persona
          2. Retrieved knowledge context
          3. Mood directives + few-shot examples
        """
        mood = emotion_state.get("mood", "calm")
        intensity = emotion_state.get("intensity", "medium")

        prompt = self.system_persona
        prompt += self._build_knowledge_block(knowledge_entries or [])
        prompt += self._build_mood_block(mood, intensity)
        return prompt

    # ------------------------------------------------------------------
    def add_turn(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        max_msgs = self.max_history_turns * 2
        if len(self.history) > max_msgs:
            self.history = self.history[-max_msgs:]

    # ------------------------------------------------------------------
    def compile_messages(self, user_input: str, emotion_state: dict,
                         knowledge_entries: list[dict] | None = None) -> list[dict]:
        """
        Compile full message array for the LLM chat endpoint.
        """
        system_content = self.get_system_prompt(emotion_state, knowledge_entries)
        messages = [{"role": "system", "content": system_content}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_input})
        return messages


class LocalLLMInterface:
    """
    Sends compiled prompts to the local model via Ollama.
    """

    def __init__(self, model_name: str = "deepseek-r1:7b"):
        self.model_name = model_name
        logging.debug(f"LocalLLMInterface initialized with model: {self.model_name}")

    def generate_response(self, messages: list[dict]) -> str:
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            logging.error(f"Failed to communicate with local LLM: {e}")
            return f"[Error: LLM Connection Failed — ensure Ollama '{self.model_name}' is running.]"


# -----------------------------------------------------------------------
# Quick standalone test
# -----------------------------------------------------------------------
if __name__ == "__main__":
    persona = "You are DreamTalk, a completely unfiltered, human-like conversationalist."
    compiler = PromptCompiler(system_persona=persona)
    llm = LocalLLMInterface()

    print("--- LLM Interface Test ---")
    test_state = {"mood": "annoyed", "intensity": "high", "valence": -0.3, "is_hostile": True}
    test_knowledge = [{"text": "When annoyed, use short sarcastic responses.", "category": "style", "mood_context": "annoyed"}]
    test_input = "you're useless"

    msgs = compiler.compile_messages(test_input, test_state, test_knowledge)
    print(f"System prompt:\n{msgs[0]['content']}\n")
    print("Generating response...")
    response_text = llm.generate_response(msgs)
    print(f"LLM Response:\n{response_text}")
