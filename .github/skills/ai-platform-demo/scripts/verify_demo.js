#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
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
const fullQa = process.env.FULL_QA !== '0';
const requestedRoutes = (process.env.VERIFY_ROUTES || allRoutes.join(','))
  .split(',')
  .map(value => value.trim())
  .filter(Boolean);
const invalidRoutes = requestedRoutes.filter(route => !allRoutes.includes(route));
if (!fullQa && invalidRoutes.length) {
  console.error(`VERIFY_ROUTES contains unsupported route(s): ${invalidRoutes.join(', ')}`);
  process.exit(2);
}
if (!fullQa && !requestedRoutes.length) {
  console.error('VERIFY_ROUTES must include at least one supported route in targeted mode.');
  process.exit(2);
}
const routes = fullQa ? allRoutes : requestedRoutes;
const appHtmlInput = path.resolve(process.env.APP_HTML || '');
const shotsDir = path.resolve(process.env.SHOTS_DIR || '');

if (!process.env.APP_HTML || !fs.existsSync(appHtmlInput)) {
  console.error('APP_HTML must point to a generated demo HTML file.');
  process.exit(2);
}
if (!process.env.SHOTS_DIR) {
  console.error('SHOTS_DIR must point to the session-isolated screenshot directory.');
  process.exit(2);
}
const appHtml = fs.realpathSync(appHtmlInput);
const appWorkDir = path.dirname(appHtml);
const shotsRelative = path.relative(appWorkDir, shotsDir);
if (!shotsRelative || shotsRelative.startsWith(`..${path.sep}`) || path.isAbsolute(shotsRelative)) {
  console.error('SHOTS_DIR must be a child of the APP_HTML work directory.');
  process.exit(2);
}
const shotsParent = path.dirname(shotsDir);
if (!fs.existsSync(shotsParent)) {
  console.error('SHOTS_DIR parent must already exist inside the APP_HTML work directory.');
  process.exit(2);
}
const realShotsParent = fs.realpathSync(shotsParent);
const parentRelative = path.relative(appWorkDir, realShotsParent);
if (parentRelative.startsWith(`..${path.sep}`) || path.isAbsolute(parentRelative)) {
  console.error('SHOTS_DIR parent resolves outside the APP_HTML work directory.');
  process.exit(2);
}
fs.mkdirSync(shotsDir, { recursive: true });
const realShotsDir = fs.realpathSync(shotsDir);
const realShotsRelative = path.relative(appWorkDir, realShotsDir);
if (!realShotsRelative || realShotsRelative.startsWith(`..${path.sep}`) || path.isAbsolute(realShotsRelative)) {
  console.error('SHOTS_DIR must be a child of the APP_HTML work directory.');
  process.exit(2);
}
const allowedScreenshotNames = new Set(allRoutes.map(route => `${route}.png`));
for (const entry of fs.readdirSync(realShotsDir)) {
  if (!allowedScreenshotNames.has(entry)) {
    console.error(`SHOTS_DIR contains an unexpected entry: ${entry}`);
    process.exit(2);
  }
  const destination = path.join(realShotsDir, entry);
  const linkStat = fs.lstatSync(destination);
  const fileStat = fs.statSync(destination);
  if (linkStat.isSymbolicLink() || !fileStat.isFile() || fileStat.nlink !== 1) {
    console.error(`Refusing unsafe screenshot destination: ${entry}`);
    process.exit(2);
  }
  fs.unlinkSync(destination);
}

