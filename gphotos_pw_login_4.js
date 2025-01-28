import { chromium } from "playwright-extra";
import stealth from "puppeteer-extra-plugin-stealth";

const stealthPlugin = stealth();
stealthPlugin.enabledEvasions.delete("iframe.contentWindow");
stealthPlugin.enabledEvasions.delete("media.codecs");
chromium.use(stealthPlugin);

const browser =  await chromium.launch({
    headless: false,
  });

// Use normally