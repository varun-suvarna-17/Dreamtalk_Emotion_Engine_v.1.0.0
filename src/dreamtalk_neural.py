"""
DreamTalk: Neural Emotion Engine - Human Brain Mimicry

Replaces template-based responses with true neural decision-making:
- Emotional neurons process sentiment
- Personality neurons determine style  
- Creative neurons generate organic responses
- No pre-defined templates or patterns
"""

import sys
import os
import re
import time

# Ensure the 'src' directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emotion_tracker import EmotionAnalyzer, AffectiveStateTracker
from human_neural_engine import HumanNeuralEngine
from http_llm_interface import HTTPLLMInterface


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    clear_terminal()
    print("=========================================================")
    print("     DreamTalk: Neural Emotion Engine v3.0 (Brain-Mimic)    ")
    print("=========================================================\n")
    print("Initializing neural components...")

    # ── 1. Emotion Engine (Limbic System Analog) ──────────────────────
    emotion_analyzer = EmotionAnalyzer()
    state_tracker = AffectiveStateTracker(initial_mood="calm", alpha=0.35)

    # ── 2. Human Neural Engine (Advanced Brain-Mimicry) ───────────────────
    human_engine = HumanNeuralEngine()
    
    # ── 3. HTTP LLM Interface (For actual response generation) ──────────────
    neural_llm = HTTPLLMInterface(model_name="llama3.1:8b")

    print("\nNeural components initialized ✓")
    print("Type 'exit' or 'quit' to stop. Type 'clear' to reset memory.\n")
    print("-" * 65 + "\n")

    # ── Main Neural Processing Loop ──────────────────────────────────
    while True:
        try:
            user_input = input("\nYou: ")

            if user_input.strip().lower() in ('exit', 'quit'):
                print("\nShutting down neural engine...")
                break

            if user_input.strip().lower() == 'clear':
                human_engine.clear_history()
                print("\n🧠 Human neural memory cleared. Starting fresh...\n")
                continue

            if not user_input.strip():
                continue

            # Step 1: Neural Sentiment Analysis (Amygdala)
            user_sentiment = emotion_analyzer.analyze_text(user_input)

            # Step 2: Update Affective State (Limbic System)
            emotion_state = state_tracker.update_state(user_input, user_sentiment)

            # Step 3: Debug Output - Neural Activation
            print(f"\n[NEURAL DEBUG] Emotion Engine Output:")
            print(f"  -> User Sentiment: {user_sentiment:+.4f}")
            print(f"  -> Avatar Valence: {emotion_state['valence']:+.4f}")
            print(f"  -> Neural Mood    : {emotion_state['mood'].upper()}")
            print(f"  -> Intensity      : {emotion_state['intensity'].upper()}")
            print(f"  -> Hostile Signal : {emotion_state['is_hostile']}")
            print("-" * 65)

            # Step 4: Neural Response Generation (Full Brain Processing)
            print("\n🧠 Neural processing...")
            
            # Add small delay to simulate neural processing time
            time.sleep(0.3)
            
            # Generate human prompt through neural pipeline
            human_prompt, neural_metadata = human_engine.process_input(
                user_input, user_sentiment
            )
            
            # Get actual response from LLM using the human-generated prompt
            neural_response = neural_llm._http_generate_response([
                {"role": "system", "content": human_prompt},
                {"role": "user", "content": user_input}
            ])

            # Step 5: Display Neural Response
            sys.stdout.write(f"\033[F\033[K")  # clear 'processing' line

            print(f"\nDreamTalk [{emotion_state['mood'].upper()}]:")
            print(f"{neural_response}")
            
            # Show neural metadata for educational purposes
            if emotion_state['intensity'] == 'high' or abs(user_sentiment) > 0.6:
                emotional_activation = neural_metadata.get('emotional_activation', {})
                if emotional_activation:
                    primary_emotion = max(emotional_activation.items(), key=lambda x: x[1])
                    print(f"\n\033[90m[Neural Insight]: {primary_emotion[0].upper()} neuron group activated ({primary_emotion[1]:.2f})\033[0m")
            
            print("-" * 65)

        except KeyboardInterrupt:
            print("\nShutting down neural engine...")
            break
        except Exception as e:
            print(f"\n[Neural Error]: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()