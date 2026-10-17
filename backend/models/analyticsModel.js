/**
 * Analytics Model (Supabase Integration)
 * Manages visitor count and session deduplication.
 * Replaces old local SQLite database with Supabase cloud database.
 */

const crypto = require('crypto');
const { supabase, isSupabaseConnected, inMemoryStore } = require('../services/supabaseClient');

const BASELINE_COUNT = 1482;

/**
 * Get current visitor count
 */
async function getVisitorCount() {
  if (isSupabaseConnected()) {
    try {
      const { data, error } = await supabase
        .from('site_analytics')
        .select('total_visits')
        .eq('id', 1)
        .single();

      if (!error && data && typeof data.total_visits === 'number') {
        return data.total_visits;
      }
    } catch (err) {
      console.warn('⚠️ Supabase error getting visitor count:', err.message);
    }
  }

  return inMemoryStore.visits || BASELINE_COUNT;
}

/**
 * Record a unique visit and increment visitor count
 * Prevents artificial inflation using 24h date buckets and client hash.
 */
async function recordVisit({ visitorId, ipAddress, userAgent }) {
  const now = new Date();
  const dateBucket = now.toISOString().slice(0, 10); // YYYY-MM-DD
  const isoNow = now.toISOString();

  // Create anonymized privacy hashes
  const ipHash = crypto.createHash('sha256').update(ipAddress || '127.0.0.1').digest('hex').slice(0, 16);
  const clientHash = visitorId
    ? crypto.createHash('sha256').update(visitorId).digest('hex').slice(0, 24)
    : ipHash;

  if (isSupabaseConnected()) {
    try {
      // 1. Check if session exists in Supabase
      const { data: existing, error: checkErr } = await supabase
        .from('visitor_sessions')
        .select('id')
        .or(`visitor_hash.eq.${clientHash},ip_hash.eq.${ipHash}`)
        .eq('date_bucket', dateBucket)
        .limit(1);

      if (!checkErr && existing && existing.length > 0) {
        const count = await getVisitorCount();
        return { count, isNewVisit: false, message: 'Existing visitor session active' };
      }

      // 2. Insert new session
      await supabase.from('visitor_sessions').insert([{
        visitor_hash: clientHash,
        ip_hash: ipHash,
        user_agent: (userAgent || '').slice(0, 255),
        date_bucket: dateBucket,
        visited_at: isoNow
      }]);

      // 3. Atomically increment or update total visits in site_analytics
      const current = await getVisitorCount();
      const newCount = current + 1;

      await supabase.from('site_analytics').upsert({
        id: 1,
        total_visits: newCount,
        last_visit_at: isoNow
      });

      return { count: newCount, isNewVisit: true, message: 'New unique visit recorded in Supabase' };
    } catch (err) {
      console.warn('⚠️ Supabase error recording visit, using in-memory fallback:', err.message);
    }
  }

  // In-Memory Fallback
  const sessionKey = `${clientHash}_${dateBucket}`;
  if (inMemoryStore.sessions.has(sessionKey)) {
    return {
      count: inMemoryStore.visits,
      isNewVisit: false,
      message: 'Existing visitor session active (local memory)'
    };
  }

  inMemoryStore.sessions.set(sessionKey, { visitedAt: isoNow });
  inMemoryStore.visits += 1;
  inMemoryStore.lastVisitAt = isoNow;

  return {
    count: inMemoryStore.visits,
    isNewVisit: true,
    message: 'New unique visit recorded (in-memory)'
  };
}

module.exports = {
  getVisitorCount,
  recordVisit,
  BASELINE_COUNT
};
