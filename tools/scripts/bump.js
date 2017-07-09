#!/usr/bin/env node

const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');
const semver = require('semver');
const releaseConfig = require('../../.release.json');

const argv = require('yargs')
  .usage(`${chalk.magenta('bump.js')} [args]`)
  .option('increment', {
    type: 'string',
    alias: 'i',
    describe: 'Increment "major", "minor", "patch", or "pre*" version',
    choices: ['major', 'minor', 'patch', 'prerelease'],
    default: 'patch',
  })
  .help()
  .argv;

const bump = (contents, type) => new Promise((resolve, reject) => {
  const regex = new RegExp(
    '([<|\'|\"]?[>|\'|\"]?[ ]*[:=]?[ ]*[\'|\"]?[a-z]?)(\\d+\\.\\d+\\.\\d+)' +
    '(-[0-9A-Za-z\.-]+)?([\'|\"|<]?)');

  let previousVersion, newVersion;
  const result = String(contents).replace(regex, (match, prefix, parsed, prerelease, suffix) => {
    parsed = parsed + (prerelease || '');

    if (!semver.valid(parsed) && !opts.version) {
      reject(`Invalid semver ${parsed}`);
    }

    const version = semver.inc(parsed, type);
    previousVersion = parsed;
    newVersion = version;

    return prefix + version + (suffix || '');
  });

  resolve({ previousVersion, newVersion, result });
});

if (releaseConfig.bump) {
  releaseConfig.bump.forEach((fileToBump) => {
    const filePath = path.join(__dirname, '../..', fileToBump);

    fs.readFile(filePath)
      .then((contents) => bump(contents, argv.increment))
      .then(({ previousVersion, newVersion, result }) => {
        return fs.writeFile(filePath, result)
          .then(() => {
            console.log(`${chalk.green(`✔ Bumped ${fileToBump}:`)} ${chalk.cyan(previousVersion)} → ${chalk.magenta(newVersion)} (${chalk.cyan(argv.increment)})`);
          })
      })
      .catch((err) => {
        console.error(chalk.red(`✘ Failed to bump ${fileToBump}:`), err);
      });
  });
} else {
  console.log('Nothing to do. Configure files to bump in your .release.json');
}
