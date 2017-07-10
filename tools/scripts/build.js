#!/usr/bin/env node

const fs = require('fs-extra');
const path = require('path');
const shell = require('shelljs');
const chalk = require('chalk');
const webpack = require("webpack");

const projectRoot = path.resolve(__dirname, '../../');
const staticFolder = path.join(projectRoot, 'conditional/static');
const webpackConfig = require(path.join(projectRoot, 'tools/config/webpack.prod.js'));

// Clean
try {
  fs.emptyDirSync(staticFolder);
} catch (err) {
  console.error(chalk.red('✘ Unable to clean static files directory:', err));
  shell.exit(1);
}

// Lint Python
if (shell.which('pylint')) {
  shell.cd(projectRoot);

  console.log(chalk.cyan('→ Linting Python source... (this may take a minute)'));
  const pylintResult = shell.exec('pylint conditional');

  if (pylintResult.code !== 0) {
    console.error(chalk.red('✘ Python source failed linter. Please correct the above issues and try again.'));
    shell.exit(1);
  }
} else {
  console.error(chalk.red('✘ Unable to find Pylint (is your virtualenv activated?)'));
  shell.exit(1);
}

// Webpack
console.log(chalk.cyan('→ Compiling frontend...'));
webpack(webpackConfig, (err, stats) => {
  console.log(stats.toString({
    chunks: false,
    colors: true,
  }));

  if (err || stats.hasErrors()) {
    console.error(chalk.red('✘ Failed to compile'));
    shell.exit(1);
  }

  // Copy Static Assets
  console.log(chalk.cyan('→ Copying static assets...'));
  fs.copySync(
    path.join(projectRoot, 'frontend/images'),
    path.join(staticFolder, 'images')
  );

  // Done!
  console.log(chalk.green('✔ Project built successfully'));
});
