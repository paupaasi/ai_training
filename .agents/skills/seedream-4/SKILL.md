---
name: seedream-4
description: Use for text-to-image generation with ByteDance Seedream-4 via Replicate API. Supports high-quality image generation with fine-grained control over dimensions, guidance scale, and random seeds for reproducibility.
---

## Command
`npm run seedream-4 -- generate [options]`

## Options
| Flag | Required | Description |
|------|----------|-------------|
| --prompt, -p | Yes | Text prompt for image generation |
| --output, -o | No | Output file path (default: seedream-TIMESTAMP.png) |
| --folder, -f | No | Output folder path (default: public/images) |
| --width, -w | No | Image width in pixels (1024-2048, default: 1024) |
| --height, -h | No | Image height in pixels (1024-2048, default: 1024) |
| --seed, -s | No | Random seed for reproducibility (default: 0 = random) |
| --steps | No | Number of generation steps, 25-100 (default: 50) |
| --guidance, -g | No | Guidance scale for prompt adherence, 1.0-10.0 (default: 7.5) |
| --negative-prompt, -n | No | Negative prompt to avoid certain features |

## Requirements
- `REPLICATE_API_TOKEN` in `.env.local`
- Replicate API token from https://replicate.com/account/api-tokens

## Examples
```bash
# Basic text-to-image
npm run seedream-4 -- generate --prompt "A serene mountain landscape at sunset"

# With custom dimensions
npm run seedream-4 -- generate --prompt "A futuristic city skyline" --width 1024 --height 512

# With negative prompt for better quality
npm run seedream-4 -- generate --prompt "A realistic portrait of a person" --width 512 --height 512 --negative-prompt "blurry, low quality"

# Fine-tuned with guidance and steps
npm run seedream-4 -- generate --prompt "Abstract colorful art" --guidance 8.5 --steps 75

# Reproducible output with seed
npm run seedream-4 -- generate --prompt "A golden retriever playing fetch" --seed 42 --output dog.png

# Custom output location
npm run seedream-4 -- generate --prompt "Ocean waves" --folder generated_images --output waves.png
```

## Tips & Best Practices
- **Guidance Scale**: Higher values (7-10) make the model follow your prompt more strictly. Lower values (1-4) allow more creativity.
- **Steps**: More steps generally improve quality but take longer (25-50 for fast results, 75-100 for best quality).
- **Seed**: Use the same seed with the same prompt to generate identical images.
- **Negative Prompts**: Add what you don't want (e.g., "ugly, distorted") to improve results.
- **Dimensions**: Aspect ratios like 1:1 (square), 16:9 (wide), or 9:16 (portrait) work best.
