# Emoji Generator Tool

Generate custom emoji-style images from text prompts using Replicate's zedge/emoji-generator model.

## Overview

This tool creates high-quality emoji-style illustrations from descriptive text prompts using Zedge's emoji generator model on Replicate. Perfect for creating custom emojis, stickers, avatars, and app icons.

## Key Features

- **Batch Generation**: Generate up to 4 emojis in a single API call
- **Fine-Grained Control**: Adjustable dimensions, inference steps, and LoRA weights
- **Style Customization**: Control emoji aesthetic with LoRA scale parameter
- **Reproducible Results**: Use seeds to generate identical outputs
- **Negative Prompts**: Specify what to avoid for better quality
- **Automatic Numbering**: Batch outputs are automatically numbered

## Setup

1. Get a Replicate API token from https://replicate.com/account/api-tokens
2. Add to `.env.local`:
   ```
   REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxx
   ```

## Usage

See [SKILL.md](SKILL.md) for complete command reference and examples.

Quick start:
```bash
npm run emoji-generator -- generate --prompt "a cute dog wearing sunglasses"
```

Generate multiple variations:
```bash
npm run emoji-generator -- generate --prompt "a coffee cup" --num-outputs 3
```

## Model Details

- **Model**: zedge/emoji-generator
- **Provider**: Replicate
- **Replicate URL**: https://replicate.com/zedge/emoji-generator
- **Input**: Text prompt, optional negative prompt
- **Output**: PNG image(s)
- **Default Size**: 1024x1024 pixels
- **Typical Generation Time**: ~1 second
- **Cost**: ~$0.0014 per image
- **Control Parameters**:
  - Inference Steps: 1-500 (default 50, higher = better quality)
  - LoRA Scale: 0-1 (default 0.6, controls style influence)
  - LoRA Weights: Style weights (default "microsoft")
  - Seed: For reproducible outputs (default -1 = random)
  - Num Outputs: 1-4 images per request (default 1)

## File Structure

```
emoji-generator/
├── SKILL.md          # Complete command reference and examples
└── README.md         # This file
```

## Common Use Cases

### Avatar Creation
```bash
npm run emoji-generator -- generate \
  --prompt "a professional avatar, person, cartoon style" \
  --num-outputs 4 \
  --folder avatars
```

### Sticker Pack Generation
```bash
npm run emoji-generator -- generate \
  --prompt "a happy emoji character" \
  --num-outputs 4 \
  --width 512 \
  --height 512
```

### Consistent Character Design (with seed)
```bash
npm run emoji-generator -- generate \
  --prompt "a cute robot with big eyes" \
  --seed 42 \
  --num-outputs 2 \
  --lora-scale 0.8
```

### High-Quality Output
```bash
npm run emoji-generator -- generate \
  --prompt "a magical crystal glowing" \
  --steps 100 \
  --lora-scale 0.75 \
  --output crystal.png
```

## Prompting Tips

**Good prompt structure**:
```
[character/object] + [style descriptor] + [emoji design note]
```

Examples:
- "A cheerful robot with big round eyes, minimalist geometric design, professional emoji style"
- "A coffee cup with steam rising, warm colors, cute cartoon emoji design"
- "A magical crystal, glowing effect, simple 3D geometric shapes, professional emoji"
- "A friendly dinosaur wearing a top hat, cartoon style, centered, emoji design"

**Avoid in prompts** (use negative prompt instead):
- Multiple subjects or characters
- Background elements
- Photorealistic style (use "cartoon" or "emoji" instead)
- Text or watermarks

## Best Practices

### Quality Tuning
- **Fast iteration**: `--steps 30` for quick previews
- **Standard quality**: `--steps 50` (default)
- **High quality**: `--steps 100` for final outputs
- **Highest quality**: `--steps 200` for best results

### Style Control
- `--lora-scale 0.4-0.5`: Maximum creative freedom
- `--lora-scale 0.6`: Balanced (default)
- `--lora-scale 0.8+`: Strong adherence to style

### Batch Generation
- Use `--num-outputs 4` to get 4 variations at once
- More cost-effective than multiple API calls
- All variations are auto-numbered: `-1.png`, `-2.png`, etc.

### Reproducibility
- Save successful seeds for future use
- Same prompt + same seed = identical output
- Useful for character design across multiple expressions

## Related Resources

- **Replicate**: https://replicate.com/zedge/emoji-generator
- **Main SKILL.md**: [SKILL.md](SKILL.md)
- **Similar Tools**:
  - [seedream-4](./../seedream-4/) — High-quality image generation
  - [gemini-image](./../gemini-image/) — Google Gemini image generation
  - [openai-image](./../openai-image/) — OpenAI image generation
  - [sprite-animator](./../sprite-animator/) — Game sprite animation

## Troubleshooting

### "404 Not Found" error
- Verify `REPLICATE_API_TOKEN` is set in `.env.local`
- Check that token is valid and has not expired
- Ensure you're on the latest tool version

### Generated emojis don't match prompt
- Add more descriptive style indicators to prompt
- Try higher `--steps` value (75-100)
- Use negative prompt to exclude unwanted features
- Adjust `--lora-scale` to balance creativity vs style

### API rate limiting
- Replicate allows multiple simultaneous predictions
- If rate limited, wait a moment and retry
- Consider batching with `--num-outputs` instead of multiple calls

## Version History

- **v1.0.0** (Apr 21, 2026): Initial release
  - Text-to-emoji generation
  - Batch output support
  - LoRA weight customization
  - Seed-based reproducibility
