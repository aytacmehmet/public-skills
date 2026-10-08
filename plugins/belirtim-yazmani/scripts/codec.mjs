import { encode, decode } from '../vendor/toon/index.mjs';
import { readFileSync } from 'node:fs';
const encodeValue = value => encode(value, {indentSize:2,delimiter:','}) + '\n';
const decodeText = text => decode(text, {strict:true,indentSize:2});
try {
  const input = readFileSync(0, 'utf8');
  const mode = process.argv[2];
  if (mode === 'encode') process.stdout.write(encodeValue(JSON.parse(input)));
  else if (mode === 'decode') process.stdout.write(JSON.stringify(decodeText(input)));
  else if (mode === 'batch-encode') process.stdout.write(JSON.stringify(Object.fromEntries(
    Object.entries(JSON.parse(input)).map(([key, value]) => {
      const text = encodeValue(value);
      return [key, {text, decoded: decodeText(text)}];
    }))));
  else if (mode === 'batch-decode') process.stdout.write(JSON.stringify(Object.fromEntries(
    Object.entries(JSON.parse(input)).map(([key, text]) => [key, decodeText(text)]))));
  else throw new Error('Use encode or decode');
} catch (e) { process.stderr.write(String(e.message)+'\n'); process.exitCode=1; }
