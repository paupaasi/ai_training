#!/usr/bin/env node

import Replicate from 'replicate';
import { config } from 'dotenv';
import { program } from 'commander';
import chalk from 'chalk';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';
import ora from 'ora';

// Load environment variables from .env.local
config({
  path: process.env.NODE_ENV === 'development' ? '.env.local' : '.env'
});

interface SeedreamOptions {
  prompt: string;
  output?: string;
  folder?: string;
  width?: number;
  height?: number;
  seed?: number;
  steps?: number;
  guidance?: number;
  negativePrompt?: string;
}

// Configure CLI
program
  .name('seedream-4')
  .description('Generate images using ByteDance Seedream-4 via Replicate')
  .version('1.0.0');

program
  .command('generate')
  .description('Generate an image from text prompt')
  .requiredOption('-p, --prompt <text>', 'Text prompt for image generation')
  .option('-o, --output <path>', 'Output file path (e.g., seedream-image.png)')
  .option('-f, --folder <path>', 'Output folder path', 'public/images')
  .option('-w, --width <number>', 'Image width in pixels (1024-2048)', (value) => parseInt(value, 10), 1024)
  .option('-h, --height <number>', 'Image height in pixels (1024-2048)', (value) => parseInt(value, 10), 1024)
  .option('-s, --seed <number>', 'Random seed for reproducibility', (value) => parseInt(value, 10), 0)
  .option('--steps <number>', 'Number of generation steps (25-100)', (value) => parseInt(value, 10), 50)
  .option('-g, --guidance <number>', 'Guidance scale for prompt adherence (1.0-10.0)', (value) => parseFloat(value), 7.5)
  .option('-n, --negative-prompt <text>', 'Negative prompt to avoid certain features')
  .action(async (options: SeedreamOptions) => {
    await generateImage(options);
  });

async function generateImage(options: SeedreamOptions) {
  const spinner = ora('Initializing Replicate client...').start();

  try {
    // Validate API token
    if (!process.env.REPLICATE_API_TOKEN) {
      spinner.fail(chalk.red('Error: REPLICATE_API_TOKEN is not set in .env.local'));
      process.exit(1);
    }

    // Ensure output directory exists
    if (!fs.existsSync(options.folder)) {
      fs.mkdirSync(options.folder, { recursive: true });
      spinner.text = `Created output directory: ${options.folder}`;
    }

    // Determine output filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const outputFilename = options.output || `seedream-${timestamp}.png`;
    const outputPath = path.isAbsolute(outputFilename)
      ? outputFilename
      : path.join(options.folder, outputFilename);

    // Initialize Replicate client
    const replicate = new Replicate({
      auth: process.env.REPLICATE_API_TOKEN,
    });

    // Prepare input parameters
    const input: Record<string, unknown> = {
      prompt: options.prompt,
      width: Math.max(1024, Math.min(2048, options.width || 1024)),
      height: Math.max(1024, Math.min(2048, options.height || 1024)),
      seed: options.seed !== 0 ? options.seed : undefined,
      num_inference_steps: Math.max(25, Math.min(100, options.steps || 50)),
      guidance_scale: Math.max(1.0, Math.min(10.0, options.guidance || 7.5)),
    };

    // Add negative prompt if provided
    if (options.negativePrompt) {
      input.negative_prompt = options.negativePrompt;
    }

    spinner.text = chalk.cyan(`Generating image with prompt: "${options.prompt}"`);

    // Generate image using Seedream-4
    const output = await replicate.run(
      'bytedance/seedream-4' as any,
      { input }
    );

    spinner.text = chalk.cyan('Downloading generated image...');

    // Handle output
    let imageUrl: string;
    if (Array.isArray(output)) {
      imageUrl = output[0] as string;
    } else if (typeof output === 'string') {
      imageUrl = output;
    } else {
      throw new Error('Unexpected output format from Replicate');
    }

    // Download the image
    const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    fs.writeFileSync(outputPath, response.data);

    spinner.succeed(
      chalk.green(`✅ Image generated successfully!`) +
      `\n${chalk.gray(`Location: ${outputPath}`)}` +
      `\n${chalk.gray(`Size: ${options.width}x${options.height}`)}` +
      `\n${chalk.gray(`Model: ByteDance Seedream-4`)}`
    );

  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    spinner.fail(chalk.red(`Error generating image: ${message}`));
    process.exit(1);
  }
}

// Show help on no command
if (!process.argv.slice(2).length) {
  program.outputHelp();
}

program.parse(process.argv);
