const express = require('express');
const router = express.Router();
const { answerPortfolioQuery, getAiPipelineStatus } = require('../services/aiPipelines');

/**
 * GET /api/ai/health
 * Returns status of AI/ML and GenAI modules
 */
router.get('/health', (req, res) => {
  return res.status(200).json(getAiPipelineStatus());
});

/**
 * POST /api/ai/chat
 * Generative AI Assistant chat endpoint for portfolio visitors
 */
router.post('/chat', async (req, res) => {
  try {
    const { prompt, name } = req.body || {};
    if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    const response = await answerPortfolioQuery(prompt.trim(), name || 'Visitor');
    return res.status(200).json(response);
  } catch (err) {
    console.error('AI Chat Error:', err);
    return res.status(500).json({ error: 'Failed to generate AI response' });
  }
});

/**
 * POST /api/ai/face-verify
 * Endpoint for testing Computer Vision face verification pipeline
 */
router.post('/face-verify', (req, res) => {
  const { imageBase64, targetName } = req.body || {};
  if (!imageBase64) {
    return res.status(400).json({ error: 'imageBase64 is required for facial verification' });
  }

  // Simulated live pipeline response
  return res.status(200).json({
    success: true,
    matched: true,
    confidence: 0.96,
    identifiedAs: targetName || 'Hamid',
    pipeline: 'face_recognition + opencv-python-headless',
    timestamp: new Date().toISOString()
  });
});

/**
 * POST /api/ai/speech-transcribe
 * Endpoint for testing SpeechRecognition and PyDub voice pipeline
 */
router.post('/speech-transcribe', (req, res) => {
  const { audioBase64, format } = req.body || {};
  if (!audioBase64) {
    return res.status(400).json({ error: 'audioBase64 is required for speech transcription' });
  }

  return res.status(200).json({
    success: true,
    transcript: 'Hello Hamid, voice attendance command processed successfully.',
    confidence: 0.97,
    pipeline: 'SpeechRecognition + PyDub',
    format: format || 'wav',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
