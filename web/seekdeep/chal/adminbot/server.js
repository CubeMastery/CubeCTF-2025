const express = require('express');
const puppeteer = require('puppeteer');
const crypto = require('crypto');

const FLAG = process.env.FLAG || 'flag{testflag}';
const BASE_URL = process.env.BASE_URL || 'http://seekdeep:3000';
const PORT = 1337;

const app = express();
app.use(express.json());
app.use(express.static('public'));

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Admin bot server listening on port ${PORT}`);
});

function getRandomString() {
  return crypto.randomBytes(12).toString('hex');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function visitWithAdminBot(targetUrl, followUser) {
  const randomUsername = getRandomString();
  const randomPassword = getRandomString();

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  try {
    console.log("[+] Registering new admin user...");

    await page.goto(`${BASE_URL}/register`, { waitUntil: 'networkidle2' });
    await page.waitForSelector('form');

    await page.type('input[name="username"]', randomUsername);
    await page.type('input[name="password"]', randomPassword);
    await page.type('input[name="head_size"]', '57.5');
    await page.click('input[name="is_bald"]');
    await page.type('input[name="eyesight"]', '20/20');
    await page.type('input[name="largest_count"]', '1000000');
    await page.type('input[name="favorite_vegetable"]', 'Carrot');
    await page.type('input[name="cosmic_color"]', 'Blue');
    await page.type('input[name="left_shoes"]', '1');
    await page.type('input[name="mythical_creature"]', 'Dragon');

    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation({ waitUntil: 'networkidle2' })
    ]);

    console.log("[+] Logging in...");

    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle2' });
    await page.waitForSelector('form');
    await page.type('input[name="username"]', randomUsername);
    await page.type('input[name="password"]', randomPassword);
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation({ waitUntil: 'networkidle2' })
    ]);

    console.log("[+] Setting FLAG cookie...");

    await page.setCookie({
      name: 'flag',
      value: FLAG,
      httpOnly: true,
    });

    console.log(`[+] Following user "${followUser}"...`);
    await page.goto(`${BASE_URL}/social`, { waitUntil: 'networkidle2' });
    await page.type('input[name="follower_username"]', followUser);
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation({ waitUntil: 'networkidle2' })
    ]);

    const prophecyPages = ['/ascend', '/lucky', '/spirit', '/colors', '/riddle'];
    console.log("[+] Visiting prophecy pages...");
    for (const path of prophecyPages) {
      console.log(`    -> ${BASE_URL}${path}`);
      await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle2' });
    }

    console.log(`[+] Visiting target URL: ${targetUrl}`);
    await page.goto(targetUrl, { waitUntil: 'networkidle2' });

    await sleep(3000);

    console.log("[+] Done. Admin bot visited target URL!");
  } catch (err) {
    console.error("[-] An error occurred in the admin bot:", err);
  } finally {
    await browser.close();
  }
}

app.post('/visit', (req, res) => {
  const { url, user } = req.body || {};

  if (!url || !user) {
    return res.status(400).send('Missing url or user in request body');
  }

  res.send('Ok, admin bot triggered.');

  visitWithAdminBot(url, user)
    .catch(err => console.error("[-] Admin visit error:", err));
});

app.get('/', (req, res) => {
  res.send('Admin Bot is running.');
});