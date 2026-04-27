---
name: emoji-generator
description: Use for generating custom emoji-style images using Replicate's zedge/emoji-generator model. Supports text-to-emoji generation with fine-grained control over size, quality, and style via LoRA weights. Generates high-quality emoji images from descriptive text prompts.
---

## Command
`npm run emoji-generator -- generate [options]`

## Options
| Flag | Required | Description |
|------|----------|-------------|
| --prompt, -p | Yes | Text prompt for emoji generation |
| --output, -o | No | Output file path (default: emoji-TIMESTAMP.png). For multiple outputs, numbering is added automatically |
| --folder, -f | No | Output folder path (default: public/images) |
| --width, -w | No | Emoji width in pixels (default: 1024) |
| --height, -h | No | Emoji height in pixels (default: 1024) |
| --num-outputs, -n | No | Number of emojis to generate, 1-4 (default: 1) |
| --seed, -s | No | Random seed for reproducibility (default: -1 = random) |
| --steps | No | Number of inference steps, 1-500 (default: 50) |
| --negative-prompt | No | Negative prompt to avoid certain features |
| --lora-scale | No | LoRA additive scale, 0-1 (default: 0.6). Controls influence of style weights |
| --lora-weights | No | LoRA weights to use (default: microsoft). Other option: "microsoft" or custom |
| --disable-safety-checker | No | Disable safety checker for generated images. API-only feature |

## Requirements
- `REPLICATE_API_TOKEN` in `.env.local`
- Replicate API token from https://replicate.com/account/api-tokens

## Examples

```bash
# Basic emoji generation
npm run emoji-generator -- generate --prompt "a cute dog wearing sunglasses"

# Custom size emoji
npm run emoji-generator -- generate --prompt "a rocket ship in space" --width 512 --height 512

# Multiple variations
npm run emoji-generator -- generate --prompt "a coffee cup with steam" --num-outputs 3

# High-quality output with more steps
npm run emoji-generator -- generate --prompt "a magical crystal" --steps 100 --lora-scale 0.8

# Reproducible output with seed
npm run emoji-generator -- generate --prompt "a golden star" --seed 42 --output star.png

# With negative prompt for better results
npm run emoji-generator -- generate --prompt "a cartoon cat" --negative-prompt "blurry, distorted, ugly" --num-outputs 2

# Custom output folder
npm run emoji-generator -- generate --prompt "a pizza slice" --folder emojis --output pizza.png

# Fine-tuned parameters
npm run emoji-generator -- generate \
  --prompt "a cozy campfire" \
  --width 1024 \
  --height 1024 \
  --steps 75 \
  --lora-scale 0.7 \
  --seed 123 \
  --num-outputs 2
```

## Tips & Best Practices

### Prompts
- **Be descriptive**: Use specific style descriptors like "professional emoji design", "cartoon style", "simple 3D geometric"
- **Include context**: Specify what the emoji should be doing or wearing
- **Anthropomorphize when needed**: Emojis work best when they have character and personality
- **Example good prompt**: "A cheerful robot with big eyes, minimalist geometric design, professional emoji style"

### Quality Tuning
- **Steps**: More steps (75-100) improve quality but take longer. Use 50 for faster iteration, 100 for final output
- **LoRA Scale**: Controls the strength of the style. 0.6 is balanced, 0.8+ for stronger style, 0.3-0.4 for more creative freedom
- **Negative Prompt**: Use to avoid common issues like "blurry, distorted, multiple subjects, background, photorealistic, shadows"

### Reproducibility
- **Same prompt + same seed** = identical output
- Use seed mode for consistent emoji variations across batches
- Useful for character design where you need multiple expressions with same base

### Batch Generation
- Use `--num-outputs 4` to generate up to 4 variations at once
- Outputs are automatically numbered (emoji-1.png, emoji-2.png, etc.)
- More cost-effective than multiple API calls

### Size Recommendations
- **1024x1024**: Default, good for all purposes
- **512x512**: Faster generation, good for previews
- **1024x512** or **512x1024**: Useful for specific aspect ratios if needed

## Model Details
- **Model**: zedge/emoji-generator
- **Provider**: Replicate
- **Typical generation time**: ~1 second
- **Cost**: ~$0.0014 per image
- **Hardware**: NVIDIA A100 (80GB) GPU

## Integration Notes
- Supports LoRA weights for style customization (default: microsoft)
- Can disable safety checker via API for unrestricted generation
- Outputs are typically PNG format
- Multiple outputs handled automatically with sequential numbering
