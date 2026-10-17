/**
 * Contact Form Module
 * Handles client-side validation, backend API submission, and animated feedback toasts.
 */

// Toast notification helper accessible globally
function showToast(message, type = 'info', duration = 4500) {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };

  toast.innerHTML = `
    <span class="toast-icon">${iconMap[type] || 'ℹ️'}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close" aria-label="Close notification">&times;</button>
  `;

  toast.querySelector('.toast-close').addEventListener('click', () => {
    toast.classList.add('hide');
    setTimeout(() => toast.remove(), 300);
  });

  toastContainer.appendChild(toast);

  // Auto dismiss
  setTimeout(() => {
    if (toast.parentElement) {
      toast.classList.add('hide');
      setTimeout(() => toast.remove(), 300);
    }
  }, duration);
}

const ContactForm = (function () {
  const form = document.getElementById('contactForm');
  const nameInput = document.getElementById('contactName');
  const emailInput = document.getElementById('contactEmail');
  const messageInput = document.getElementById('contactMessage');
  const submitBtn = document.getElementById('contactSubmitBtn');

  // Regex for standard RFC 5322 compliant email format
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;

  // Set field error state
  function setError(input, message) {
    const group = input.closest('.form-group');
    if (!group) return;
    group.classList.add('has-error');
    let errorEl = group.querySelector('.field-error');
    if (!errorEl) {
      errorEl = document.createElement('span');
      errorEl.className = 'field-error';
      group.appendChild(errorEl);
    }
    errorEl.textContent = message;
  }

  // Clear field error state
  function clearError(input) {
    const group = input.closest('.form-group');
    if (!group) return;
    group.classList.remove('has-error');
    const errorEl = group.querySelector('.field-error');
    if (errorEl) errorEl.textContent = '';
  }

  // Validate entire form
  function validate() {
    let isValid = true;

    // Validate Name
    const nameVal = nameInput.value.trim();
    if (!nameVal) {
      setError(nameInput, 'Name is required.');
      isValid = false;
    } else if (nameVal.length < 2) {
      setError(nameInput, 'Please enter at least 2 characters.');
      isValid = false;
    } else {
      clearError(nameInput);
    }

    // Validate Email
    const emailVal = emailInput.value.trim();
    if (!emailVal) {
      setError(emailInput, 'Email address is required.');
      isValid = false;
    } else if (!emailRegex.test(emailVal)) {
      setError(emailInput, 'Please enter a valid email address (e.g. name@example.com).');
      isValid = false;
    } else {
      clearError(emailInput);
    }

    // Validate Message
    const msgVal = messageInput.value.trim();
    if (!msgVal) {
      setError(messageInput, 'Message is required.');
      isValid = false;
    } else if (msgVal.length < 10) {
      setError(messageInput, 'Message should be at least 10 characters long.');
      isValid = false;
    } else {
      clearError(messageInput);
    }

    return isValid;
  }

  // Attach live validation on input/blur
  function bindLiveValidation() {
    [nameInput, emailInput, messageInput].forEach(input => {
      if (!input) return;
      input.addEventListener('input', () => clearError(input));
      input.addEventListener('blur', () => {
        if (input === nameInput && nameInput.value.trim().length > 0 && nameInput.value.trim().length < 2) {
          setError(nameInput, 'Please enter at least 2 characters.');
        } else if (input === emailInput && emailInput.value.trim().length > 0 && !emailRegex.test(emailInput.value.trim())) {
          setError(emailInput, 'Please enter a valid email address.');
        } else if (input === messageInput && messageInput.value.trim().length > 0 && messageInput.value.trim().length < 10) {
          setError(messageInput, 'Message should be at least 10 characters.');
        }
      });
    });
  }

  // Submit form
  async function handleSubmit(e) {
    e.preventDefault();

    if (!validate()) {
      showToast('Please fix the highlighted errors before submitting.', 'warning');
      return;
    }

    const payload = {
      name: nameInput.value.trim(),
      email: emailInput.value.trim(),
      message: messageInput.value.trim(),
      timestamp: new Date().toISOString()
    };

    // UI Loading state
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <span class="spinner-small"></span>
      <span>Sending Message...</span>
    `;

    const endpoints = [
      `${APP_CONFIG.apiUrl}/contact`,
      `${APP_CONFIG.backendApiUrl}/contact`,
      'http://localhost:5000/contact',
      `${APP_CONFIG.renderBackendUrl}/contact`
    ];

    let success = false;
    let responseData = null;
    let errorMessage = '';

    for (const url of endpoints) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload),
          signal: AbortSignal.timeout(9000)
        });

        responseData = await response.json().catch(() => null);

        if (response.ok && responseData && (responseData.status === 'success' || responseData.success)) {
          success = true;
          break;
        } else {
          errorMessage = responseData?.message || `Server error (${response.status})`;
        }
      } catch (err) {
        errorMessage = err.name === 'TimeoutError'
          ? 'Server connection timed out (Render free tier may be waking up).'
          : 'Unable to reach email backend server.';
      }
    }

    // Reset button state
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalBtnText;

    if (success) {
      const msg = responseData?.message || 'Email sent successfully!';
      showToast(`🎉 ${msg}`, 'success', 6000);
      form.reset();
      Analytics.trackEvent('contact_form_success', 'Contact', payload.name);
    } else {
      // Show failure message with direct mailto fallback option
      const fallbackMailto = `mailto:8090hamid@gmail.com?subject=Portfolio%20Inquiry%20from%20${encodeURIComponent(payload.name)}&body=${encodeURIComponent(payload.message)}`;
      showToast(`⚠️ ${errorMessage || 'Could not send message.'} Click "Email Me Directly" below.`, 'error', 7000);
      
      // Offer direct mailto
      let fallbackBox = document.getElementById('contactFallbackNotice');
      if (!fallbackBox) {
        fallbackBox = document.createElement('div');
        fallbackBox.id = 'contactFallbackNotice';
        fallbackBox.className = 'contact-fallback-notice';
        form.appendChild(fallbackBox);
      }
      fallbackBox.innerHTML = `
        <p>Backend not reachable right now? You can send via your email client:</p>
        <a href="${fallbackMailto}" class="contact-btn mailto-btn">
          ✉️ Open in Email Client (8090hamid@gmail.com)
        </a>
      `;
      Analytics.trackEvent('contact_form_error', 'Contact', errorMessage);
    }
  }

  return {
    init: function () {
      if (!form) return;
      bindLiveValidation();
      form.addEventListener('submit', handleSubmit);
    }
  };
})();
