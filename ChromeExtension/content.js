// CSS for the button
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
`;

// Function to create the button
function createButton() {
    const button = document.createElement('button');
    button.innerText = 'Premiere Pro';
    button.id = 'send-to-premiere-button';
    button.style.cssText = buttonStyles;
    button.onclick = sendURL;
    button.onmouseenter = () => button.style.backgroundColor = '#1E1E59';
    button.onmouseleave = () => button.style.backgroundColor = '#00005B';
    return button;
}

let currentVideoUrl = '';  // Add this line to keep track of the current video URL
let lastUrl = window.location.href;  // Store the current URL

console.log(document.querySelector('#top-level-buttons-computed'));
const topLevelButtons = document.querySelector('#top-level-buttons-computed');
console.log(topLevelButtons);  

// Function to send the video URL to your server
function sendURL() {
    const videoId = new URLSearchParams(window.location.search).get('v');
    if (videoId) {
        const currentVideoUrl = `https://www.youtube.com/watch?v=${videoId}`;  // Construct the video URL
        const serverUrl = 'http://localhost:3001/handle-video-url';  // Updated to your local server

        fetch(serverUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ videoUrl: currentVideoUrl }),  // Sends the video URL in the request body
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.text();  // Use text() instead of json() if the response is plain text
        })
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });

    } else {
        console.error('No video URL found.');
    }
}


function isVideoPage() {
    return window.location.href.includes('/watch?v=');
}

function tryModifyMenu() {
    if (isVideoPage()) {  // Check if it's a video page before proceeding
        const topLevelButtons = document.querySelector('#top-level-buttons-computed');
        if (topLevelButtons && !document.getElementById('send-to-premiere-button')) {
            const premiereButton = createButton();
            const shareButton = topLevelButtons.querySelector('ytd-button-renderer[button-next]');
            if (shareButton) {
                shareButton.parentNode.insertBefore(premiereButton, shareButton.nextSibling);
            } else {
                console.error('Share button not found.');
            }
        } else {
            // If the top level buttons div isn't available yet, try again in a moment
            setTimeout(tryModifyMenu, 200);  // Increased delay to 1000 milliseconds (1 second)
        }
    }
}

const socket = io.connect('http://localhost:3001');


socket.on('percentage', (data) => {  
    console.log(data);  // Add this line
    const button = document.getElementById('send-to-premiere-button');
    if (button) {
        button.innerText = `Download ${data.percentage}`;  // update the button text
    }
});

socket.on('download-complete', () => {
    const button = document.getElementById('send-to-premiere-button');
    if (button) {
        button.innerText = 'Premiere Pro';  // reset the button text
    }
});
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});
// Function to update the video URL
function updateVideoUrl() {
    if (window.location.href.includes('/watch?v=')) {
        currentVideoUrl = window.location.href;
        console.log('Updated video URL:', currentVideoUrl);
    }
}


// Function to check for URL changes
function checkUrlChange() {
    if (lastUrl !== window.location.href) {
        lastUrl = window.location.href;
        updateVideoUrl();
        addPremiereButton();  // Ensure the button is added on URL change
    }
}

// Function to check for URL changes every 500 milliseconds (replaces previous setInterval call)
setInterval(checkUrlChange, 500);

function addPremiereButton() {
    const likeButton = document.querySelector('ytd-menu-renderer yt-icon-button#button');
    if (likeButton && !document.getElementById('send-to-premiere-button')) {
        const premiereButton = createButton();
        likeButton.parentNode.insertBefore(premiereButton, likeButton);
        console.log('Premiere button added.');
    }
}

// Initial call to add the button if the page is already loaded
addPremiereButton();

// Set up a MutationObserver to monitor for changes if the button isn't added yet
const observer = new MutationObserver((mutations, observer) => {
    for (const mutation of mutations) {
        if (mutation.type === 'childList' && mutation.addedNodes.length) {
            addPremiereButton();
        }
    }
});

// Start observing the document body for changes
observer.observe(document.body, { childList: true, subtree: true });
