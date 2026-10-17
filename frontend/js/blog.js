/**
 * Modular Blog Section (LinkedIn-Style Cards)
 * Showcases Machine Learning libraries, mathematics, and interactive infographics.
 */

const BlogModule = (function () {
  let posts = [];
  let activeTag = 'all';

  // Format LinkedIn style author snippet
  function renderAuthorHeader(post) {
    return `
      <div class="linkedin-header">
        <img src="${post.author.avatar}" alt="${post.author.name}" class="author-avatar" />
        <div class="author-meta">
          <div class="author-top">
            <h4 class="author-name">${post.author.name}</h4>
            <span class="badge-connect">• 1st</span>
          </div>
          <p class="author-role">${post.author.role}</p>
          <div class="post-time-line">
            <span class="post-time">${post.date}</span>
            <span class="dot-separator">•</span>
            <span class="post-read">${post.readTime}</span>
            <span class="dot-separator">•</span>
            <svg class="globe-icon" viewBox="0 0 16 16" width="13" height="13" fill="currentColor">
              <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0ZM1.5 8a6.5 6.5 0 0 1 1.05-3.535l2.673 2.673A1.5 1.5 0 0 0 6.28 7.5h1.22a1.5 1.5 0 0 0 1.5-1.5V5.5c0-.414.336-.75.75-.75h.5a.75.75 0 0 0 .75-.75V3.535A6.47 6.47 0 0 1 14.5 8a6.47 6.47 0 0 1-.95 3.375l-2.05-2.05a1.5 1.5 0 0 0-1.06-.44h-.88a1.5 1.5 0 0 0-1.5 1.5v.56a.75.75 0 0 1-.75.75h-.375a.75.75 0 0 1-.75-.75v-.81a1.5 1.5 0 0 0-1.5-1.5H3.5a1.5 1.5 0 0 0-1.5 1.5v.19A6.474 6.474 0 0 1 1.5 8Z"></path>
            </svg>
          </div>
        </div>
        <div class="linkedin-logo-badge" title="LinkedIn Format">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="#0a66c2">
            <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9h2.8v8.37h-2.8v-8.37M7.86 6.54a1.63 1.63 0 1 0 0 3.26 1.63 1.63 0 0 0 0-3.26Z"/>
          </svg>
        </div>
      </div>
    `;
  }

  // Render post card
  function createPostCardHTML(post) {
    const userLiked = localStorage.getItem(`blog_liked_${post.id}`) === 'true';
    const likesCount = (post.likes || 100) + (userLiked ? 1 : 0);

    const tagsHTML = post.tags.map(t => `<span class="blog-tag">#${t}</span>`).join(' ');

    const takeawaysHTML = (post.keyTakeaways || []).map(item => `
      <li class="takeaway-item">
        <span class="takeaway-icon">⚡</span>
        <span>${item}</span>
      </li>
    `).join('');

    return `
      <article class="linkedin-card glass-card" id="post-${post.id}">
        <div class="card-glow"></div>
        ${renderAuthorHeader(post)}

        <div class="post-content">
          <span class="post-category-pill">${post.category}</span>
          <h3 class="post-title" onclick="BlogModule.openPostModal('${post.id}')">${post.title}</h3>
          <p class="post-summary">${post.summary}</p>

          <div class="post-tags-row">
            ${tagsHTML}
          </div>

          ${takeawaysHTML ? `<ul class="takeaway-list">${takeawaysHTML}</ul>` : ''}
        </div>

        <div class="post-media" onclick="BlogModule.openImageModal('${post.image}', '${post.title.replace(/'/g, "\\'")}')">
          <img src="${post.image}" alt="${post.title}" loading="lazy" class="infographic-img" />
          <div class="media-overlay">
            <span class="expand-badge">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                <path d="M15 3h6v6h-2V6.41l-4.29 4.3-1.42-1.42L17.59 5H15V3zM3 9V3h6v2H6.41l4.3 4.29-1.42 1.42L5 6.41V9H3zm6 12H3v-6h2v2.59l4.29-4.3 1.42 1.42L6.41 19H9v2zm12-6v6h-6v-2h2.59l-4.3-4.29 1.42-1.42L19 17.59V15h2z"/>
              </svg>
              Click to view high-res infographic
            </span>
          </div>
        </div>

        <!-- Social Reactions Bar -->
        <div class="post-social-stats">
          <span class="social-reaction-icons">
            <span class="react-circle blue">👍</span>
            <span class="react-circle green">💡</span>
            <span class="react-circle red">❤️</span>
            <span class="like-counter" id="like-count-${post.id}">${likesCount}</span>
          </span>
          <span class="social-comments-count">${post.commentsCount || 15} comments</span>
        </div>

        <div class="post-actions-bar">
          <button class="action-btn like-btn ${userLiked ? 'liked' : ''}" onclick="BlogModule.toggleLike('${post.id}')" id="like-btn-${post.id}">
            <svg class="action-icon" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/>
            </svg>
            <span>${userLiked ? 'Liked' : 'Like'}</span>
          </button>

          <button class="action-btn" onclick="BlogModule.openPostModal('${post.id}')">
            <svg class="action-icon" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
            </svg>
            <span>Read Article</span>
          </button>

          <button class="action-btn" onclick="BlogModule.sharePost('${post.id}', '${post.title.replace(/'/g, "\\'")}')">
            <svg class="action-icon" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
            </svg>
            <span>Share</span>
          </button>

          <a href="${post.linkedInUrl}" target="_blank" rel="noopener noreferrer" class="action-btn linkedin-btn" onclick="Analytics.trackEvent('blog_linkedin_profile_click', 'Blog', '${post.id}')">
            <span>Connect on LinkedIn</span>
            <svg viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
              <path fill-rule="evenodd" d="M8.22 2.97a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042l2.97-2.97H3.75a.75.75 0 0 1 0-1.5h7.44L8.22 4.03a.75.75 0 0 1 0-1.06Z"></path>
            </svg>
          </a>
        </div>
      </article>
    `;
  }

  // Render all cards
  function renderPosts() {
    const container = document.getElementById('blogPostsContainer');
    if (!container) return;

    let filtered = posts;
    if (activeTag !== 'all') {
      filtered = posts.filter(p => p.tags.some(t => t.toLowerCase() === activeTag.toLowerCase()) || p.category.toLowerCase().includes(activeTag.toLowerCase()));
    }

    container.innerHTML = filtered.map(createPostCardHTML).join('');
  }

  // Toggle like
  function toggleLike(postId) {
    const post = posts.find(p => p.id === postId);
    if (!post) return;

    const storageKey = `blog_liked_${postId}`;
    const wasLiked = localStorage.getItem(storageKey) === 'true';
    const isNowLiked = !wasLiked;

    localStorage.setItem(storageKey, isNowLiked.toString());

    const countEl = document.getElementById(`like-count-${postId}`);
    const btnEl = document.getElementById(`like-btn-${postId}`);

    const baseCount = post.likes || 100;
    const newCount = baseCount + (isNowLiked ? 1 : 0);

    if (countEl) countEl.textContent = newCount;
    if (btnEl) {
      btnEl.classList.toggle('liked', isNowLiked);
      btnEl.querySelector('span').textContent = isNowLiked ? 'Liked' : 'Like';
    }

    Analytics.trackEvent(isNowLiked ? 'blog_like' : 'blog_unlike', 'Blog', postId);
  }

  // Share post
  function sharePost(postId, title) {
    const postUrl = `${window.location.origin}${window.location.pathname}#post-${postId}`;

    if (navigator.clipboard) {
      navigator.clipboard.writeText(postUrl).then(() => {
        showToast('Link copied to clipboard! 📋', 'success');
      }).catch(() => {
        showToast(`Post URL: ${postUrl}`, 'info');
      });
    } else {
      showToast(`Post URL: ${postUrl}`, 'info');
    }

    Analytics.trackEvent('blog_share', 'Blog', postId);
  }

  // Open modal reading view
  function openPostModal(postId) {
    const post = posts.find(p => p.id === postId);
    if (!post) return;

    const modal = document.getElementById('postModal');
    const modalBody = document.getElementById('postModalBody');
    if (!modal || !modalBody) return;

    modalBody.innerHTML = `
      <div class="modal-article-header">
        <span class="post-category-pill">${post.category}</span>
        <h2>${post.title}</h2>
        <div class="modal-author-row">
          <img src="${post.author.avatar}" alt="${post.author.name}" class="modal-author-avatar"/>
          <div>
            <strong>${post.author.name}</strong>
            <p>${post.author.role} • ${post.date} • ${post.readTime}</p>
          </div>
        </div>
      </div>
      <div class="modal-infographic-wrap">
        <img src="${post.image}" alt="${post.title}" class="modal-infographic-img" />
      </div>
      <div class="modal-article-text">
        ${post.fullArticle.split('\n\n').map(p => {
          if (p.startsWith('### ')) {
            return `<h3>${p.replace('### ', '')}</h3>`;
          }
          return `<p>${p}</p>`;
        }).join('')}
      </div>
      <div class="modal-article-footer">
        <a href="${post.linkedInUrl}" target="_blank" rel="noopener noreferrer" class="contact-btn">
          Discuss on LinkedIn →
        </a>
      </div>
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    Analytics.trackEvent('blog_modal_open', 'Blog', postId);
  }

  // Open full-screen image preview
  function openImageModal(imgSrc, title) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImageElement');
    const modalTitle = document.getElementById('modalImageTitle');
    if (!modal || !modalImg) return;

    modalImg.src = imgSrc;
    if (modalTitle) modalTitle.textContent = title;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    Analytics.trackEvent('infographic_zoom', 'Blog', title);
  }

  // Close modals
  function closeModals() {
    document.querySelectorAll('.app-modal').forEach(m => m.classList.remove('active'));
    document.body.style.overflow = '';
  }

  // Fetch posts from backend or static json
  async function loadPosts() {
    try {
      // Try backend route first
      let data = null;
      try {
        const res = await fetch(`${APP_CONFIG.backendApiUrl}/posts`, { signal: AbortSignal.timeout(3000) });
        if (res.ok) {
          data = await res.json();
        }
      } catch (e) {}

      // Fallback to static JSON
      if (!data || !Array.isArray(data)) {
        const res = await fetch('data/posts.json');
        if (res.ok) {
          data = await res.json();
        }
      }

      if (Array.isArray(data) && data.length > 0) {
        posts = data;
        renderPosts();
      }
    } catch (err) {
      console.warn('Error loading blog posts:', err);
    }
  }

  // Setup modal handlers
  function bindModals() {
    document.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
      el.addEventListener('click', closeModals);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModals();
    });

    // Tag filter chips
    document.querySelectorAll('.blog-filter-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('.blog-filter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        activeTag = chip.dataset.tag;
        Analytics.trackEvent('blog_tag_filter', 'Blog', activeTag);
        renderPosts();
      });
    });
  }

  return {
    init: function () {
      bindModals();
      loadPosts();
    },
    toggleLike: toggleLike,
    sharePost: sharePost,
    openPostModal: openPostModal,
    openImageModal: openImageModal,
    closeModals: closeModals
  };
})();
