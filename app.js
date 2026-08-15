/**
 * app.js - Executive Intelligence Hub PWA Client Logic
 * Designed for Nishant Agarwal
 */

// Application State
const state = {
  briefing: null,
  activeCategory: 'ALL',
  bookmarks: JSON.parse(localStorage.getItem('exec_bookmarks') || '[]'),
  audio: {
    isPlaying: false,
    currentIndex: 0,
    speed: 1.0,
    playlist: [],
    utterance: null
  },
  theme: localStorage.getItem('exec_theme') || 'dark'
};

// DOM Elements
const elements = {
  briefingDate: document.getElementById('briefingDate'),
  macroList: document.getElementById('macroList'),
  cardsFeed: document.getElementById('cardsFeed'),
  categoryNav: document.getElementById('categoryNav'),
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  refreshLiveBtn: document.getElementById('refreshLiveBtn'),
  listenAllBtn: document.getElementById('listenAllBtn'),
  
  // Audio Player Elements
  audioPlayerBar: document.getElementById('audioPlayerBar'),
  audioBadge: document.getElementById('audioBadge'),
  audioTitle: document.getElementById('audioTitle'),
  audioSpeedBtn: document.getElementById('audioSpeedBtn'),
  audioPlayPauseBtn: document.getElementById('audioPlayPauseBtn'),
  playIcon: document.getElementById('playIcon'),
  pauseIcon: document.getElementById('pauseIcon'),
  audioNextBtn: document.getElementById('audioNextBtn'),
  audioProgressBar: document.getElementById('audioProgressBar'),
  
  // Modal Elements
  linkedInModal: document.getElementById('linkedInModal'),
  modalHeadline: document.getElementById('modalHeadline'),
  linkedInPostText: document.getElementById('linkedInPostText'),
  closeModalBtn: document.getElementById('closeModalBtn'),
  copyPostBtn: document.getElementById('copyPostBtn'),
  toastNotification: document.getElementById('toastNotification')
};

// Initialize Application
async function initApp() {
  setupTheme();
  setupEventListeners();
  await loadBriefingData();
  setupHabitChecklist();
  registerServiceWorker();
}

// Setup Theme
function setupTheme() {
  if (state.theme === 'light') {
    document.body.classList.add('light-theme');
    document.body.classList.remove('dark-theme');
  } else {
    document.body.classList.add('dark-theme');
    document.body.classList.remove('light-theme');
  }
}

