const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

const POSTS_FILE = path.join(__dirname, '..', '..', 'frontend', 'data', 'posts.json');

function getPosts() {
  try {
    if (fs.existsSync(POSTS_FILE)) {
      const data = fs.readFileSync(POSTS_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.warn('Error reading posts.json:', err.message);
  }
  return [];
}

/**
 * GET /api/posts
 * Returns all modular blog posts
 */
router.get('/', (req, res) => {
  const posts = getPosts();
  res.status(200).json(posts);
});

/**
 * GET /api/posts/:id
 * Returns a single post by ID
 */
router.get('/:id', (req, res) => {
  const posts = getPosts();
  const post = posts.find(p => p.id === req.params.id);
  if (!post) {
    return res.status(404).json({ error: 'Post not found' });
  }
  res.status(200).json(post);
});

module.exports = router;