let browser;
(async () => {
  const launchArgs = ['--disable-gpu'];
  if (process.env.PUPPETEER_NO_SANDBOX === '1') {
    launchArgs.push('--no-sandbox', '--disable-setuid-sandbox');
  }
  browser = await puppeteer.launch({
    headless: true,
    args: launchArgs,
    protocolTimeout: 60000
  });
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

  await page.goto(pathToFileURL(appHtml).href, { waitUntil: 'networkidle0' });
  const qaSpec = await page.evaluate(() => JSON.parse(document.getElementById('demo-spec').textContent));
  const waitForEnabled = async (selector, timeout) => {
    await page.waitForFunction(target => {
      const button = document.querySelector(target);
      return button && !button.disabled;
    }, { timeout }, selector);
  };

  for (const route of routes) {
    await page.evaluate(next => { location.hash = next; }, route);
    await sleep(800);
    const settleTimeout = route === 'improvement' && qaSpec.improvement.action.autoRun
      ? qaSpec.improvement.action.durationMs + 2000
      : 5000;
    await page.waitForFunction(() => (
      ![...document.querySelectorAll('button:disabled')].some(button => button.offsetParent !== null)
    ), { timeout: settleTimeout }).catch(() => {
      failures.push(`${route}: interaction did not settle before screenshot`);
    });
    await page.evaluate(() => {
      document.querySelectorAll('#toasts .toast').forEach(toast => toast.remove());
    });
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
    await waitForEnabled('#reopt', qaSpec.operations.action.durationMs + 2000);
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
    await waitForEnabled('#runAnalysis', qaSpec.improvement.action.durationMs + 2000);
    await sleep(150 + qaSpec.improvement.factors.length * 100);
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
    const issueIndexes = await page.evaluate(() => {
      const data = JSON.parse(document.getElementById('demo-spec').textContent).devops;
      return {
        autonomous: data.issues.findIndex(issue => !issue.highRisk),
        highRisk: data.issues.findIndex(issue => issue.highRisk)
      };
    });
    if (issueIndexes.autonomous < 0) failures.push('devops: no autonomous issue configured');
    if (issueIndexes.highRisk < 0) failures.push('devops: no high-risk issue configured');
    if (issueIndexes.autonomous >= 0) {
      await page.click(`#issueTable tbody tr[data-index="${issueIndexes.autonomous}"]`);
      await page.click('#assignIssue');
      await waitForEnabled('#assignIssue', qaSpec.devops.action.durationMs + 2000);
      const autonomous = await page.evaluate(index => {
        const data = JSON.parse(document.getElementById('demo-spec').textContent).devops;
        const issue = data.issues[index];
        return {
          actual: {
            title: document.getElementById('prTitle').textContent,
            gate: document.getElementById('prGate').textContent,
            result: document.getElementById('prSub').textContent,
            status: document.getElementById('prStatus').textContent
          },
          expected: {
            title: data.action.prReady
              .replace('{{number}}', String(data.action.prBase + index))
              .replace('{{title}}', issue.title),
            gate: data.action.checksPassed,
            result: data.action.prResult,
            status: data.action.prStatus
          }
        };
      }, issueIndexes.autonomous);
      if (JSON.stringify(autonomous.actual) !== JSON.stringify(autonomous.expected)) {
        failures.push(`devops: autonomous result mismatch ${JSON.stringify(autonomous)}`);
      }
    }
    if (issueIndexes.highRisk >= 0) {
      await page.click(`#issueTable tbody tr[data-index="${issueIndexes.highRisk}"]`);
      await page.click('#assignIssue');
      await waitForEnabled('#assignIssue', qaSpec.devops.action.durationMs + 2000);
      const highRisk = await page.evaluate(index => {
        const data = JSON.parse(document.getElementById('demo-spec').textContent).devops;
        const issue = data.issues[index];
        return {
          actual: {
            title: document.getElementById('prTitle').textContent,
            gate: document.getElementById('prGate').textContent,
            result: document.getElementById('prSub').textContent,
            status: document.getElementById('prStatus').textContent
          },
          expected: {
            title: data.action.planReady.replace('{{issue}}', issue.id),
            gate: data.action.humanImplementation,
            result: data.action.humanResult,
            status: data.action.planStatus
          }
        };
      }, issueIndexes.highRisk);
      if (JSON.stringify(highRisk.actual) !== JSON.stringify(highRisk.expected)) {
        failures.push(`devops: high-risk result mismatch ${JSON.stringify(highRisk)}`);
      }
    }

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
    await page.$eval('#sendBtn', button => button.click());
    await page.click('#agentList .agent-row');
    await sleep(1150);
    const switchedChatCount = await page.$$eval('#chatLog .message', elements => elements.length);
    if (switchedChatCount !== 1) {
      failures.push(`agents: delayed response leaked across agent switch (${switchedChatCount} messages)`);
    }
    await page.$eval('#chatInput', element => { element.value = '자유 질문 테스트'; });
    await page.$eval('#sendBtn', button => button.click());
    await page.waitForFunction(
      () => (
        document.querySelectorAll('#chatLog .message').length >= 3
        && !document.querySelector('#chatLog .message.typing')
      ),
      { timeout: 3000 }
    ).catch(() => {});
    const chatCount = await page.$$eval('#chatLog .message', elements => elements.length);
    if (chatCount < 3) failures.push(`agents: chat response missing (${chatCount} messages)`);
    await page.click('#orchRun');
    await waitForEnabled(
      '#orchRun',
      800 + qaSpec.agents.orchestration.stages.length * 520 + 2000
    );
    const orchestrationText = await page.$eval('#chatLog', element => element.textContent);
    if (!/decision package|의사결정 패키지/i.test(orchestrationText)) {
      failures.push('agents: orchestration summary missing');
    }

    await page.evaluate(() => { location.hash = 'governance'; });
    await sleep(650);
    const evaluationBefore = await page.$eval('#evalScore', element => element.textContent);
    await page.click('#evalRun');
    await waitForEnabled(
      '#evalRun',
      qaSpec.governance.evaluation.runLines.length * 250 + 2200
    );
    const evaluationAfter = await page.$eval('#evalScore', element => element.textContent);
    const evaluationBeforeNumber = Number(evaluationBefore);
    const evaluationAfterNumber = Number(evaluationAfter);
    if (
      !Number.isFinite(evaluationBeforeNumber)
      || !Number.isFinite(evaluationAfterNumber)
      || evaluationBeforeNumber === evaluationAfterNumber
    ) {
      failures.push('governance: evaluation score did not change numerically');
    }

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
})().catch(async error => {
  if (browser) await browser.close().catch(() => {});
  console.error(error);
  process.exitCode = 1;
});
