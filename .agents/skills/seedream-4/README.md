# Seedream-4 Tool

Text-to-image generation using ByteDance's Seedream-4 model via Replicate API.

## Overview

This tool generates high-quality images from text prompts using ByteDance's Seedream-4 model, a state-of-the-art text-to-image generation model available on Replicate.

## Key Features

- **High-Quality Output**: Supports up to 2048x2048 pixel images
- **Fine-Grained Control**: Adjustable guidance scale, inference steps, and seeds
- **Reproducible Results**: Use seeds to generate identical images
- **Negative Prompts**: Specify what to avoid in generated images
- **Batch Processing**: Can be integrated into scripts and automation

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
npm run seedream-4 -- generate --prompt "A serene mountain landscape at sunset"
```

## Model Details

- **Model**: ByteDance Seedream-4
- **Replicate URL**: https://replicate.com/bytedance/seedream-4
- **Input**: Text prompt, optional negative prompt
- **Output**: PNG image
- **Dimensions**: 512-2048px (width and height)
- **Control Parameters**:
  - Guidance Scale: 1.0-10.0 (higher = more prompt adherence)
  - Inference Steps: 25-100 (higher = better quality, slower)
  - Seed: Optional for reproducibility

## File Structure

```
seedream-4/
├── SKILL.md          # Complete command reference
└── README.md         # This file
```
