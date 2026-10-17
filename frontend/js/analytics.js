/**
 * Analytics Module:
 * - Real-Visit Counter backed by SQLite Database
 * - Google Analytics 4 Integration (gtag.js loader + event tracking)
 */

const Analytics = (function () {
  const LOCAL_STORAGE_KEY = 'devhamid_visitor_count';
  const VISITOR_ID_KEY = 'devhamid_visitor_uuid';
  const SESSION_VISITED_KEY = 'devhamid_session_counted';
  const BASELINE_COUNT = 1482;

  // Retrieve or create persistent anonymous visitor ID
  function getVisitorId() {
    let id = localStorage.getItem(VISITOR_ID_KEY);
    if (!id) {
      id = 'vis_' + Math.random().toString(36).substring(2, 12) + '_' + Date.now().toString(36);
      localStorage.setItem(VISITOR_ID_KEY, id);
    }
    return id;
  }

  // Initialize Google Analytics 4
  function initGoogleAnalytics() {
    const gaId = APP_CONFIG.googleAnalyticsId;
    if (!gaId || gaId === 'G-MEASUREMENT_ID') {
      console.log('ℹ️ Google Analytics: Configure your GA4 Measurement ID in config.js to track real traffic.');
      return;
    }

    try {
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
      document.head.appendChild(script);

      window.dataLayer = window.dataLayer || [];
      function gtag() {
        window.dataLayer.push(arguments);
      }
      window.gtag = gtag;

      gtag('js', new Date());
      gtag('config', gaId, {
        page_title: document.title,
        page_location: window.location.href,
        send_page_view: true
      });

      console.log(`✅ Google Analytics 4 initialized with ID: ${gaId}`);
    } catch (err) {
      console.warn('Google Analytics initialization skipped:', err);
    }
  }

  // Track custom event in GA4
  function trackEvent(action, category, label, value) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', action, {
        event_category: category,
        event_label: label,
        value: value
      });
    }
    console.log(`📊 Analytics Event: [${category}] ${action} -> ${label || ''}`);
  }

  // Animate count-up display
  function animateCounter(targetNumber) {
    const el = document.getElementById('visitorCountDisplay');
    if (!el) return;

    const duration = 1200; // ms
    const startNumber = Math.max(0, targetNumber - 45);
    const startTime = performance.now();

    function update(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // Ease out cubic
      const current = Math.floor(startNumber + (targetNumber - startNumber) * ease);

      el.textContent = current.toLocaleString();

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = targetNumber.toLocaleString();
      }
    }

    requestAnimationFrame(update);
  }

  // Fetch and record real visit in SQLite database
  async function initVisitorCounter() {
    const visitorId = getVisitorId();
    const isNewSession = !sessionStorage.getItem(SESSION_VISITED_KEY);
    let count = null;

    const endpoints = [
      `${APP_CONFIG.backendApiUrl}/analytics/visit`,
      `${APP_CONFIG.renderBackendUrl}/analytics/visit`
    ];

    for (const url of endpoints) {
      try {
        const method = isNewSession ? 'POST' : 'GET';
        const options = {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(3500)
        };

        if (isNewSession) {
          options.body = JSON.stringify({
            visitorId: visitorId,
            referrer: document.referrer || 'direct',
            screen: `${window.innerWidth}x${window.innerHeight}`
          });
        }

        const res = await fetch(url, options);

        if (res.ok) {
          const data = await res.json();
          if (data && typeof data.count === 'number') {
            count = data.count;
            if (isNewSession) {
              sessionStorage.setItem(SESSION_VISITED_KEY, 'true');
            }
            localStorage.setItem(LOCAL_STORAGE_KEY, count.toString());
            break;
          }
        }
      } catch (err) {
        // Backend offline or waking up, try fallback
      }
    }

    // Fallback if backend is not reachable
    if (count === null) {
      let stored = parseInt(localStorage.getItem(LOCAL_STORAGE_KEY), 10);
      if (isNaN(stored) || stored < BASELINE_COUNT) {
        stored = BASELINE_COUNT;
      }
      if (isNewSession) {
        stored += 1;
        sessionStorage.setItem(SESSION_VISITED_KEY, 'true');
        localStorage.setItem(LOCAL_STORAGE_KEY, stored.toString());
      }
      count = stored;
    }

    animateCounter(count);
  }

  return {
    init: function () {
      initGoogleAnalytics();
      initVisitorCounter();
    },
    trackEvent: trackEvent
  };
})();
