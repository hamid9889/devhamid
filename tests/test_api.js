/**
 * Comprehensive API Integration Test Suite
 * Tests all production routes:
 * - GET  /api/health
 * - GET  /api/analytics/visitor
 * - POST /api/analytics/visitor
 * - GET  /api/posts
 * - GET  /api/ai/health
 * - POST /api/ai/chat
 */

const http = require('http');

const PORT = process.env.PORT || 5000;
const BASE_URL = `http://localhost:${PORT}`;

function makeRequest(method, path, data = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const options = {
      method,
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => { body += chunk; });
      res.on('end', () => {
        try {
          const parsed = JSON.parse(body);
          resolve({ status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, raw: body });
        }
      });
    });

    req.on('error', (err) => reject(err));
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

async function runTests() {
  console.log('\n======================================================');
  console.log('🧪 Running DevHamid Portfolio Backend Integration Tests');
  console.log(`📡 Target Server: ${BASE_URL}`);
  console.log('======================================================\n');

  let passed = 0;
  let total = 0;

  async function test(name, fn) {
    total++;
    try {
      await fn();
      console.log(`✅ [PASS] ${name}`);
      passed++;
    } catch (err) {
      console.error(`❌ [FAIL] ${name}:`, err.message);
    }
  }

  // 1. Health check
  await test('GET /api/health returns 200 and healthy status', async () => {
    const res = await makeRequest('GET', '/api/health');
    if (res.status !== 200 || res.data?.status !== 'healthy') {
      throw new Error(`Unexpected response: status=${res.status}, body=${JSON.stringify(res.data)}`);
    }
  });

  // 2. Visitor count (GET)
  await test('GET /api/analytics/visitor returns visitor count >= 1482', async () => {
    const res = await makeRequest('GET', '/api/analytics/visitor');
    if (res.status !== 200 || typeof res.data?.count !== 'number' || res.data.count < 1482) {
      throw new Error(`Invalid visitor count: ${JSON.stringify(res.data)}`);
    }
  });

  // 3. Visitor count (POST)
  await test('POST /api/analytics/visitor records visit', async () => {
    const res = await makeRequest('POST', '/api/analytics/visitor', { visitorId: 'test-session-123' });
    if (res.status !== 200 || !res.data?.success) {
      throw new Error(`Failed to record visit: ${JSON.stringify(res.data)}`);
    }
  });

  // 4. Blog Posts
  await test('GET /api/posts returns array of blog posts', async () => {
    const res = await makeRequest('GET', '/api/posts');
    if (res.status !== 200 || !Array.isArray(res.data) || res.data.length === 0) {
      throw new Error(`Expected array of posts, got: ${JSON.stringify(res.data)}`);
    }
  });

  // 5. AI Modules Health
  await test('GET /api/ai/health returns operational modules status', async () => {
    const res = await makeRequest('GET', '/api/ai/health');
    if (res.status !== 200 || res.data?.status !== 'operational') {
      throw new Error(`AI health check failed: ${JSON.stringify(res.data)}`);
    }
  });

  // 6. AI Assistant Chat
  await test('POST /api/ai/chat returns contextual portfolio answer', async () => {
    const res = await makeRequest('POST', '/api/ai/chat', { prompt: 'What projects has Hamid built?', name: 'Recruiter' });
    if (res.status !== 200 || !res.data?.reply) {
      throw new Error(`AI chat failed: ${JSON.stringify(res.data)}`);
    }
  });

  // 7. Contact Endpoint Validation
  await test('POST /api/contact validates payload and rejects invalid inputs', async () => {
    const res = await makeRequest('POST', '/api/contact', { name: '', email: 'invalid', message: 'hi' });
    if (res.status !== 400 || res.data?.status !== 'error') {
      throw new Error(`Contact form validation failed: status=${res.status}`);
    }
  });

  console.log('\n------------------------------------------------------');
  console.log(`Summary: ${passed}/${total} tests passed!`);
  console.log('======================================================\n');

  if (passed === total) {
    process.exit(0);
  } else {
    process.exit(1);
  }
}

// Run test if invoked directly
if (require.main === module) {
  runTests().catch(err => {
    console.error('Test suite error (is the server running?):', err.message);
    process.exit(1);
  });
}

module.exports = { runTests };
