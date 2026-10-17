const express = require('express');
const router = express.Router();
const { getVisitorCount, recordVisit } = require('../models/analyticsModel');

/**
 * GET /api/analytics/visitor (or /api/analytics/visit)
 * Returns the current total visitor count without incrementing.
 */
async function handleGetCount(req, res) {
  try {
    const count = await getVisitorCount();
    return res.status(200).json({ count });
  } catch (err) {
    console.error('Error fetching visitor count from Supabase/cache:', err);
    return res.status(500).json({ error: 'Failed to retrieve visitor count' });
  }
}

/**
 * POST /api/analytics/visitor (or /api/analytics/visit)
 * Records a unique visit in Supabase ONLY if not already counted today.
 */
async function handleRecordVisit(req, res) {
  try {
    const { visitorId } = req.body || {};

    // Extract client IP address accurately (supporting cloud proxies like Vercel, Render)
    const forwardedFor = req.headers['x-forwarded-for'];
    const ipAddress = forwardedFor ? forwardedFor.split(',')[0].trim() : req.socket.remoteAddress;
    const userAgent = req.headers['user-agent'] || '';

    const result = await recordVisit({
      visitorId,
      ipAddress,
      userAgent
    });

    return res.status(200).json({
      success: true,
      count: result.count,
      isNewVisit: result.isNewVisit,
      message: result.message
    });
  } catch (err) {
    console.error('Error recording visit:', err);
    const fallbackCount = await getVisitorCount();
    return res.status(500).json({
      success: false,
      count: fallbackCount,
      error: 'Failed to record visit'
    });
  }
}

// Support both /visitor and /visit endpoints for maximum compatibility
router.get('/visitor', handleGetCount);
router.get('/visit', handleGetCount);

router.post('/visitor', handleRecordVisit);
router.post('/visit', handleRecordVisit);

module.exports = router;
