// node render_alpha.js in.svg out.png width height: one SVG to a PNG with a see-through background.
const { chromium } = require('playwright');
(async () => {
  const [inp, out, w, h] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto('file://' + inp);
  await page.screenshot({ path: out, omitBackground: true });
  await browser.close();
})();
