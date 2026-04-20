# Emotion Engine (PAD Model)

The Emotion Engine is the reactive core of DreamTalk v3.5. It implements the **Pleasure-Arousal-Dominance (PAD)** model, which provides a significantly more nuanced emotional space than traditional sentiment systems.

## The PAD Dimensions

1. **Pleasure (P)**: Measures how pleasant or unpleasant an emotion is.
   - Range: -1.0 (Extreme Distress/Pain) to +1.0 (Extreme Happiness/Ecstasy).
   - In DreamTalk, this is primarily driven by the semantic sentiment of the user's input.
2. **Arousal (A)**: Measures the level of physical or mental activation.
   - Range: -1.0 (Sleepy/Apathetic) to +1.0 (Frantic/Excited).
   - This dimension determines the "energy" of DreamTalk's responses.
3. **Dominance (D)**: Measures the level of control or influence.
   - Range: -1.0 (Submissive/Fearful) to +1.0 (Powerful/Aggressive).
   - This determines whether DreamTalk is assertive or withdrawn in its interaction.

## Emotional States & Mapping
DreamTalk maps **50+ discrete emotional states** within this 3D PAD space. The system uses Euclidean distance to find the closest named emotion to its current internal PAD values.

### Example Mappings:
- **Ecstasy**: P=+0.9, A=+0.9, D=+0.8 (Highly positive, highly energetic, highly in control).
- **Rage**: P=-0.9, A=+1.0, D=+0.8 (Highly negative, maximum activation, high control).
- **Grief**: P=-0.9, A=-0.2, D=-0.7 (Highly negative, low activation, low control).
- **Sarcasm**: P=-0.2, A=+0.4, D=+0.5 (Slightly negative, moderate activation, moderate control).

## Key Implementation Features

### 1. Emotional Inertia
Unlike simple chatbots that switch moods instantly, DreamTalk features **Emotional Inertia**. The `inertia` parameter (default 0.85) ensures that the current mood resists sudden changes. A single negative comment won't turn a "Joyful" DreamTalk "Furious" instantly; it requires sustained interaction to shift the emotional baseline.

### 2. Emotional Blending
The engine identifies both a **Primary** and a **Secondary** emotion based on proximity in PAD space. This allows the Brain Simulation to create "blended" reactions, such as a response that is primarily "Annoyed" but has secondary "Sarcastic" undertones.

### 3. Intensity Scaling
The Arousal dimension is mapped to five intensity levels:
- **Minimal**: < -0.4
- **Low**: -0.4 to 0.0
- **Medium**: 0.0 to 0.4
- **High**: 0.4 to 0.7
- **Extreme**: > 0.7

## Technical Usage
The `PADEmotionEngine` class in [engine.py](../backend/emotion/engine.py) provides the following interface:

```python
# Update with a new stimulus (P, A, D)
current_state = engine.update((0.8, 0.5, 0.4))

# Returns:
# {
#   "name": "joy",
#   "display_name": "Joy",
#   "secondary_emotion": "Excited",
#   "pad": [0.72, 0.45, 0.36],
#   "intensity": "high"
# }
```

---
[Next: Brain Simulation (Neural Layers)](brain_simulation.md)
