const fs = require('fs');
const path = require('path');

// Target files
const preloadPath = path.join(__dirname, '..', '..', 'electron', 'preload.ts');
const mainTsPath = path.join(__dirname, '..', '..', 'electron', 'main.ts');
const apiPath = path.join(__dirname, '..', '..', 'src', 'services', 'api.ts');
const mainPyPath = path.join(__dirname, '..', 'main.py');

console.log('Running BlastScope IPC Alignment Integration Check...\n');

// 1. Parse validChannels from preload.ts
function parsePreloadChannels() {
  const content = fs.readFileSync(preloadPath, 'utf8');
  const match = content.match(/const\s+validChannels\s*=\s*\[([\s\S]*?)\];/);
  if (!match) throw new Error('Could not find validChannels array in preload.ts');
  
  return match[1]
    .split(',')
    .map(s => s.trim().replace(/['"]/g, ''))
    .filter(s => s.length > 0);
}

// 2. Parse channels from main.ts
function parseMainChannels() {
  const content = fs.readFileSync(mainTsPath, 'utf8');
  const match = content.match(/const\s+channels\s*=\s*\[([\s\S]*?)\];/);
  if (!match) throw new Error('Could not find channels array in main.ts');
  
  return match[1]
    .split(',')
    .map(s => s.trim().replace(/['"]/g, ''))
    .filter(s => s.length > 0);
}

// 3. Parse invoke calls from api.ts
function parseApiInvokeCalls() {
  const content = fs.readFileSync(apiPath, 'utf8');
  // Match window.api!.invoke('channel') or window.api!.invoke("channel")
  const matches = [...content.matchAll(/window\.api!\.invoke\(\s*['"](.*?)['"]/g)];
  return [...new Set(matches.map(m => m[1]))];
}

// 4. Parse routed channels from main.py
function parsePythonRoutes() {
  const content = fs.readFileSync(mainPyPath, 'utf8');
  // Match elif channel == "channel" or elif channel == 'channel'
  const matches = [...content.matchAll(/channel\s*==\s*['"](.*?)['"]/g)];
  return [...new Set(matches.map(m => m[1]))];
}

try {
  const preloadChannels = parsePreloadChannels();
  const mainChannels = parseMainChannels();
  const apiInvokes = parseApiInvokeCalls();
  const pythonRoutes = parsePythonRoutes();

  // Create unified channel list
  const allChannels = [...new Set([...preloadChannels, ...mainChannels, ...apiInvokes, ...pythonRoutes])].sort();

  console.log('----------------------------------------------------------------------------------------');
  console.log(String('Channel').padEnd(35) + ' | ' + 'Frontend (api.ts)' + ' | ' + 'Preload Whitelist' + ' | ' + 'Main Routing' + ' | ' + 'Python Backend');
  console.log('----------------------------------------------------------------------------------------');

  let discrepancies = 0;

  const nodeOnlyChannels = ['database:export', 'database:import'];

  for (const chan of allChannels) {
    const inApi = apiInvokes.includes(chan);
    const inPreload = preloadChannels.includes(chan);
    const inMain = mainChannels.includes(chan);
    const inPython = pythonRoutes.includes(chan);
    const isNodeOnly = nodeOnlyChannels.includes(chan);

    const apiStr = inApi ? '✅ YES'.padEnd(17) : '❌ NO'.padEnd(17);
    const preloadStr = inPreload ? '✅ YES'.padEnd(17) : '❌ NO'.padEnd(17);
    const mainStr = inMain ? '✅ YES'.padEnd(12) : '❌ NO'.padEnd(12);
    const pythonStr = isNodeOnly ? 'N/A (NODE)' : (inPython ? '✅ YES' : '❌ NO');

    const statusMark = (inApi && inPreload && inMain && (inPython || isNodeOnly)) ? '' : ' ⚠️ ';
    if (statusMark) discrepancies++;

    console.log(`${statusMark}${chan.padEnd(32)} | ${apiStr} | ${preloadStr} | ${mainStr} | ${pythonStr}`);
  }
  console.log('----------------------------------------------------------------------------------------\n');

  // Assertions
  let failed = false;
  
  // A. Check if preload and main whitelists are identical
  const preloadExtra = preloadChannels.filter(c => !mainChannels.includes(c));
  const mainExtra = mainChannels.filter(c => !preloadChannels.includes(c));
  if (preloadExtra.length > 0 || mainExtra.length > 0) {
    console.error('❌ ERROR: Preload whitelist and Main process router whitelists are not aligned!');
    if (preloadExtra.length > 0) console.error(`  - In preload but missing from main.ts: ${preloadExtra.join(', ')}`);
    if (mainExtra.length > 0) console.error(`  - In main.ts but missing from preload: ${mainExtra.join(', ')}`);
    failed = true;
  }

  // B. Check if all frontend invokes are in preload whitelist
  const unwhitelistedInvokes = apiInvokes.filter(c => !preloadChannels.includes(c));
  if (unwhitelistedInvokes.length > 0) {
    console.error(`❌ ERROR: Frontend is calling channels not whitelisted in preload.ts: ${unwhitelistedInvokes.join(', ')}`);
    failed = true;
  }

  // C. Check if all whitelisted channels exist in backend main.py
  const unroutedChannels = preloadChannels
    .filter(c => !nodeOnlyChannels.includes(c))
    .filter(c => !pythonRoutes.includes(c));
  if (unroutedChannels.length > 0) {
    console.error(`❌ ERROR: Whitelisted channels are not routed in backend main.py: ${unroutedChannels.join(', ')}`);
    failed = true;
  }

  // D. Check for dead/unreachable backend routes (in python but never called by api.ts)
  const deadPythonRoutes = pythonRoutes.filter(c => !apiInvokes.includes(c));
  if (deadPythonRoutes.length > 0) {
    console.log(`💡 NOTE: Found dead/unreachable python backend routes (not called by frontend): ${deadPythonRoutes.join(', ')}`);
  }

  if (failed || discrepancies > 0) {
    if (failed) {
      console.error(`\nTest FAILED: Found ${discrepancies} alignment discrepancy/ies.`);
      process.exit(1);
    } else {
      console.log(`\nAlignment check complete. Found warnings but no critical blocks.`);
      process.exit(0);
    }
  } else {
    console.log('\n✅ SUCCESS: All IPC channels are 100% aligned across the entire application stack!');
    process.exit(0);
  }

} catch (err) {
  console.error('IPC check script execution error:', err.message);
  process.exit(1);
}
