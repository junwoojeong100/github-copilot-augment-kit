#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const sleep = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));
const allRoutes = [
  'dashboard',
  'operations',
  'simulator',
  'improvement',
  'finance',
  'devops',
  'agents',
  'governance'
];
const requiredIds = {
  dashboard: ['dashChart', 'dashFeed', 'dashTable'],
  operations: ['opsFlow', 'flowMover', 'reopt', 'opsTable'],
  simulator: ['simInputs', 'simGauge', 'simValue', 'simHistogram'],
  improvement: ['runAnalysis', 'analysisSteps', 'factorBars', 'improvementBoard'],
  finance: ['financeLevers', 'marginValue', 'valueDonut', 'financeTable'],
  devops: ['assignIssue', 'devSteps', 'codeDiff', 'issueTable', 'prStatus'],
  agents: ['agentList', 'chatTitle', 'chatLog', 'chips', 'chatInput', 'sendBtn', 'orchRun'],
  governance: ['evalRun', 'evalScore', 'evalTrace', 'controlTable', 'memoryTable']
};
const routes = (process.env.VERIFY_ROUTES || allRoutes.join(','))
  .split(',')
  .map(value => value.trim())
  .filter(Boolean);
const fullQa = process.env.FULL_QA !== '0';
const appHtml = path.resolve(process.env.APP_HTML || '');
const shotsDir = path.resolve(process.env.SHOTS_DIR || 'shots');

if (!process.env.APP_HTML || !fs.existsSync(appHtml)) {
  console.error('APP_HTML must point to a generated demo HTML file.');
  process.exit(2);
}
fs.mkdirSync(shotsDir, { recursive: true });