// Load Briefing Data (Local JSON / Backend API / Cache)
async function loadBriefingData() {
  elements.cardsFeed.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Loading 08:30 AM Sector Intelligence & Regulatory Scans...</p>
    </div>
  `;

  try {
    // Try fetching static daily JSON (GitHub Pages or local static root)
    let response = await fetch('./data/briefing_today.json?v=' + Date.now());
    
    // Fallback to API if static JSON not found
    if (!response.ok) {
      response = await fetch('/api/briefing/today');
    }

    if (response.ok) {
      state.briefing = await response.json();
      localStorage.setItem('exec_briefing_today', JSON.stringify(state.briefing));
    } else {
      throw new Error('Failed to fetch from static data and API');
    }
  } catch (err) {
    console.warn('Network fetch failed, checking local cache:', err);
    const cached = localStorage.getItem('exec_briefing_today');
    if (cached) {
      state.briefing = JSON.parse(cached);
    } else {
      state.briefing = getEmergencyFallbackData();
    }
  }

  renderBriefing();
}

// Render Header, Macro Signals, and Cards
function renderBriefing() {
  if (!state.briefing) return;

  // Header meta
  elements.briefingDate.textContent = `${state.briefing.date} • ${state.briefing.generated_at}`;

  // Macro Signals Hero
  const macroItems = state.briefing.top_macro_signals || [];
  elements.macroList.innerHTML = macroItems
    .map(signal => `<li>${signal}</li>`)
    .join('');

  // Prepare Audio Playlist
  state.audio.playlist = [];
  // Add intro macro narration
  state.audio.playlist.push({
    title: `08:30 AM Executive Macro Briefing`,
    text: `Good morning Nishant. Here is your 8-minute executive intelligence scan for ${state.briefing.date}. Top macro signals: ${macroItems.join('. ')}`
  });

  // Add individual cards
  (state.briefing.briefing_cards || []).forEach(card => {
    state.audio.playlist.push({
      title: card.headline,
      text: card.audio_text || `${card.headline}. ${card.summary}. Strategic P&L Impact: ${card.pl_impact}`
    });
  });

  renderCards();
}

// Render Briefing Cards based on active category
function renderCards() {
  const cards = state.briefing.briefing_cards || [];
  let filtered = [];

  if (state.activeCategory === 'ALL') {
    filtered = cards;
  } else if (state.activeCategory === 'BOOKMARKS') {
    filtered = cards.filter(c => state.bookmarks.includes(c.id));
  } else {
    filtered = cards.filter(c => c.category === state.activeCategory);
  }

  if (filtered.length === 0) {
    elements.cardsFeed.innerHTML = `
      <div class="loading-state">
        <p>No signals found in this category.</p>
      </div>
    `;
    return;
  }

  elements.cardsFeed.innerHTML = filtered.map(card => {
    const isBookmarked = state.bookmarks.includes(card.id);
    const badgeClass = getBadgeClass(card.category);

    return `
      <article class="brief-card" id="${card.id}">
        <div class="card-top">
          <span class="card-category-badge ${badgeClass}">${card.category}</span>
          <span class="card-source-tag">${card.source}</span>
        </div>

        <h3 class="card-headline">${card.headline}</h3>
        <p class="card-summary">${card.summary}</p>

        <div class="pl-impact-box">
          <div class="pl-impact-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>
            P&L & Strategic Growth Impact
          </div>
          <p class="pl-impact-text">${card.pl_impact}</p>
        </div>

        <div class="card-actions">
          <div class="action-left">
            <button class="action-btn btn-linkedin-angle" onclick="openLinkedInAngle('${card.id}')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.2V10.9H6.46M7.83 6.64c-.88 0-1.6.72-1.6 1.6 0 .88.72 1.6 1.6 1.6.88 0 1.6-.72 1.6-1.6 0-.88-.72-1.6-1.6-1.6Z"></path></svg>
              LinkedIn Angle
            </button>
            <a href="${card.url}" target="_blank" rel="noopener" class="action-btn">
              Source ↗
            </a>
          </div>
          <button class="action-btn" onclick="toggleBookmark('${card.id}')" title="Bookmark">
            ${isBookmarked ? '⭐ Saved' : '☆ Save'}
          </button>
        </div>
      </article>
    `;
  }).join('');
}

function getBadgeClass(category) {
  if (category.includes('RBI') || category.includes('SEBI') || category.includes('Regulatory')) return 'badge-reg';
  if (category.includes('FinTech') || category.includes('WealthTech')) return 'badge-fin';
  if (category.includes('MTF') || category.includes('Capital Markets')) return 'badge-mkt';
  return 'badge-lend';
}

// Bookmark Toggle
window.toggleBookmark = function(cardId) {
  if (state.bookmarks.includes(cardId)) {
    state.bookmarks = state.bookmarks.filter(id => id !== cardId);
    showToast('Removed from bookmarks');
  } else {
    state.bookmarks.push(cardId);
    showToast('Saved to bookmarks ⭐');
  }
  localStorage.setItem('exec_bookmarks', JSON.stringify(state.bookmarks));
  renderCards();
};

// LinkedIn Thought-Leadership Hook Modal
window.openLinkedInAngle = function(cardId) {
  const card = (state.briefing.briefing_cards || []).find(c => c.id === cardId);
  if (!card) return;

  elements.modalHeadline.textContent = card.headline;

  const postDraft = `🚀 Strategic Lens on Indian BFSI & FinTech: ${card.headline}

In scaling digital businesses and retail distribution models, regulatory shifts and market changes aren't roadblocks—they are unit-economics moats for agile teams.

Key Development:
${card.summary}

The Commercial & P&L Reality:
${card.pl_impact}

Executive Takeaway:
${card.action_trigger}

For digital leaders and platforms, the playbook is clear: optimize turnaround time, eliminate onboarding friction, and build automated self-service rails before margin compression forces your hand.

How is your organization adapting to this shift?

#FinTech #BFSI #DigitalLending #WealthTech #Growth #Leadership #Strategy`;

  elements.linkedInPostText.value = postDraft;
  elements.linkedInModal.classList.remove('hidden');
};

