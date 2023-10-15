

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

// Function to send the video URL to your server
function sendURL() {
    const videoUrlElement = document.querySelector('link[rel="canonical"]');
    if (videoUrlElement) {
        const videoUrl = videoUrlElement.href;
        const serverUrl = 'http://localhost:3000/handle-video-url';  // Updated to your local server

        fetch(serverUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ videoUrl }),  // Sends the video URL in the request body
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
            setTimeout(tryModifyMenu, 100);
        }
    }
}
const socket = io('http://localhost:3000');  // establish a WebSocket connection to the server

socket.on('percentage', (data) => {  
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


function addPremiereButton() {
    if (isVideoPage()) {  // Check if it's a video page before proceeding
        const topLevelButtons = document.querySelector('#top-level-buttons-computed');
        if (topLevelButtons) {
            const shareButton = topLevelButtons.querySelector('ytd-button-renderer[button-next]');
            if (shareButton) {
                const premiereButton = createButton();
                shareButton.parentNode.insertBefore(premiereButton, shareButton.nextSibling);
                observer.disconnect();  // Stop observing once the button has been added
            }
        }
    }
}

// Start the first attempt to modify the menu
tryModifyMenu();

// Start observing the document
const observer = new MutationObserver(addPremiereButton);

// Start observing the document with the configured parameters
observer.observe(document.body, { childList: true, subtree: true });

// Initially try to add the button
addPremiereButton();
