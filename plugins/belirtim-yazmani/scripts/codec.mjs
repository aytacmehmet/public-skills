import { encode, decode } from '../vendor/toon/index.mjs';
import { readFileSync } from 'node:fs';
try {
  const input = readFileSync(0, 'utf8');
  const mode = process.argv[2];
  if (mode === 'encode') process.stdout.write(encode(JSON.parse(input), {indentSize:2,delimiter:','}) + '\n');
  else if (mode === 'decode') process.stdout.write(JSON.stringify(decode(input, {strict:true,indentSize:2})));
  else throw new Error('Use encode or decode');
} catch (e) { process.stderr.write(String(e.message)+'\n'); process.exitCode=1; }