// Text-to-Speech (TTS) Audio Engine
function setupAudioPlayer() {
  if (!('speechSynthesis' in window)) {
    elements.audioBadge.textContent = 'TTS Not Supported';
    return;
  }

  elements.audioPlayPauseBtn.addEventListener('click', toggleAudioPlayPause);
  elements.listenAllBtn.addEventListener('click', () => {
    state.audio.currentIndex = 0;
    playCurrentAudioTrack();
  });
  elements.audioNextBtn.addEventListener('click', playNextAudioTrack);
  elements.audioSpeedBtn.addEventListener('click', cycleAudioSpeed);
}

function toggleAudioPlayPause() {
  if (state.audio.isPlaying) {
    window.speechSynthesis.pause();
    state.audio.isPlaying = false;
    updateAudioUI(false);
  } else {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      state.audio.isPlaying = true;
      updateAudioUI(true);
    } else {
      playCurrentAudioTrack();
    }
  }
}

function playCurrentAudioTrack() {
  window.speechSynthesis.cancel();

  if (state.audio.playlist.length === 0) return;
  const track = state.audio.playlist[state.audio.currentIndex];
  if (!track) return;

  state.audio.utterance = new SpeechSynthesisUtterance(track.text);
  state.audio.utterance.rate = state.audio.speed;
  state.audio.utterance.pitch = 1.0;

  // Prefer natural English voice
  const voices = window.speechSynthesis.getVoices();
  const naturalVoice = voices.find(v => (v.lang.includes('en-IN') || v.lang.includes('en-GB') || v.lang.includes('en-US')) && v.name.includes('Natural')) || voices[0];
  if (naturalVoice) state.audio.utterance.voice = naturalVoice;

  state.audio.utterance.onstart = () => {
    state.audio.isPlaying = true;
    updateAudioUI(true);
    elements.audioTitle.textContent = track.title;
    elements.audioBadge.textContent = `Playing ${state.audio.currentIndex + 1}/${state.audio.playlist.length}`;
  };

  state.audio.utterance.onend = () => {
    if (state.audio.currentIndex < state.audio.playlist.length - 1) {
      state.audio.currentIndex++;
      playCurrentAudioTrack();
    } else {
      state.audio.isPlaying = false;
      updateAudioUI(false);
      elements.audioBadge.textContent = 'Completed';
      elements.audioProgressBar.style.width = '100%';
    }
  };

  state.audio.utterance.onerror = () => {
    state.audio.isPlaying = false;
    updateAudioUI(false);
  };

  window.speechSynthesis.speak(state.audio.utterance);
  updateAudioProgress();
}

function playNextAudioTrack() {
  if (state.audio.currentIndex < state.audio.playlist.length - 1) {
    state.audio.currentIndex++;
    playCurrentAudioTrack();
  }
}

function cycleAudioSpeed() {
  if (state.audio.speed === 1.0) state.audio.speed = 1.25;
  else if (state.audio.speed === 1.25) state.audio.speed = 1.5;
  else state.audio.speed = 1.0;

  elements.audioSpeedBtn.textContent = `${state.audio.speed}x`;
  if (state.audio.isPlaying) {
    playCurrentAudioTrack();
  }
}

function updateAudioUI(isPlaying) {
  if (isPlaying) {
    elements.playIcon.classList.add('hidden');
    elements.pauseIcon.classList.remove('hidden');
  } else {
    elements.playIcon.classList.remove('hidden');
    elements.pauseIcon.classList.add('hidden');
  }
}

function updateAudioProgress() {
  const total = state.audio.playlist.length || 1;
  const current = state.audio.currentIndex;
  const pct = ((current + 1) / total) * 100;
  elements.audioProgressBar.style.width = `${pct}%`;
}

