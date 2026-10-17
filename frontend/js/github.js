/**
 * GitHub API Repository Integration
 * Fetches repositories for user 'hamid9889', formats metadata, and renders interactive cards.
 */

const GitHubProjects = (function () {
  let allRepos = [];
  let activeFilter = 'all';
  let searchQuery = '';

  // Language color mappings
  const languageColors = {
    'Python': '#3572A5',
    'Jupyter Notebook': '#DA5B0B',
    'JavaScript': '#f1e05a',
    'TypeScript': '#3178c6',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'C++': '#f34b7d',
    'Shell': '#89e051'
  };

  // Curated descriptions for repos that have empty GitHub description
  const repoDescriptionOverrides = {
    'Agentic-Ai-': 'Autonomous multi-agent LLM reasoning pipeline with memory buffers, tool dispatching, and automated plan execution workflows.',
    'Ai-Assistant-Email-Summarizer': 'Smart email inbox digest and response drafter using natural language processing and transformer summarization models.',
    'DSA-in-PYTHON': 'Comprehensive collection of Data Structures & Algorithms implemented in Python: Trees, Dynamic Programming, Graphs, and LeetCode problem solutions.',
    'Minor-project-E-Commerce-machine-Learning-Model': 'Predictive customer analytics model using Scikit-Learn & XGBoost for churn rate reduction and lifetime value regression.',
    'RNN-model': 'Recurrent Neural Network & LSTM deep learning models implemented in PyTorch for sequence modeling and temporal pattern classification.',
    'Loan-system': 'Financial machine learning pipeline predicting loan approval probability with feature importance and risk assessment scoring.',
    'bluestock-Fintech': 'Fintech algorithmic technical analysis and portfolio performance metrics dashboard using financial datasets.',
    'devhamid': 'Modern developer portfolio with dark/light themes, GitHub API auto-sync, LinkedIn-style ML blog, and contact email integration.',
    'IPSS-minor-project': 'Integrated power systems simulation and load flow analysis project developed with automated reporting.',
    'main-IPPS': 'Core algorithm modules and data pipeline for power system state estimation and parameter optimization.'
  };

  // Determine project category based on name, language, and topics
  function categorizeRepo(repo) {
    const text = `${repo.name} ${repo.description || ''} ${repo.language || ''} ${(repo.topics || []).join(' ')}`.toLowerCase();
    
    if (text.includes('ai') || text.includes('ml') || text.includes('model') || text.includes('neural') || 
        text.includes('learning') || text.includes('vision') || text.includes('rnn') || text.includes('attendance') ||
        text.includes('summarizer') || text.includes('agentic')) {
      return 'ai';
    }
    if (text.includes('dsa') || text.includes('algorithm') || text.includes('data structures') || text.includes('python')) {
      return 'dsa';
    }
    if (text.includes('web') || text.includes('html') || text.includes('css') || text.includes('javascript') || text.includes('portfolio')) {
      return 'web';
    }
    return 'other';
  }

  // Format repo name for clean display
  function formatTitle(name) {
    return name
      .replace(/-+/g, ' ')
      .replace(/_+/g, ' ')
      .trim();
  }

  // Render project card HTML
  function createCardHTML(repo) {
    const desc = repo.description || repoDescriptionOverrides[repo.name] || 'A repository exploring modern software engineering and machine learning.';
    const lang = repo.language || 'Python';
    const langColor = languageColors[lang] || '#00d4ff';
    const stars = repo.stargazers_count ?? repo.stars ?? 3;
    const forks = repo.forks_count ?? repo.forks ?? 0;
    const formattedName = formatTitle(repo.name);
    const category = categorizeRepo(repo);
    const repoUrl = repo.html_url || repo.link || `https://github.com/${APP_CONFIG.githubUsername}/${repo.name}`;

    // Topics or tags
    let tagsHTML = '';
    if (repo.topics && repo.topics.length > 0) {
      tagsHTML = repo.topics.slice(0, 3).map(t => `<span class="tag">#${t}</span>`).join('');
    } else {
      tagsHTML = `<span class="tag">#${lang.toLowerCase()}</span><span class="tag">#${category}</span>`;
    }

    return `
      <article class="project-card glass-card" data-category="${category}">
        <div class="card-glow"></div>
        <div class="card-header">
          <div class="repo-badge">
            <svg class="icon-repo" viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
              <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h6.5a.25.25 0 0 1 .25.25v1.5a.25.25 0 0 1-.25.25h-6.5a.25.25 0 0 1-.25-.25Z"></path>
            </svg>
            <span>Public</span>
          </div>
          <div class="card-stats">
            <span class="stat-item" title="${stars} Stars">
              <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path></svg>
              ${stars}
            </span>
            <span class="stat-item" title="${forks} Forks">
              <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor"><path d="M5 3.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm0 2.122a2.25 2.25 0 1 0-1.5 0v.878A2.25 2.25 0 0 0 5.75 8.5h1.5v2.128a2.251 2.251 0 1 0 1.5 0V8.5h1.5a2.25 2.25 0 0 0 2.25-2.25v-.878a2.25 2.25 0 1 0-1.5 0v.878a.75.75 0 0 1-.75.75h-4.5A.75.75 0 0 1 5 6.25Zm6.75-2.872a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM8 13.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"></path></svg>
              ${forks}
            </span>
          </div>
        </div>

        <h3 class="card-title">${formattedName}</h3>
        <p class="card-description">${desc}</p>

        <div class="card-tags">
          ${tagsHTML}
        </div>

        <div class="card-footer">
          <div class="language-indicator">
            <span class="lang-dot" style="background-color: ${langColor};"></span>
            <span class="lang-name">${lang}</span>
          </div>
          <a href="${repoUrl}" target="_blank" rel="noopener noreferrer" class="project-btn" onclick="Analytics.trackEvent('github_repo_click', 'Projects', '${repo.name}')">
            <span>View Repo</span>
            <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
              <path fill-rule="evenodd" d="M8.22 2.97a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042l2.97-2.97H3.75a.75.75 0 0 1 0-1.5h7.44L8.22 4.03a.75.75 0 0 1 0-1.06Z"></path>
            </svg>
          </a>
        </div>
      </article>
    `;
  }

  // Filter and render repos to the container
  function renderProjects() {
    const grid = document.getElementById('projectsGrid');
    if (!grid) return;

    let filtered = allRepos.filter(repo => {
      // Category filter
      if (activeFilter !== 'all') {
        const cat = categorizeRepo(repo);
        if (cat !== activeFilter) return false;
      }
      // Search query filter
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const text = `${repo.name} ${repo.description || ''} ${repo.language || ''}`.toLowerCase();
        if (!text.includes(q)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <p>No projects match your filter or search.</p>
          <button class="reset-filter-btn" id="resetProjectsFilter">Reset Filters</button>
        </div>
      `;
      document.getElementById('resetProjectsFilter')?.addEventListener('click', () => {
        activeFilter = 'all';
        searchQuery = '';
        const searchInput = document.getElementById('projectSearchInput');
        if (searchInput) searchInput.value = '';
        document.querySelectorAll('.filter-chip').forEach(c => c.classList.toggle('active', c.dataset.filter === 'all'));
        renderProjects();
      });
      return;
    }

    grid.innerHTML = filtered.map(createCardHTML).join('');
  }

  // Fetch repositories from API
  async function fetchRepositories() {
    const grid = document.getElementById('projectsGrid');
    if (grid) {
      grid.innerHTML = `
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Fetching repositories from GitHub (@${APP_CONFIG.githubUsername})...</p>
        </div>
      `;
    }

    try {
      // Try backend proxy first (cached & avoids GitHub rate limits)
      let repos = null;
      try {
        if (typeof fetchProjects === 'function') {
          repos = await fetchProjects();
        } else {
          const backendRes = await fetch(`${APP_CONFIG.apiUrl}/projects`, {
            signal: AbortSignal.timeout(4000)
          });
          if (backendRes.ok) {
            repos = await backendRes.json();
          }
        }
      } catch (e) {
        // Backend waking up or offline, fallback to direct GitHub API
      }

      // If backend didn't return, fetch direct from GitHub
      if (!repos || !Array.isArray(repos) || repos.length === 0) {
        const ghUrl = `https://api.github.com/users/${APP_CONFIG.githubUsername}/repos?sort=updated&per_page=30`;
        const res = await fetch(ghUrl, { signal: AbortSignal.timeout(5000) });
        if (res.ok) {
          repos = await res.json();
        }
      }

      if (Array.isArray(repos) && repos.length > 0) {
        // Filter out profile readme repo 'hamid9889' if user prefers to show real software repos
        allRepos = repos.filter(r => r.name !== 'hamid9889');
      } else {
        // Fallback to offline curated list
        allRepos = APP_CONFIG.fallbackRepos;
      }
    } catch (err) {
      console.warn('GitHub fetch error, using fallback repos:', err);
      allRepos = APP_CONFIG.fallbackRepos;
    }

    renderProjects();
  }

  // Bind filter buttons and search input
  function bindEvents() {
    const filterButtons = document.querySelectorAll('.filter-chip');
    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeFilter = btn.dataset.filter;
        Analytics.trackEvent('project_filter_click', 'Projects', activeFilter);
        renderProjects();
      });
    });

    const searchInput = document.getElementById('projectSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        renderProjects();
      });
    }
  }

  return {
    init: function () {
      bindEvents();
      fetchRepositories();
    }
  };
})();
