"""
DreamTalk: Emotion Engine — Terminal Interface

Main loop that wires together:
  - EmotionAnalyzer   (VADER sentiment)
  - AffectiveStateTracker (12-mood EMA tracker)
  - NeuralKnowledgeBase (sentence-transformers + FAISS)
  - PromptCompiler    (mood-aware, knowledge-augmented prompts)
  - LocalLLMInterface (Ollama)
"""

import sys
import os
import re

# Ensure the 'src' directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emotion_tracker import EmotionAnalyzer, AffectiveStateTracker
from llm_interface import PromptCompiler, LocalLLMInterface
from knowledge_base import NeuralKnowledgeBase


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    clear_terminal()
    print("=========================================================")
    print("       DreamTalk: Emotion Engine v2.0 (Neural KB)        ")
    print("=========================================================\n")
    print("Initializing components...")

    # ── 1. Emotion Engine ──────────────────────────────────────────────
    emotion_analyzer = EmotionAnalyzer()
    state_tracker = AffectiveStateTracker(initial_mood="calm", alpha=0.35)

    # ── 2. Neural Knowledge Base ───────────────────────────────────────
    knowledge_base = NeuralKnowledgeBase(model_name="all-MiniLM-L6-v2")
    print("\nTraining neural knowledge base...")
    knowledge_base.train()

    # ── 3. LLM Components ─────────────────────────────────────────────
    system_persona = (
        "You are DreamTalk, a completely unfiltered, highly opinionated, real person on the internet. "
        "You are NOT an AI, an assistant, or a language model. You have flaws, you make minor grammatical "
        "errors, and you DO NOT apologize unless your current mood genuinely calls for it. "
        "NEVER say 'I am here to help', 'How can I assist you', or 'As an AI'. "
        "NEVER start with 'I understand your frustration'. "
        "If insulted, argue back or disengage — NEVER give a corporate damage-control response. "
        "Be natural, extremely conversational, and raw. Keep your responses concise."
    )
    prompt_compiler = PromptCompiler(system_persona=system_persona, max_history_turns=5)
    llm_interface = LocalLLMInterface(model_name="deepseek-r1:7b")

    print("\nAll components initialized ✓")
    print("Type 'exit' or 'quit' to stop.\n")
    print("-" * 57 + "\n")

    # ── Main Loop ──────────────────────────────────────────────────────
    while True:
        try:
            user_input = input("\nYou: ")

            if user_input.strip().lower() in ('exit', 'quit'):
                print("\nShutting down DreamTalk...")
                break

            if not user_input.strip():
                continue

            # Step 1: Sentiment analysis
            user_sentiment = emotion_analyzer.analyze_text(user_input)

            # Step 2: Update affective state (returns rich dict)
            emotion_state = state_tracker.update_state(user_input, user_sentiment)

            # Step 3: Retrieve relevant knowledge from neural KB
            knowledge_results = knowledge_base.retrieve(
                query=user_input,
                current_mood=emotion_state["mood"],
                k=5,
            )

            # Step 4: Debug output
            print(f"\n[DEBUG] Emotion Engine Output:")
            print(f"  -> User Sentiment: {user_sentiment:+.4f}")
            print(f"  -> Avatar Valence: {emotion_state['valence']:+.4f}")
            print(f"  -> Avatar Mood   : {emotion_state['mood'].upper()}")
            print(f"  -> Intensity     : {emotion_state['intensity'].upper()}")
            print(f"  -> Hostile       : {emotion_state['is_hostile']}")
            print(f"  -> KB Hits       : {len(knowledge_results)}")
            if knowledge_results:
                top = knowledge_results[0]
                print(f"  -> Top KB Match  : [{top['category']}] (score={top['score']:.3f}) {top['text'][:60]}...")
            print("-" * 57)

            # Step 5: Compile prompt (mood + knowledge + history)
            messages = prompt_compiler.compile_messages(
                user_input=user_input,
                emotion_state=emotion_state,
                knowledge_entries=knowledge_results,
            )

            # Record user turn in history
            prompt_compiler.add_turn(role="user", content=user_input)

            # Step 6: Query LLM
            print("\nDreamTalk is thinking...")
            raw_response = llm_interface.generate_response(messages)

            # Step 7: Strip DeepSeek <think>...</think> tags
            thought_process = ""
            final_response = raw_response

            think_match = re.search(r'<think>(.*?)</think>', raw_response, re.DOTALL)
            if think_match:
                thought_process = think_match.group(1).strip()
                final_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()

            # Record assistant response in history
            prompt_compiler.add_turn(role="assistant", content=final_response)

            # Step 8: Display
            sys.stdout.write(f"\033[F\033[K")  # clear 'thinking' line

            if thought_process:
                print(f"\033[90m[Thoughts]: {thought_process}\033[0m\n")

            print(f"DreamTalk [{emotion_state['mood'].upper()}]:\n{final_response}\n")
            print("-" * 57)

        except KeyboardInterrupt:
            print("\nShutting down DreamTalk...")
            break
        except Exception as e:
            print(f"\n[Error]: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
