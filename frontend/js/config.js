// Base API URL (Render backend)
const API_URL = "https://devhamid.onrender.com";

// Health check
async function checkHealth() {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

// Fetch projects from Supabase via backend
async function fetchProjects() {
  const res = await fetch(`${API_URL}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

// Increment visits counter
async function incrementVisits() {
  const res = await fetch(`${API_URL}/visits`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to increment visits");
  return res.json();
}

// Example usage in frontend component / exported for modules
async function runPortfolio() {
  console.log("Checking backend health...");
  const health = await checkHealth();
  console.log("Health:", health);

  console.log("Fetching projects...");
  const projects = await fetchProjects();
  console.log("Projects:", projects);

  console.log("Incrementing visits...");
  await incrementVisits();
  console.log("Visits incremented successfully!");
}

// Expose on global window object
if (typeof window !== 'undefined') {
  window.API_URL = API_URL;
  window.checkHealth = checkHealth;
  window.fetchProjects = fetchProjects;
  window.incrementVisits = incrementVisits;
  window.runPortfolio = runPortfolio;
}

const APP_CONFIG = {
  // Base API URL
  apiUrl: API_URL,

  // GitHub Profile
  githubUsername: 'hamid9889',

  // Backend API URL:
  // Connects directly to production Render backend, or localhost if testing locally
  backendApiUrl: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : API_URL,

  // Render backend live URL
  renderBackendUrl: API_URL,

  // Google Analytics 4 Measurement ID
  googleAnalyticsId: 'G-MEASUREMENT_ID',

  // Fallback pinned/curated repositories in case GitHub API rate limit is reached
  fallbackRepos: [
    {
      name: 'Snap-Class-Attendance-System',
      description: 'Smart attendance platform using face recognition and voice biometric attendance, with student & teacher portals for automated tracking and records.',
      html_url: 'https://github.com/hamid9889/Snap-Class-Attendance-System',
      language: 'Python',
      stargazers_count: 5,
      forks_count: 2,
      topics: ['computer-vision', 'face-recognition', 'deep-learning', 'python', 'attendance-system'],
      updated_at: '2026-10-15T09:00:00Z',
      category: 'ai'
    },
    {
      name: 'Agentic-Ai-',
      description: 'Autonomous multi-agent LLM reasoning pipeline with memory buffers, tool dispatching, and automated plan execution workflows.',
      html_url: 'https://github.com/hamid9889/Agentic-Ai-',
      language: 'Python',
      stargazers_count: 4,
      forks_count: 1,
      topics: ['agentic-ai', 'llm', 'langchain', 'autonomous-agents', 'python'],
      updated_at: '2026-10-12T11:20:00Z',
      category: 'ai'
    },
    {
      name: 'Ai-Assistant-Email-Summarizer',
      description: 'Intelligent inbox email summarizer and smart-reply drafting assistant powered by NLP and transformer summarization models.',
      html_url: 'https://github.com/hamid9889/Ai-Assistant-Email-Summarizer',
      language: 'Python',
      stargazers_count: 4,
      forks_count: 0,
      topics: ['nlp', 'transformers', 'email-assistant', 'productivity'],
      updated_at: '2026-10-05T14:40:00Z',
      category: 'ai'
    },
    {
      name: 'DSA-in-PYTHON',
      description: 'Comprehensive repository of Data Structures & Algorithms implemented in Python: Trees, Graphs, Dynamic Programming, and LeetCode problem solutions.',
      html_url: 'https://github.com/hamid9889/DSA-in-PYTHON',
      language: 'Python',
      stargazers_count: 4,
      forks_count: 1,
      topics: ['dsa', 'algorithms', 'data-structures', 'leetcode', 'python'],
      updated_at: '2026-09-28T16:15:00Z',
      category: 'dsa'
    },
    {
      name: 'Minor-project-E-Commerce-machine-Learning-Model',
      description: 'Customer churn prediction, recommendation engine, and lifetime value regression models for e-commerce platforms using XGBoost and Scikit-Learn.',
      html_url: 'https://github.com/hamid9889/Minor-project-E-Commerce-machine-Learning-Model',
      language: 'Jupyter Notebook',
      stargazers_count: 3,
      forks_count: 1,
      topics: ['machine-learning', 'e-commerce', 'xgboost', 'scikit-learn'],
      updated_at: '2026-09-18T10:30:00Z',
      category: 'ai'
    },
    {
      name: 'RNN-model',
      description: 'Recurrent Neural Network & LSTM architectures implemented for sequential time-series forecasting and natural language sentiment classification.',
      html_url: 'https://github.com/hamid9889/RNN-model',
      language: 'Jupyter Notebook',
      stargazers_count: 3,
      forks_count: 0,
      topics: ['deep-learning', 'rnn', 'lstm', 'time-series', 'pytorch'],
      updated_at: '2026-09-02T08:00:00Z',
      category: 'ai'
    },
    {
      name: 'Loan-system',
      description: 'Fintech risk evaluation and credit risk assessment classification pipeline with automated feature engineering and model interpretability (SHAP).',
      html_url: 'https://github.com/hamid9889/Loan-system',
      language: 'Python',
      stargazers_count: 3,
      forks_count: 0,
      topics: ['fintech', 'credit-risk', 'machine-learning', 'classification'],
      updated_at: '2026-08-20T17:45:00Z',
      category: 'ai'
    },
    {
      name: 'devhamid',
      description: 'Source code for modern portfolio website with dark/light themes, GitHub API integration, LinkedIn-style ML blog, and visitor analytics.',
      html_url: 'https://github.com/hamid9889/devhamid',
      language: 'JavaScript',
      stargazers_count: 3,
      forks_count: 0,
      topics: ['portfolio', 'html5', 'css3', 'javascript', 'backend-integration'],
      updated_at: '2026-10-17T12:00:00Z',
      category: 'web'
    }
  ]
};
