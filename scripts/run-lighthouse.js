#!/usr/bin/env node
const puppeteer = require('puppeteer');
const { navigation, desktopConfig } = require('lighthouse');
const fs = require('fs');
const path = require('path');

const TARGET = process.argv[2] || 'http://localhost:3000';
const PRESET = process.argv[3] || 'desktop';
const OUTPUT_NAME = process.argv[4] || 'lighthouse-report';
const AUDIT_SUBDIR = process.argv[5] || 'before';

const AUDIT_DIR = path.resolve(__dirname, '..', 'audit', AUDIT_SUBDIR);
if (!fs.existsSync(AUDIT_DIR)) {
  fs.mkdirSync(AUDIT_DIR, { recursive: true });
}

async function run() {
  console.log(`Launching Chromium via Puppeteer for ${TARGET} (${PRESET})...`);
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--disable-software-rasterizer',
      '--disable-extensions',
      '--disable-background-networking',
      '--disable-sync',
      '--disable-translate',
      '--hide-scrollbars',
      '--mute-audio',
      '--no-first-run'
    ]
  });
  console.log('Browser launched!');

  const port = (new URL(browser.wsEndpoint())).port;
  console.log('DevTools port:', port);

  const flags = {
    port,
    preset: PRESET,
    output: ['json', 'html'],
    logLevel: 'info',
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo']
  };

  const config = PRESET === 'desktop' ? desktopConfig : undefined;

  const result = await navigation(null, TARGET, { flags, config });

  const lhr = result.lhr;
  console.log(`\n=== RESULTS for ${TARGET} (${PRESET}) ===`);
  console.log('Performance:', Math.round(lhr.categories.performance.score * 100));
  console.log('Accessibility:', Math.round(lhr.categories.accessibility.score * 100));
  console.log('Best Practices:', Math.round(lhr.categories['best-practices'].score * 100));
  console.log('SEO:', Math.round(lhr.categories.seo.score * 100));

  // Save JSON report
  const jsonPath = path.join(AUDIT_DIR, `${OUTPUT_NAME}.json`);
  fs.writeFileSync(jsonPath, JSON.stringify(lhr, null, 2));
  console.log(`\nJSON report saved: ${jsonPath}`);

  // Generate and save HTML report
  const { generateReport } = require('lighthouse');
  const html = generateReport(lhr, 'html');
  const htmlPath = path.join(AUDIT_DIR, `${OUTPUT_NAME}.html`);
  fs.writeFileSync(htmlPath, html);
  console.log(`HTML report saved: ${htmlPath}`);

  await browser.close();
  console.log('Done!');
}

run().catch(err => {
  console.error('Error:', err.message);
  console.error(err.stack);
  process.exit(1);
});