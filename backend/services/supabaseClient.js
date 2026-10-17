/**
 * Supabase Client Service (Node.js)
 * Connects to Supabase Cloud Database using @supabase/supabase-js.
 * Provides fallback in-memory store if credentials are not configured yet,
 * guaranteeing zero downtime and seamless local development.
 */

const { createClient } = (() => {
  try {
    return require('@supabase/supabase-js');
  } catch (e) {
    return { createClient: null };
  }
})();

const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_KEY || process.env.SUPABASE_ANON_KEY;

let supabase = null;
let isConfigured = false;

if (createClient && SUPABASE_URL && SUPABASE_KEY && !SUPABASE_URL.includes('your-supabase-project')) {
  try {
    supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
      auth: { persistSession: false }
    });
    isConfigured = true;
    console.log('✅ Supabase Client initialized successfully.');
  } catch (err) {
    console.warn('⚠️ Error initializing Supabase client:', err.message);
    supabase = null;
    isConfigured = false;
  }
} else {
  console.log('ℹ️ Supabase credentials not set or incomplete. Running in-memory mock store.');
}

/**
 * In-memory fallback database for local testing when Supabase is not yet connected
 */
const inMemoryStore = {
  baselineCount: 1482,
  visits: 1482,
  lastVisitAt: new Date().toISOString(),
  sessions: new Map(),
  messages: []
};

/**
 * Check if live Supabase instance is active
 */
function isSupabaseConnected() {
  return isConfigured && supabase !== null;
}

module.exports = {
  supabase,
  isSupabaseConnected,
  inMemoryStore
};
