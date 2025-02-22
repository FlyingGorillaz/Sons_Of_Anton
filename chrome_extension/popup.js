const playPauseButton = document.getElementById("playPause");
const playPauseIcon = document.getElementById("playPauseIcon");
const extractButton = document.getElementById("extract");
const styleSelect = document.getElementById("styleSelect");
const stopButton = document.getElementById("stop");
const restartButton = document.getElementById("restart");

// Add ripple effect to buttons
const addRippleEffect = (button) => {
    button.addEventListener('click', function(e) {
        const ripple = document.createElement('div');
        ripple.classList.add('ripple');
        this.appendChild(ripple);
        
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size/2;
        const y = e.clientY - rect.top - size/2;
        
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        setTimeout(() => ripple.remove(), 600);
    });
};

// Add ripple effect to buttons
addRippleEffect(extractButton);
addRippleEffect(playPauseButton);
addRippleEffect(stopButton);
addRippleEffect(restartButton);

// Initialize button states
stopButton.hidden = true;
restartButton.hidden = true;

// Load previously selected style with smooth transition
chrome.storage.local.get(['selectedStyle'], (result) => {
    if (result.selectedStyle) {
        styleSelect.style.transition = 'none';
        styleSelect.value = result.selectedStyle;
        // Force a reflow
        styleSelect.offsetHeight;
        styleSelect.style.transition = '';
    }
});

// Save selected style with visual feedback
styleSelect.addEventListener('change', (e) => {
    chrome.storage.local.set({ 'selectedStyle': e.target.value });
    styleSelect.style.transform = 'scale(1.05)';
    setTimeout(() => {
        styleSelect.style.transform = 'scale(1)';
    }, 200);
});

const updateUI = (state) => {
    const setButtonState = (button, config) => {
        Object.entries(config).forEach(([key, value]) => {
            if (key === 'innerHTML') {
                button.innerHTML = value;
            } else {
                button.style[key] = value;
            }
        });
    };

    if (state === "loading") {
        extractButton.hidden = true;
        playPauseButton.hidden = false;
        playPauseButton.disabled = true;
        stopButton.hidden = false;
        restartButton.hidden = true;
        setButtonState(playPauseButton, {
            backgroundColor: '#4a4a4a',
            opacity: '0.8',
            innerHTML: `<i class="fas fa-spinner fa-spin icon"></i> Processing`
        });
        styleSelect.disabled = true;
    } else if (state === "playing") {
        playPauseButton.disabled = false;
        setButtonState(playPauseButton, {
            background: 'linear-gradient(135deg, #d4af37 0%, #f9d77e 100%)',
            opacity: '1',
            innerHTML: `<i class="fas fa-pause icon"></i> Pause`
        });
        extractButton.hidden = true;
        playPauseButton.hidden = false;
        stopButton.hidden = false;
        restartButton.hidden = false;
    } else if (state === "paused") {
        playPauseButton.disabled = false;
        setButtonState(playPauseButton, {
            background: 'linear-gradient(135deg, #d4af37 0%, #f9d77e 100%)',
            opacity: '1',
            innerHTML: `<i class="fas fa-play icon"></i> Resume`
        });
        extractButton.hidden = true;
        playPauseButton.hidden = false;
        stopButton.hidden = false;
        restartButton.hidden = false;
    } else if (state === "stopped") {
        extractButton.hidden = false;
        playPauseButton.hidden = true;
        stopButton.hidden = true;
        restartButton.hidden = true;
        styleSelect.disabled = false;
    } else if (state === "needsInteraction") {
        playPauseButton.disabled = false;
        setButtonState(playPauseButton, {
            background: 'linear-gradient(135deg, #d4af37 0%, #f9d77e 100%)',
            opacity: '1',
            innerHTML: `<i class="fas fa-play icon"></i> Start`
        });
        extractButton.hidden = true;
        playPauseButton.hidden = false;
        stopButton.hidden = false;
        restartButton.hidden = false;
    } else if (state === "error") {
        extractButton.hidden = false;
        playPauseButton.hidden = true;
        styleSelect.disabled = false;
        setButtonState(extractButton, {
            background: 'linear-gradient(135deg, #8b0000 0%, #a83232 100%)',
            innerHTML: `<i class="fas fa-redo icon"></i> Try Again`
        });
    } else {
        extractButton.hidden = false;
        playPauseButton.hidden = true;
        stopButton.hidden = true;
        restartButton.hidden = true;
        styleSelect.disabled = false;
        setButtonState(extractButton, {
            background: 'linear-gradient(135deg, #d4af37 0%, #f9d77e 100%)',
            innerHTML: `<i class="fas fa-headphones icon"></i> Listen Now`
        });
    }
};

// Send message to content script
const sendMessage = (action) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, { action });
        }
    });
};

// Extract button click handler
extractButton.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        const activeTabId = activeTab.id;
        
        // Check if the URL is valid for content script injection
        if (activeTab.url.startsWith('chrome://') || 
            activeTab.url.startsWith('edge://') || 
            activeTab.url.startsWith('about:')) {
            alert('This extension cannot run on browser system pages.');
            return;
        }

        chrome.storage.local.set({ activeTabId, isLoading: true });
        updateUI("loading");

        chrome.scripting.executeScript({
            target: { tabId: activeTabId },
            files: ["content.js"],
        });
    });
});

// Play/Pause button click handler
playPauseButton.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.tabs.sendMessage(tabs[0].id, { action: "toggleAudio" }, (response) => {
            const isPlaying = response?.isPlaying || false;
            chrome.storage.local.set({ isPlaying, isLoading: false });
            updateUI(isPlaying ? "playing" : "paused");
        });
    });
});

// Stop button click handler
stopButton.addEventListener('click', () => {
    sendMessage("stopAudio");
    updateUI("stopped");
});

// Restart button click handler
restartButton.addEventListener('click', () => {
    sendMessage("restartAudio");
    updateUI("playing");
});

// Check the state when the popup is opened
chrome.storage.local.get(["isPlaying", "isLoading", "activeTabId"], (result) => {
    const isPlaying = result.isPlaying || false;
    const isLoading = result.isLoading || false;

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTabId = tabs[0].id;
        const isActiveTab = currentTabId === result.activeTabId;

        if (isLoading && isActiveTab) {
            updateUI("loading");
        } else if (isPlaying && isActiveTab) {
            updateUI("playing");
        } else {
            updateUI();
        }
    });
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "audioStarted") {
        chrome.storage.local.set({ isPlaying: true, isLoading: false });
        updateUI("playing");
    } else if (message.action === "audioCompleted") {
        chrome.storage.local.set({ isPlaying: false, isLoading: false });
        updateUI("stopped");
    } else if (message.action === "audioPaused") {
        chrome.storage.local.set({ isPlaying: false, isLoading: false });
        updateUI("paused");
    } else if (message.action === "audioNeedsUserInteraction") {
        chrome.storage.local.set({ isPlaying: false, isLoading: false });
        updateUI("needsInteraction");
    } else if (message.action === "audioError") {
        chrome.storage.local.set({ isPlaying: false, isLoading: false });
        alert(message.error);
        updateUI("error");
    }
});
