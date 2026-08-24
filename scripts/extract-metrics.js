const fs = require('fs');
const path = require('path');

const dirs = ['before', 'after'];
const files = ['website-home-desktop', 'website-home-mobile', 'backoffice-dashboard-desktop', 'backoffice-dashboard-mobile'];

const metricsOfInterest = ['largest-contentful-paint', 'total-blocking-time', 'cumulative-layout-shift', 'interactive', 'speed-index', 'first-contentful-paint', 'server-response-time', 'max-potential-fid', 'render-blocking-resources', 'unused-javascript', 'unused-css-rules', 'mainthread-work-breakdown', 'bootup-time', 'network-requests', 'dom-size', 'font-display', 'offscreen-images', 'uses-optimized-images', 'uses-text-compression', 'uses-rel-preconnect', 'uses-http2', 'uses-long-cache-ttl', 'duplicated-javascript', 'legacy-javascript'];

async function extract() {
  for (const f of files) {
    console.log(`\n=== ${f} ===`);
    for (const dir of dirs) {
      const p = path.join('audit', dir, `${f}.json`);
      if (!fs.existsSync(p)) { console.log(`  ${dir}: FILE NOT FOUND`); continue; }
      const lhr = JSON.parse(fs.readFileSync(p, 'utf8'));
      const perf = Math.round(lhr.categories.performance.score * 100);
      console.log(`  [${dir}] Performance: ${perf}`);
      for (const m of metricsOfInterest) {
        const audit = lhr.audits[m];
        if (audit) {
          const display = audit.displayValue || '';
          const score = audit.score !== null ? Math.round(audit.score*100) : 'N/A';
          if (display) console.log(`    ${m}: ${display} (score ${score})`);
        }
      }
    }
  }
}
extract();