(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });

  const errors = [];
  const failures = [];
  const routeResults = {};
  let agentTitles = [];

  page.on('console', message => {
    if (message.type() === 'error') errors.push(`CONSOLE: ${message.text()}`);
  });
  page.on('pageerror', error => errors.push(`PAGEERROR: ${error.message}`));

  await page.goto(`file://${appHtml}`, { waitUntil: 'networkidle0' });

  for (const route of routes) {
    await page.evaluate(next => { location.hash = next; }, route);
    await sleep(800);
    routeResults[route] = await page.evaluate(expectedIds => {
      const rows = [...document.querySelectorAll(
        '.click-row, .agent-row, .node-card, .detail-card, .impact-card, .board-card, .governance-card, .sovereignty-step'
      )];
      const text = document.body.innerText;
      const agentList = document.getElementById('agentList');
      const view = document.getElementById('view');
      return {
        title: document.getElementById('topTitle')?.textContent || '',
        demoBadge: document.querySelector('.demo-badge')?.textContent || '',
        forbiddenText: /NaN|undefined|null%/.test(text),
        pageOverflow:
          document.documentElement.scrollWidth > window.innerWidth + 2
          || (view && view.scrollWidth > view.clientWidth + 2),
        unboundRows: rows
          .filter(row => typeof row.onclick !== 'function')
          .map(row => row.textContent.trim().slice(0, 60)),
        missingIds: expectedIds.filter(id => !document.getElementById(id)),
        agentRowsAllVisible: !agentList || agentList.scrollHeight <= agentList.clientHeight + 1
      };
    }, requiredIds[route] || []);

    const result = routeResults[route];
    if (!result.demoBadge.includes('DEMO DATA')) failures.push(`${route}: DEMO DATA badge missing`);
    if (result.forbiddenText) failures.push(`${route}: contains NaN/undefined/null%`);
    if (result.pageOverflow) failures.push(`${route}: horizontal page overflow`);
    if (result.unboundRows.length) failures.push(`${route}: unbound rows ${JSON.stringify(result.unboundRows)}`);
    if (result.missingIds.length) failures.push(`${route}: missing IDs ${JSON.stringify(result.missingIds)}`);
    if (!result.agentRowsAllVisible) failures.push(`${route}: not all agent rows are visible`);
    await page.screenshot({ path: path.join(shotsDir, `${route}.png`), fullPage: false });
  }

  if (fullQa) {
    await page.evaluate(() => { location.hash = 'operations'; });
    await sleep(650);
    const recommendationBefore = await page.$eval('#opsRecommendation', element => element.textContent);
    await page.click('#reopt');
    await sleep(1300);
    const recommendationAfter = await page.$eval('#opsRecommendation', element => element.textContent);
    if (recommendationBefore === recommendationAfter) failures.push('operations: reoptimization did not change recommendation');

    await page.evaluate(() => { location.hash = 'simulator'; });
    await sleep(650);
    const simulationBefore = await page.$eval('#simValue', element => element.textContent);
    await page.$eval('#simInputs input[type="range"]', element => {
      element.value = String(Number(element.max) - 1);
      element.dispatchEvent(new Event('input', { bubbles: true }));
    });
    const simulationAfter = await page.$eval('#simValue', element => element.textContent);
    if (simulationBefore === simulationAfter) failures.push('simulator: slider did not change output');

    await page.evaluate(() => { location.hash = 'improvement'; });
    await sleep(650);
    await page.click('#runAnalysis');
    await sleep(2200);
    const improvement = await page.evaluate(() => ({
      visibleSteps: document.querySelectorAll('#analysisSteps .step.visible').length,
      visibleBars: [...document.querySelectorAll('#factorBars .bar-fill')]
        .filter(bar => parseFloat(getComputedStyle(bar).width) > 0).length
    }));
    if (improvement.visibleSteps < 5 || improvement.visibleBars < 4) {
      failures.push(`improvement: incomplete animation ${JSON.stringify(improvement)}`);
    }

    await page.evaluate(() => { location.hash = 'finance'; });
    await sleep(650);
    const marginBefore = await page.$eval('#marginValue', element => element.textContent);
    await page.$eval('#financeLevers input[type="range"]', element => {
      element.value = String(Number(element.max) - 1);
      element.dispatchEvent(new Event('input', { bubbles: true }));
    });
    const marginAfter = await page.$eval('#marginValue', element => element.textContent);
    if (marginBefore === marginAfter) failures.push('finance: lever did not change margin');

    await page.evaluate(() => { location.hash = 'devops'; });
    await sleep(650);
    const secondIssue = await page.$('#issueTable tbody tr[data-index="1"]');
    if (secondIssue) await secondIssue.click();
    await page.click('#assignIssue');
    await sleep(2800);
    const prTitle = await page.$eval('#prTitle', element => element.textContent);
    if (/not created/i.test(prTitle)) failures.push('devops: assignment did not produce a result');

    await page.evaluate(() => { location.hash = 'agents'; });
    await sleep(700);
    agentTitles = await page.evaluate(() => {
      const titles = [];
      for (const row of document.querySelectorAll('#agentList .agent-row')) {
        row.click();
        titles.push(document.getElementById('chatTitle')?.textContent || '');
      }
      return titles;
    });
    if (agentTitles.length < 5 || new Set(agentTitles).size !== agentTitles.length) {
      failures.push(`agents: row switching failed ${JSON.stringify(agentTitles)}`);
    }
    await page.$eval('#chatInput', element => { element.value = '전환 중 응답 테스트'; });
    await page.click('#sendBtn');
    await page.click('#agentList .agent-row');
    await sleep(1150);
    const switchedChatCount = await page.$$eval('#chatLog .message', elements => elements.length);
    if (switchedChatCount !== 1) {
      failures.push(`agents: delayed response leaked across agent switch (${switchedChatCount} messages)`);
    }
    await page.$eval('#chatInput', element => { element.value = '자유 질문 테스트'; });
    await page.click('#sendBtn');
    await sleep(1150);
    const chatCount = await page.$$eval('#chatLog .message', elements => elements.length);
    if (chatCount < 3) failures.push(`agents: chat response missing (${chatCount} messages)`);
    await page.click('#orchRun');
    await sleep(4500);
    const orchestrationText = await page.$eval('#chatLog', element => element.textContent);
    if (!/decision package|의사결정 패키지/i.test(orchestrationText)) {
      failures.push('agents: orchestration summary missing');
    }

    await page.evaluate(() => { location.hash = 'governance'; });
    await sleep(650);
    const evaluationBefore = await page.$eval('#evalScore', element => element.textContent);
    await page.click('#evalRun');
    await sleep(2300);
    const evaluationAfter = await page.$eval('#evalScore', element => element.textContent);
    if (evaluationBefore === evaluationAfter) failures.push('governance: evaluation score did not change');

    for (let iteration = 0; iteration < 4; iteration++) {
      for (const route of allRoutes) {
        await page.evaluate(next => { location.hash = next; }, route);
        await sleep(80);
      }
    }
    await sleep(1300);
  }

  if (errors.length) failures.push(...errors);
  console.log(JSON.stringify({
    mode: fullQa ? 'FULL' : 'TARGETED',
    routes: routeResults,
    agentTitles,
    errors,
    failures
  }, null, 2));

  await browser.close();
  process.exitCode = failures.length ? 1 : 0;
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
