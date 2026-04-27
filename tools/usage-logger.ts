import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { program } from 'commander';

const LOG_DIR = process.env.LOG_DIR || path.join(process.cwd(), 'logs');
const LOG_FILE = process.env.LOG_FILE || 'usage.log.json';

interface LogEntry {
  id: string;
  timestamp: string;
  type: 'tool' | 'agent' | 'action';
  name: string;
  input?: Record<string, unknown>;
  output?: unknown;
  error?: string;
  duration_ms?: number;
  metadata?: Record<string, unknown>;
}

function ensureLogDir() {
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
}

function readLogs(): LogEntry[] {
  const logPath = path.join(LOG_DIR, LOG_FILE);
  if (!fs.existsSync(logPath)) {
    return [];
  }
  try {
    const content = fs.readFileSync(logPath, 'utf-8');
    return content.trim() ? JSON.parse(content) : [];
  } catch {
    return [];
  }
}

function writeLogs(entries: LogEntry[]) {
  ensureLogDir();
  const logPath = path.join(LOG_DIR, LOG_FILE);
  fs.writeFileSync(logPath, JSON.stringify(entries, null, 2));
}

function appendLog(entry: Omit<LogEntry, 'id' | 'timestamp'>) {
  const entries = readLogs();
  const newEntry: LogEntry = {
    ...entry,
    id: uuidv4(),
    timestamp: new Date().toISOString(),
  };
  entries.push(newEntry);
  writeLogs(entries);
  return newEntry;
}

export function logToolUsage(
  name: string,
  input?: Record<string, unknown>,
  output?: unknown,
  error?: string,
  duration_ms?: number,
  metadata?: Record<string, unknown>
) {
  return appendLog({
    type: 'tool',
    name,
    input,
    output,
    error,
    duration_ms,
    metadata,
  });
}

export function logAgentAction(
  name: string,
  action: string,
  input?: Record<string, unknown>,
  output?: unknown,
  error?: string,
  duration_ms?: number,
  metadata?: Record<string, unknown>
) {
  return appendLog({
    type: 'agent',
    name: `${name}:${action}`,
    input,
    output,
    error,
    duration_ms,
    metadata,
  });
}

export function logAction(
  name: string,
  input?: Record<string, unknown>,
  output?: unknown,
  error?: string,
  duration_ms?: number,
  metadata?: Record<string, unknown>
) {
  return appendLog({
    type: 'action',
    name,
    input,
    output,
    error,
    duration_ms,
    metadata,
  });
}

export function getLogs(type?: LogEntry['type'], limit = 100): LogEntry[] {
  const entries = readLogs();
  let filtered = entries;
  if (type) {
    filtered = entries.filter((e) => e.type === type);
  }
  return filtered.slice(-limit);
}

export function clearLogs() {
  const logPath = path.join(LOG_DIR, LOG_FILE);
  if (fs.existsSync(logPath)) {
    fs.unlinkSync(logPath);
  }
}

export { LOG_DIR, LOG_FILE, LogEntry };

if (require.main === module || process.argv[1]?.includes('usage-logger')) {
  program
    .command('view')
    .option('-t, --type <type>', 'Filter by type: tool, agent, action')
    .option('-l, --limit <number>', 'Limit number of entries', '100')
    .option('--json', 'Output as JSON')
    .action((opts) => {
      const logs = getLogs(opts.type as LogEntry['type'] | undefined, parseInt(opts.limit));
      if (opts.json) {
        console.log(JSON.stringify(logs, null, 2));
      } else {
        logs.forEach((log) => {
          console.log(`[${log.timestamp}] ${log.type}: ${log.name}`);
          if (log.error) console.log(`  Error: ${log.error}`);
          if (log.duration_ms) console.log(`  Duration: ${log.duration_ms}ms`);
        });
      }
    });

  program.command('clear').action(() => {
    clearLogs();
    console.log('Logs cleared');
  });

  program.parse(process.argv);
}