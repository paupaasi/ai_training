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

interface EmojiGeneratorOptions {
  prompt: string;
  output?: string;
  folder?: string;
  width?: number;
  height?: number;
  numOutputs?: number;
  negativePrompt?: string;
  steps?: number;
  seed?: number;
  loraScale?: number;
  loraWeights?: string;
  disableSafetyChecker?: boolean;
}

// Configure CLI
program
  .name('emoji-generator')
  .description('Generate custom emojis using Replicate')
  .version('1.0.0');

program
  .command('generate')
  .description('Generate emoji(s) from text prompt')
  .requiredOption('-p, --prompt <text>', 'Text prompt for emoji generation')
  .option('-o, --output <path>', 'Output file path (e.g., emoji.png). For multiple outputs, numbering is added automatically')
  .option('-f, --folder <path>', 'Output folder path', 'public/images')
  .option('-w, --width <number>', 'Emoji width in pixels (default: 1024)', (value) => parseInt(value, 10), 1024)
  .option('-h, --height <number>', 'Emoji height in pixels (default: 1024)', (value) => parseInt(value, 10), 1024)
  .option('-n, --num-outputs <number>', 'Number of emojis to generate (1-4, default: 1)', (value) => parseInt(value, 10), 1)
  .option('-s, --seed <number>', 'Random seed for reproducibility (default: -1 for random)', (value) => parseInt(value, 10), -1)
  .option('--steps <number>', 'Number of inference steps (1-500, default: 50)', (value) => parseInt(value, 10), 50)
  .option('--negative-prompt <text>', 'Negative prompt to avoid certain features')
  .option('--lora-scale <number>', 'LoRA additive scale (0-1, default: 0.6)', (value) => parseFloat(value), 0.6)
  .option('--lora-weights <string>', 'LoRA weights to use (default: microsoft)', 'microsoft')
  .option('--disable-safety-checker', 'Disable safety checker for generated images', false)
  .action(async (options: EmojiGeneratorOptions) => {
    await generateEmojis(options);
  });

async function generateEmojis(options: EmojiGeneratorOptions) {
  const spinner = ora('Initializing Replicate client...').start();

  try {
    // Validate API token
    if (!process.env.REPLICATE_API_TOKEN) {
      spinner.fail(chalk.red('Error: REPLICATE_API_TOKEN is not set in .env.local'));
      process.exit(1);
    }

    // Validate inputs
    const numOutputs = Math.max(1, Math.min(4, options.numOutputs || 1));
    if (numOutputs !== options.numOutputs) {
      spinner.warn(chalk.yellow(`⚠️  Clamping num-outputs to range [1-4]: ${options.numOutputs} → ${numOutputs}`));
    }

    const steps = Math.max(1, Math.min(500, options.steps || 50));
    if (steps !== options.steps) {
      spinner.warn(chalk.yellow(`⚠️  Clamping steps to range [1-500]: ${options.steps} → ${steps}`));
    }

    // Ensure output directory exists
    if (!fs.existsSync(options.folder)) {
      fs.mkdirSync(options.folder, { recursive: true });
      spinner.text = `Created output directory: ${options.folder}`;
    }

    // Initialize Replicate client
    const replicate = new Replicate({
      auth: process.env.REPLICATE_API_TOKEN,
    });

    // Prepare input parameters
    const input: Record<string, unknown> = {
      prompt: options.prompt,
      width: options.width || 1024,
      height: options.height || 1024,
      num_outputs: numOutputs,
      num_inference_steps: steps,
      seed: options.seed !== -1 ? options.seed : -1,
      lora_scale: Math.max(0, Math.min(1, options.loraScale || 0.6)),
      lora_weights: options.loraWeights || 'microsoft',
      disable_safety_checker: options.disableSafetyChecker || false,
    };

    // Add negative prompt if provided
    if (options.negativePrompt) {
      input.negative_prompt = options.negativePrompt;
    }

    spinner.text = chalk.cyan(`Generating ${numOutputs} emoji(s) with prompt: "${options.prompt}"`);

    // Generate emojis using zedge/emoji-generator
    const output = await replicate.run(
      'zedge/emoji-generator:3545c6eeeb6c95e22a386a4f945423de3b277ce18a9abfd6ebc70af1e76fdd9d' as any,
      { input }
    );

    spinner.text = chalk.cyan('Downloading generated emoji(s)...');

    // Handle output - can be array or single string
    let imageUrls: string[] = [];
    if (Array.isArray(output)) {
      imageUrls = output as string[];
    } else if (typeof output === 'string') {
      imageUrls = [output];
    } else {
      throw new Error('Unexpected output format from Replicate');
    }

    // Download images
    const outputPaths: string[] = [];
    for (let i = 0; i < imageUrls.length; i++) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      
      let outputFilename: string;
      if (options.output) {
        // If multiple outputs, add index to filename
        if (imageUrls.length > 1) {
          const ext = path.extname(options.output);
          const base = path.basename(options.output, ext);
          outputFilename = `${base}-${i + 1}${ext}`;
        } else {
          outputFilename = options.output;
        }
      } else {
        outputFilename = `emoji-${timestamp}${imageUrls.length > 1 ? `-${i + 1}` : ''}.png`;
      }

      const outputPath = path.isAbsolute(outputFilename)
        ? outputFilename
        : path.join(options.folder, outputFilename);

      // Download the image
      const response = await axios.get(imageUrls[i], { responseType: 'arraybuffer' });
      fs.writeFileSync(outputPath, response.data);
      outputPaths.push(outputPath);
    }

    // Display success message
    if (outputPaths.length === 1) {
      spinner.succeed(
        chalk.green(`✅ Emoji generated successfully!`) +
        `\n${chalk.gray(`Location: ${outputPaths[0]}`)}` +
        `\n${chalk.gray(`Size: ${options.width}x${options.height}`)}` +
        `\n${chalk.gray(`Model: zedge/emoji-generator`)}`
      );
    } else {
      spinner.succeed(
        chalk.green(`✅ ${outputPaths.length} emojis generated successfully!`) +
        `\n${chalk.gray(`Locations:\n  - ${outputPaths.join('\n  - ')}`)}` +
        `\n${chalk.gray(`Size: ${options.width}x${options.height} each`)}` +
        `\n${chalk.gray(`Model: zedge/emoji-generator`)}`
      );
    }

  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    spinner.fail(chalk.red(`Error generating emoji: ${message}`));
    process.exit(1);
  }
}

// Show help on no command
if (!process.argv.slice(2).length) {
  program.outputHelp();
}

program.parse(process.argv);