// Setup Event Listeners
function setupEventListeners() {
  // Category Pill Navigation
  elements.categoryNav.addEventListener('click', e => {
    if (e.target.classList.contains('cat-pill')) {
      document.querySelectorAll('.cat-pill').forEach(btn => btn.classList.remove('active'));
      e.target.classList.add('active');
      state.activeCategory = e.target.dataset.category;
      renderCards();
    }
  });

  // Theme Toggle
  elements.themeToggleBtn.addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('exec_theme', state.theme);
    setupTheme();
  });

  // Live Refresh
  elements.refreshLiveBtn.addEventListener('click', async () => {
    showToast('Refreshing sector intelligence...');
    elements.refreshLiveBtn.style.transform = 'rotate(360deg)';
    elements.refreshLiveBtn.style.transition = 'transform 0.8s ease';
    localStorage.removeItem('exec_briefing_today');
    setTimeout(() => {
      elements.refreshLiveBtn.style.transform = 'none';
    }, 800);
    await loadBriefingData();
    showToast('Intelligence feed updated! ⚡');
  });

  // LinkedIn Modal Close & Copy
  elements.closeModalBtn.addEventListener('click', () => {
    elements.linkedInModal.classList.add('hidden');
  });

  elements.linkedInModal.addEventListener('click', e => {
    if (e.target === elements.linkedInModal) {
      elements.linkedInModal.classList.add('hidden');
    }
  });

  elements.copyPostBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(elements.linkedInPostText.value);
    showToast('Post copied! Ready for LinkedIn 🚀');
    elements.linkedInModal.classList.add('hidden');
  });

  setupAudioPlayer();
}

// Habit Checklist Persistence
function setupHabitChecklist() {
  ['habit1', 'habit2', 'habit3'].forEach(id => {
    const checkbox = document.getElementById(id);
    if (!checkbox) return;
    const saved = localStorage.getItem(`exec_${id}_${new Date().toDateString()}`);
    if (saved !== null) {
      checkbox.checked = saved === 'true';
    }
    checkbox.addEventListener('change', () => {
      localStorage.setItem(`exec_${id}_${new Date().toDateString()}`, checkbox.checked);
    });
  });
}

// Toast Helper
function showToast(msg) {
  elements.toastNotification.textContent = msg;
  elements.toastNotification.classList.remove('hidden');
  setTimeout(() => {
    elements.toastNotification.classList.add('hidden');
  }, 2400);
}

// Service Worker for Offline PWA
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./service-worker.js')
        .then(reg => console.log('PWA Service Worker registered:', reg.scope))
        .catch(err => console.log('Service Worker registration failed:', err));
    });
  }
}

// Fallback emergency data
function getEmergencyFallbackData() {
  return {
    date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
    generated_at: '08:30 AM IST',
    top_macro_signals: [
      "SEBI updates Margin Trading Facility (MTF) surveillance framework.",
      "RBI expands Account Aggregator (AA 2.0) to GST and tax rails for frictionless credit.",
      "WealthTech platforms accelerate cross-sell transition towards active advisory products."
    ],
    briefing_cards: [
      {
        id: "card-1",
        headline: "SEBI Updates Margin Trading Facility (MTF) & Surveillance Architecture",
        category: "Capital Markets & MTF",
        source: "SEBI Regulatory Update",
        url: "https://www.sebi.gov.in",
        summary: "SEBI issues updated guidance on collateral haircuts, intraday risk reporting, and capital allocation for retail MTF books.",
        pl_impact: "Direct tailwind for scaled brokerages with automated risk tech. Expands net interest margin (NIM) and MTF book size by up to 3.5×.",
        action_trigger: "Draft a LinkedIn analysis: 'The MTF Moat: Why Capital Markets Winners Win on Balance-Sheet Tech and Risk Automation.'",
        tags: ["SEBI", "MTF", "Capital Markets"],
        audio_text: "Good morning Nishant. Today's top capital markets signal: SEBI is refining the Margin Trading Facility framework."
      }
    ]
  };
}

// Start App
document.addEventListener('DOMContentLoaded', initApp);
