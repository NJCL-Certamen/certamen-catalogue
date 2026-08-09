// This is an imperfect script that I'm using on markdown files that are generated from older pdfs. The documents on both ends still require a lot of doctoring.
const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2)

if (args.length < 2) {
  console.error("Usage: node md-parse.js <year> <filepath>");
  process.exit(1);
}

const processQ = q => {
  let joiner = "?";
  let parts = q.split(/\?\"*/g);
  if (parts.length === 1) {
    parts = q.split(/\.\\"*/g);
    joiner = ".";

    if (parts.length === 1) {
      parts.push(""); // just give up
    }

    if (parts[parts.length - 1].trim() === "" && parts.length > 1) {
      parts = parts.slice(0, parts.length - 1);
    }
  }

  const answer = parts.pop().trim();
  return {
    question: parts.join(joiner).trim() + joiner,
    answer
  }
}

const year = args[0];
const filepath = args[1];

let content;
try {
  content = fs.readFileSync(filepath, "utf-8");
} catch (error) {
  console.error(`Error reading file: ${error.message}`);
  process.exit(1);
}

let closeQuote = false;
let startIdx = content.indexOf("\"");
while (startIdx !== -1) {
  content = content.substring(0, startIdx) + (closeQuote ? "”" : "“") + content.substring(startIdx + 1);
  closeQuote = !closeQuote;
  startIdx = content.indexOf("\"", startIdx);
}

const rounds = content.split('# ');
rounds.forEach(round => {
  const trimmedRound = round.trim();
  const roundName = trimmedRound.substring(0, trimmedRound.indexOf("\n"))
  let yaml = `tournament: ""\nyear: ${year}\ndivision: ""\nround: ${roundName}\nquestions:\n`;

  const questions = trimmedRound.split(/[\dIVX]+(\.|:)/g).slice(1); // leaves out title part
  questions.forEach(q => {
    const lines = q.split("\n").filter(line => line.trim() !== "");
    const qs = [];
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].endsWith("?") || lines[i].endsWith("?\"")) {
        qs.push(lines[i] + " " + lines[++i]);
      } else {
        qs.push(lines[i]);
      }
    }

    qs.forEach((x, idx) => {
      const { question, answer } = processQ(x);
      if (idx === 0) {
        yaml += `\n  - tossup:\n      question: "${question}"\n      answer: "${answer}"`
      } else {
        if (idx === 1) {
          yaml += `\n    boni:`
        }

        yaml += `\n      - question: "${question}"\n        answer: "${answer}"`;
      }
    })
  });

  fs.writeFileSync(`temp/${year}${roundName}.yaml`, yaml, 'utf8', err => {
    console.error(`Error writing file for ${roundName}`, err)
  });
});

process.exit(0);
