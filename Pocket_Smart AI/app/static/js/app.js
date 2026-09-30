/* ==========================================================================
   PocketSmart AI - Frontend JavaScript Framework
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initAuthForms();
  initPlannerForms();
  initImageUploadPreview();
});

/* Toast Notification Utility */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : '⚠️'}</span>
    <div>${message}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/* Loading Overlay Manager */
function showLoading(customText = 'PocketSmart AI is analyzing your budget and preferences...') {
  const overlay = document.getElementById('loading-overlay');
  const textEl = document.getElementById('loading-text');
  if (textEl) textEl.textContent = customText;
  if (overlay) overlay.classList.add('active');
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.classList.remove('active');
}

/* Auth Forms handling */
function initAuthForms() {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;

      showLoading('Logging in securely...');

      try {
        const res = await fetch('/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await res.json();
        hideLoading();

        if (res.ok) {
          showToast('Welcome back! Redirecting to dashboard...');
          setTimeout(() => window.location.href = '/dashboard', 800);
        } else {
          showToast(data.detail || 'Login failed. Please check your credentials.', 'error');
        }
      } catch (err) {
        hideLoading();
        showToast('Network error occurred. Please try again.', 'error');
      }
    });
  }

  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('name').value;
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const confirm_password = document.getElementById('confirm_password').value;

      if (password !== confirm_password) {
        showToast('Passwords do not match.', 'error');
        return;
      }

      showLoading('Creating your PocketSmart AI account...');

      try {
        const res = await fetch('/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password, confirm_password })
        });

        const data = await res.json();
        hideLoading();

        if (res.ok) {
          showToast('Registration successful! Redirecting to dashboard...');
          setTimeout(() => window.location.href = '/dashboard', 800);
        } else {
          showToast(data.detail || 'Registration failed.', 'error');
        }
      } catch (err) {
        hideLoading();
        showToast('Network error occurred.', 'error');
      }
    });
  }
}

/* Logout Helper */
async function logoutUser() {
  showLoading('Logging out...');
  try {
    await fetch('/logout');
    window.location.href = '/';
  } catch (err) {
    window.location.href = '/';
  }
}

/* Image Upload Preview for Jewelry Planner */
function initImageUploadPreview() {
  const fileInput = document.getElementById('outfit_image');
  const previewBox = document.getElementById('image-preview-container');
  const previewImg = document.getElementById('image-preview');

  if (fileInput && previewBox && previewImg) {
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        if (file.size > 5 * 1024 * 1024) {
          showToast('Image file size exceeds 5MB limit.', 'error');
          fileInput.value = '';
          previewBox.style.display = 'none';
          return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
          previewImg.src = event.target.result;
          previewBox.style.display = 'block';
        };
        reader.readAsDataURL(file);
      } else {
        previewBox.style.display = 'none';
      }
    });
  }
}

/* Planner Forms logic */
function initPlannerForms() {
  // Home Planner Form
  const homeForm = document.getElementById('home-planner-form');
  if (homeForm) {
    homeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const budget = parseFloat(document.getElementById('budget').value);
      const room_type = document.getElementById('room_type').value;
      const home_type = document.getElementById('home_type').value;
      const style = document.getElementById('style').value;
      const color_preference = document.getElementById('color_preference').value;
      const material_preference = document.getElementById('material_preference').value;
      const brand_preference = document.getElementById('brand_preference').value;
      const must_have_items = document.getElementById('must_have_items').value;
      const avoid_items = document.getElementById('avoid_items').value;

      const checkedItems = Array.from(document.querySelectorAll('input[name="items_required"]:checked')).map(cb => cb.value);

      const payload = {
        budget,
        home_type,
        room_type,
        style,
        items_required: checkedItems,
        color_preference,
        material_preference,
        brand_preference,
        must_have_items,
        avoid_items
      };

      showLoading('PocketSmart AI is analyzing your home budget and space preferences...');

      try {
        const res = await fetch('/generate-home', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        hideLoading();

        if (res.ok && data.id) {
          showToast('Recommendations generated!');
          window.location.href = `/results/${data.id}`;
        } else {
          showToast(data.detail || 'Failed to generate recommendations.', 'error');
        }
      } catch (err) {
        hideLoading();
        showToast('Error connecting to server.', 'error');
      }
    });
  }

  // Party Planner Form
  const partyForm = document.getElementById('party-planner-form');
  if (partyForm) {
    partyForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const budget = parseFloat(document.getElementById('budget').value);
      const guests = parseInt(document.getElementById('guests').value);
      const event_type = document.getElementById('event_type').value;
      const venue_preference = document.getElementById('venue_preference').value;
      const location = document.getElementById('location').value;
      const food_preference = document.getElementById('food_preference').value;
      const decoration_style = document.getElementById('decoration_style').value;
      const entertainment_preference = document.getElementById('entertainment_preference').value;
      const accommodation_required = document.getElementById('accommodation_required').checked;

      const payload = {
        budget,
        guests,
        event_type,
        venue_preference,
        location,
        food_preference,
        decoration_style,
        entertainment_preference,
        accommodation_required
      };

      showLoading('PocketSmart AI is optimizing event budget & guest packages...');

      try {
        const res = await fetch('/generate-party', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        hideLoading();

        if (res.ok && data.id) {
          showToast('Event plan generated!');
          window.location.href = `/results/${data.id}`;
        } else {
          showToast(data.detail || 'Failed to generate party plan.', 'error');
        }
      } catch (err) {
        hideLoading();
        showToast('Error connecting to server.', 'error');
      }
    });
  }

  // Jewelry Planner Form (Supports Outfit Image Upload)
  const jewelryForm = document.getElementById('jewelry-planner-form');
  if (jewelryForm) {
    jewelryForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(jewelryForm);

      showLoading('PocketSmart AI is analyzing your outfit tone and jewelry budget...');

      try {
        const res = await fetch('/generate-jewelry', {
          method: 'POST',
          body: formData
        });

        const data = await res.json();
        hideLoading();

        if (res.ok && data.id) {
          showToast('Jewelry recommendations generated!');
          window.location.href = `/results/${data.id}`;
        } else {
          showToast(data.detail || 'Failed to generate jewelry plan.', 'error');
        }
      } catch (err) {
        hideLoading();
        showToast('Error connecting to server.', 'error');
      }
    });
  }
}

/* Save Plan Toggle Function */
async function toggleSavePlan(recId) {
  try {
    const res = await fetch(`/recommendations/${recId}/save`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message);
      const btn = document.getElementById(`save-btn-${recId}`);
      if (btn) {
        btn.textContent = data.is_saved ? '❤️ Saved' : '🤍 Save Recommendation';
        btn.className = data.is_saved ? 'btn btn-secondary' : 'btn btn-primary';
      }
    } else {
      showToast(data.detail || 'Could not save plan.', 'error');
    }
  } catch (err) {
    showToast('Network error.', 'error');
  }
}

/* Delete Plan Function */
async function deletePlan(recId) {
  if (!confirm('Are you sure you want to delete this recommendation plan?')) return;

  try {
    const res = await fetch(`/recommendations/${recId}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok) {
      showToast('Plan deleted.');
      const row = document.getElementById(`history-card-${recId}`);
      if (row) row.remove();
      else window.location.reload();
    } else {
      showToast(data.detail || 'Could not delete plan.', 'error');
    }
  } catch (err) {
    showToast('Network error.', 'error');
  }
}
