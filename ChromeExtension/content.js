const buttonStyles = `
    padding: 9px 18px;
    font-family: "Roboto","Arial",sans-serif;
    font-size: 14px;
    font-weight: 500;
    border: none;
    background-color: #00005B;
    color: #9999FF;
    border-radius: 18px;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease;
    margin-left: 5px;
    width: 100px;
    text-align: center;
`;

let lastClickedButton = null;
let currentVideoUrl = '';
let lastUrl = window.location.href;
let isRequestInProgress = false;

// Socket.IO connection
const socket = io.connect('http://localhost:3001');

// Handle percentage updates
socket.on('percentage', (data) => {
    let button;
    if (lastClickedButton === 'premiere') {
        button = document.getElementById('send-to-premiere-button');
    } else if (lastClickedButton === 'clip') {
        button = document.getElementById('clip-button');
    } else if (lastClickedButton === 'audio') {
        button = document.getElementById('audio-button');
    }
    if (button) {
        button.innerText = `${data.percentage}`;
    }
});

// Handle download complete events
socket.on('download-complete', () => {
    const premiereButton = document.getElementById('send-to-premiere-button');
    const clipButton = document.getElementById('clip-button');
    const audioButton = document.getElementById('audio-button');
    if (premiereButton) premiereButton.innerText = 'Video';
    if (clipButton) clipButton.innerText = 'Clip';
    if (audioButton) audioButton.innerText = 'Audio';
});

// Log socket connection events
socket.on('connect', () => console.log('Connected to server'));
socket.on('disconnect', () => console.log('Disconnected from server'));

// Update video URL based on current window location
function updateVideoUrl() {
    const videoId = new URLSearchParams(window.location.search).get('v');
    if (videoId) {
        currentVideoUrl = `https://www.youtube.com/watch?v=${videoId}`;
        console.log('Updated video URL:', currentVideoUrl);
    }
}

// Check for URL changes
function checkUrlChange() {
    if (lastUrl !== window.location.href) {
        lastUrl = window.location.href;
        updateVideoUrl();
        addPremiereButton();
        addClipButton();
        addAudioButton();
    }
}

// Handle errors and reset button text
function handleError(error, button) {
    console.error('Error:', error);
    button.textContent = 'Error';
    isRequestInProgress = false;
}

// Handle server responses
function handleResponse(response, buttonId) {
    if (!response.ok) {
        throw new Error('Network response was not ok: ' + response.statusText);
    }
    response.text().then(data => {
        console.log('Success:', data);
        document.getElementById(buttonId).innerText = buttonId === 'send-to-premiere-button' ? 'Video' : buttonId === 'clip-button' ? 'Clip' : 'Audio';
    }).catch(error => handleError(error, document.getElementById(buttonId)));
}

// Send URL to the server
function sendURL(downloadType, additionalData = {}) {
    if (isRequestInProgress) {
        console.log("Request already in progress. Please wait.");
        return;
    }

    isRequestInProgress = true;
    const buttonId = downloadType === 'full' ? 'send-to-premiere-button' : downloadType === 'clip' ? 'clip-button' : 'audio-button';
    const button = document.getElementById(buttonId);

    if (!button) {
        console.error("Button not found:", buttonId);
        isRequestInProgress = false;
        return;
    }

    button.innerText = 'Loading';
    const videoId = new URLSearchParams(window.location.search).get('v');

    if (videoId) {
        currentVideoUrl = `https://youtu.be/${videoId}`;
        const serverUrl = 'http://localhost:3001/handle-video-url';
        const requestData = {
            videoUrl: currentVideoUrl,
            downloadType: downloadType,
            ...additionalData
        };

        fetch(serverUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(requestData),
        })
        .then(response => handleResponse(response, buttonId))
        .catch(error => handleError(error, button))
        .finally(() => {
            isRequestInProgress = false;
        });
    } else {
        console.error('No video URL found.');
        handleError('No video URL found.', button);
        isRequestInProgress = false;
    }
}

// Create a button with specified properties
function createButton(id, text, onClick, onMouseEnterColor) {
    const button = document.createElement('button');
    button.textContent = text;
    button.id = id;
    button.style.cssText = buttonStyles;
    button.setAttribute('role', 'button');
    button.setAttribute('aria-label', text);
    button.onclick = onClick;
    button.onmouseenter = () => button.style.backgroundColor = onMouseEnterColor;
    button.onmouseleave = () => button.style.backgroundColor = '#00005B';
    return button;
}

// Create the Premiere Pro button
function createPremiereProButton() {
    let button = document.getElementById('send-to-premiere-button');
    if (!button) {
        button = createButton('send-to-premiere-button', 'Video', () => {
            lastClickedButton = 'premiere';
            sendURL('full');
        }, '#1E1E59');
    }
    return button;
}

// Create the Clip button
function createClipButton() {
    let button = document.getElementById('clip-button');
    if (!button) {
        button = createButton('clip-button', 'Clip', () => {
            lastClickedButton = 'clip';
            sendClipRequest();
        }, '#2E2E5F');
    }
    return button;
}

// Create the Audio button
function createAudioButton() {
    let button = document.getElementById('audio-button');
    if (!button) {
        button = createButton('audio-button', 'Audio', () => {
            lastClickedButton = 'audio';
            sendURL('audio');
        }, '#3E3E6F');
    }
    return button;
}

// Add the Premiere Pro button to the page
function addPremiereButton() {
    if (!document.getElementById('send-to-premiere-button')) {
        const ownerContainer = document.querySelector('#owner');
        if (ownerContainer) {
            ownerContainer.appendChild(createPremiereProButton());
            console.log('Premiere button added.');
        } else {
            console.log('Owner container not found, retrying...');
            setTimeout(addPremiereButton, 1000);
        }
    }
}

// Add the Clip button to the page
function addClipButton() {
    if (!document.getElementById('clip-button')) {
        const ownerContainer = document.querySelector('#owner');
        if (ownerContainer) {
            ownerContainer.appendChild(createClipButton());
            console.log('Clip button added.');
        } else {
            console.log('Owner container not found, retrying...');
            setTimeout(addClipButton, 1000);
        }
    }
}

// Add the Audio button to the page
function addAudioButton() {
    if (!document.getElementById('audio-button')) {
        const ownerContainer = document.querySelector('#owner');
        if (ownerContainer) {
            ownerContainer.appendChild(createAudioButton());
            console.log('Audio button added.');
        } else {
            console.log('Owner container not found, retrying...');
            setTimeout(addAudioButton, 1000);
        }
    }
}

// Function to send clip request
function sendClipRequest() {
    const button = document.getElementById('clip-button');
    if (!button) return;

    const videoPlayer = document.querySelector('video');
    if (videoPlayer) {
        const currentTime = videoPlayer.currentTime;
        sendURL('clip', { currentTime: currentTime });
        button.innerText = 'Processing';
    } else {
        console.error('No video player found.');
    }
}

// Initial call to add buttons if the page is already loaded
addPremiereButton();
addClipButton();
addAudioButton();

// Check for URL changes every 500 milliseconds
setInterval(checkUrlChange, 500);

// Set up a MutationObserver to monitor for changes if the button isn't added yet
const observer = new MutationObserver(() => {
    addPremiereButton();
    addClipButton();
    addAudioButton();
});

// Start observing the document body for changes
observer.observe(document.body, { childList: true, subtree: true });
