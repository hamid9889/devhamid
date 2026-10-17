const express = require('express');
const router = express.Router();

// In-memory cache
let cachedRepos = null;
let lastFetchTime = 0;
const CACHE_TTL_MS = 15 * 60 * 1000; // 15 minutes

/**
 * GET /api/github/repos
 * Fetches and caches repositories for hamid9889
 */
router.get('/repos', async (req, res) => {
  const username = process.env.GITHUB_USERNAME || 'hamid9889';
  const now = Date.now();

  // Return cached data if still fresh
  if (cachedRepos && (now - lastFetchTime) < CACHE_TTL_MS) {
    return res.status(200).json(cachedRepos);
  }

  try {
    const headers = {
      'User-Agent': 'DevHamid-Portfolio-Backend',
      'Accept': 'application/vnd.github.v3+json'
    };

    if (process.env.GITHUB_TOKEN) {
      headers['Authorization'] = `Bearer ${process.env.GITHUB_TOKEN}`;
    }

    const ghUrl = `https://api.github.com/users/${username}/repos?sort=updated&per_page=30`;
    const response = await fetch(ghUrl, { headers });

    if (!response.ok) {
      const errText = await response.text();
      console.warn(`GitHub API returned status ${response.status}: ${errText}`);
      // If we have stale cache, return it rather than failing
      if (cachedRepos) {
        return res.status(200).json(cachedRepos);
      }
      return res.status(response.status).json({
        error: 'Failed to fetch repositories from GitHub',
        status: response.status
      });
    }

    const data = await response.json();
    if (Array.isArray(data)) {
      // Filter out user's profile README repo 'hamid9889'
      const filtered = data.filter(r => r.name !== username);
      cachedRepos = filtered;
      lastFetchTime = now;
      return res.status(200).json(filtered);
    } else {
      return res.status(500).json({ error: 'Unexpected GitHub API response structure' });
    }
  } catch (err) {
    console.error('Error fetching GitHub repos:', err);
    if (cachedRepos) {
      return res.status(200).json(cachedRepos);
    }
    return res.status(500).json({ error: 'Network error communicating with GitHub API' });
  }
});

module.exports = router;
