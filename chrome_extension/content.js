(() => {
    let audio = null;
    let isPlaying = false;
    let pendingAudioBlob = null;
    let currentAudioBlob = null;  // Store the current audio blob for restart functionality

    const playAudio = async (audioBlob) => {
        try {
            const audioUrl = URL.createObjectURL(audioBlob);
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
                audio.src = "";
                audio = null;
            }
            audio = new Audio(audioUrl);
            currentAudioBlob = audioBlob;  // Store the blob for restart
            
            // Set up event listeners
            audio.addEventListener("ended", () => {
                isPlaying = false;
                chrome.runtime.sendMessage({ action: "audioCompleted" });
            });
            
            audio.addEventListener("play", () => {
                isPlaying = true;
                chrome.runtime.sendMessage({ action: "audioStarted" });
            });

            audio.addEventListener("pause", () => {
                if (!audio.ended) {  // Only send pause event if not ended
                    chrome.runtime.sendMessage({ action: "audioPaused" });
                }
            });

            audio.addEventListener("error", (e) => {
                console.error("Audio playback error:", e);
                chrome.runtime.sendMessage({ 
                    action: "audioError",
                    error: "Failed to play audio. Please try again."
                });
            });

            try {
                await audio.play();
            } catch (error) {
                if (error.name === "NotAllowedError") {
                    // Store the blob for later playback
                    pendingAudioBlob = audioBlob;
                    chrome.runtime.sendMessage({ 
                        action: "audioNeedsUserInteraction",
                        message: "Click the play button to start audio"
                    });
                } else {
                    throw error;
                }
            }
        } catch (error) {
            console.error("Error in playAudio:", error);
            chrome.runtime.sendMessage({ 
                action: "audioError",
                error: error.message
            });
        }
    };

    const stopAudio = () => {
        if (audio) {
            audio.pause();
            audio.currentTime = 0;
            audio.src = "";
            audio = null;
            isPlaying = false;
            pendingAudioBlob = null;
            // Don't clear currentAudioBlob in case we want to restart
        }
    };

    const restartAudio = async () => {
        if (currentAudioBlob) {
            if (audio) {
                audio.pause();
                audio.currentTime = 0;
            }
            await playAudio(currentAudioBlob);
        }
    };

    const toggleAudioPlayback = async () => {
        try {
            if (pendingAudioBlob) {
                // Try to play the pending audio
                await playAudio(pendingAudioBlob);
                pendingAudioBlob = null;
                return true;
            }
            
            if (audio) {
                if (audio.paused) {
                    await audio.play();
                    isPlaying = true;
                } else {
                    audio.pause();
                    isPlaying = false;
                }
            } else {
                console.log("No audio loaded yet.");
            }
            return isPlaying;
        } catch (error) {
            console.error("Error in toggleAudioPlayback:", error);
            return false;
        }
    };

    const pageUrl = window.location.href;

    // Get the selected style from chrome storage
    chrome.storage.local.get(['selectedStyle'], (result) => {
        const style = result.selectedStyle || 'RAP';  // Default to RAP if not set
        
        fetch("http://localhost:8000/api/data", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "audio/mpeg, application/json"
            },
            body: JSON.stringify({ 
                url: pageUrl,
                style: style
            }),
        })
        .then((response) => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`API error: ${response.status} ${response.statusText}\n${text}`);
                });
            }
            return response.blob();
        })
        .then((audioBlob) => {
            playAudio(audioBlob);
        })
        .catch((error) => {
            console.error("API error:", error);
            chrome.runtime.sendMessage({ 
                action: "audioError",
                error: error.message
            });
        });
    });

    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === "toggleAudio") {
            toggleAudioPlayback().then(currentPlayingState => {
                sendResponse({ isPlaying: currentPlayingState });
            });
            return true; // Keep the message channel open for the async response
        } else if (message.action === "stopAudio") {
            stopAudio();
            sendResponse({ stopped: true });
        } else if (message.action === "restartAudio") {
            restartAudio().then(() => {
                sendResponse({ restarted: true });
            });
            return true; // Keep the message channel open for the async response
        }
    });
})();
