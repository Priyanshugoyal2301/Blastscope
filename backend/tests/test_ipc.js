const { spawn } = require('child_process');
const path = require('path');
const readline = require('readline');

const backendPath = path.join(__dirname, '..', 'main.py');
console.log(`Starting IPC flood test against: ${backendPath}`);

// Spawn python subprocess
const pythonProcess = spawn('python', [backendPath], {
  env: { ...process.env, PYTHONPATH: path.join(__dirname, '..', '..') }
});

const rl = readline.createInterface({
  input: pythonProcess.stdout,
  terminal: false
});

let testCount = 50;
let sentCount = 0;
let receivedCount = 0;
let startTimes = new Map();
let latencies = [];
let deadlocked = false;

// Set a timeout to catch deadlocks
const watchdog = setTimeout(() => {
  if (receivedCount < testCount) {
    console.error(`\nCRITICAL: Deadlock detected! Received only ${receivedCount}/${testCount} responses.`);
    deadlocked = true;
    pythonProcess.kill();
    process.exit(1);
  }
}, 5000);

rl.on('line', (line) => {
  const timeReceived = Date.now();
  try {
    const response = JSON.parse(line.trim());
    const id = response.id;
    
    if (id && startTimes.has(id)) {
      const timeSent = startTimes.get(id);
      const latency = timeReceived - timeSent;
      latencies.push(latency);
      receivedCount++;
      
      if (receivedCount % 10 === 0 || receivedCount === testCount) {
        console.log(`Received response ${receivedCount}/${testCount} (Latency: ${latency}ms)`);
      }

      if (receivedCount === testCount) {
        clearTimeout(watchdog);
        finishTest();
      }
    }
  } catch (e) {
    console.error('Error parsing line:', line, e.message);
  }
});

pythonProcess.stderr.on('data', (data) => {
  const msg = data.toString().trim();
  if (msg.includes('BLASTSCOPE_PYTHON_BACKEND_READY')) {
    console.log('Python backend is ready. Initiating flood...');
    sendBatch();
  }
});

function sendBatch() {
  for (let i = 1; i <= testCount; i++) {
    const id = `req_flood_${i}`;
    startTimes.set(id, Date.now());
    
    // Save scenario call payload
    const payload = {
      id: 100 + i,
      name: `Flood Test Scenario ${i}`,
      explosiveId: 1, // TNT
      chargeWeight: 100 + i * 2,
      distance: 10 + i,
      burstType: 'Surface',
      unitSystem: 'Metric'
    };
    
    const requestMessage = JSON.stringify({
      id: id,
      channel: 'scenarios:save',
      payload: payload
    }) + '\n';
    
    pythonProcess.stdin.write(requestMessage);
    sentCount++;
  }
  console.log(`Dispatched ${sentCount} scenario save requests to stdin concurrently.`);
}

function finishTest() {
  const sum = latencies.reduce((a, b) => a + b, 0);
  const avg = sum / latencies.length;
  const max = Math.max(...latencies);
  const min = Math.min(...latencies);
  
  console.log('\n================ IPC Test Results ================');
  console.log(`Total Requests Dispatched: ${sentCount}`);
  console.log(`Total Responses Received:   ${receivedCount}`);
  console.log(`Lost Messages / Dropouts:   ${sentCount - receivedCount}`);
  console.log(`Minimum Latency:            ${min}ms`);
  console.log(`Maximum Latency:            ${max}ms`);
  console.log(`Average Latency:            ${avg.toFixed(2)}ms`);
  console.log('==================================================');
  
  pythonProcess.kill();
  process.exit(0);
}
