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
    width: 100px; /* Fixed width */
    text-align: center; /* Center the text inside the button */
`;


let lastClickedButton = null;


function createButton() {
    const button = document.createElement('button');
    button.textContent = 'Video';
    button.id = 'send-to-premiere-button';
    button.style.cssText = buttonStyles;
    button.setAttribute('role', 'button');
    button.setAttribute('aria-label', 'Send to Premiere Pro');
    button.onclick = sendURL;
    button.onmouseenter = (event) => event.target.style.backgroundColor = '#1E1E59';
    button.onmouseleave = (event) => event.target.style.backgroundColor = '#00005B';
    button.addEventListener('click', () => {
      button.disabled = true;
    });
  
    socket.on('download-complete', () => {
      button.disabled = false;
    });
  
    return button;
  }
  
let currentVideoUrl = '';  // Add this line to keep track of the current video URL
let lastUrl = window.location.href;  // Store the current URL

console.log(document.querySelector('#top-level-buttons-computed'));
const topLevelButtons = document.querySelector('#top-level-buttons-computed');
console.log(topLevelButtons);  

let isRequestInProgress = false; // Global flag to check if a request is in progress

function sendClipRequest() {
    const button = document.getElementById('clip-button');
    if (!button) return;

    const videoPlayer = document.querySelector('video');
    if (videoPlayer) {
        const currentTime = videoPlayer.currentTime;
        sendURL('clip', { currentTime: currentTime });  // Pass currentTime in an object
        button.innerText = 'Processing';
    } else {
        console.error('No video player found.');
    }
}

function handleError(error, button) {
    console.error('Error:', error);
    button.textContent = 'Error';
  }
  

  function sendURL(downloadType, additionalData = {}) {
    const buttonId = downloadType === 'full' ? 'send-to-premiere-button' : 'clip-button';
    console.log("sendURL called with downloadType:", downloadType, "and URL:", currentVideoUrl);
  
    if (isRequestInProgress) {
      console.log("Request already in progress. Please wait.");
      return;
    }
  
    isRequestInProgress = true;
    const button = document.getElementById(buttonId);
    if (!button) {
      console.error("Button not found:", buttonId);
      isRequestInProgress = false;
      return;
    }
  
    button.innerText = 'Loading';
    const videoId = new URLSearchParams(window.location.search).get('v');
  
    if (videoId) {
      currentVideoUrl = `https://www.youtube.com/watch?v=${videoId}`;
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
      .catch(error => handleError(error, button)) // Pass the button element here
      .finally(() => {
          isRequestInProgress = false;
      });
    } else {
      console.error('No video URL found.');
      handleError('No video URL found.', button) // Pass the button element here
      isRequestInProgress = false;
    }
  }



function handleResponse(response, buttonId) {
    if (!response.ok) {
        throw new Error('Network response was not ok: ' + response.statusText);
    }
    response.text().then(data => {
        console.log('Success:', data);
        const button = document.getElementById(buttonId);
        button.innerText = buttonId === 'send-to-premiere-button' ? 'Video' : 'Clip';  // Reset the button text
    }).catch(error => handleError(error, buttonId));
}



// Example usage:
// sendURL('full'); // For Video download
// sendURL('clip'); // For clip segment download



function isVideoPage() {
    return window.location.href.includes('/watch?v=');
}

function createClipButton() {
  const button = document.createElement('button');
  button.textContent = 'Clip';
  button.id = 'clip-button';
  button.style.cssText = buttonStyles;
  button.onclick = sendClipRequest;
  button.onmouseenter = () => button.style.backgroundColor = '#2E2E5F';
  button.onmouseleave = () => button.style.backgroundColor = '#00005B';
  button.onclick = sendClipRequest; // This should only call sendClipRequest
  return button;
}



function sendCurrentTimeToServer(timeSettings) {
    fetch('http://localhost:3001/current-time', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(timeSettings),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server responded with error status: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Error from server:', data.error);
        } else {
            console.log('Timecode sent successfully:', data);
        }
        document.getElementById('clip-button').innerText = 'Clip';  // Reset button text after processing
    })
    .catch(error => {
        console.error('Error sending current time:', error);
        document.getElementById('clip-button').innerText = 'Clip';  // Reset button text in case of error
    });
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
    let button;
    if (lastClickedButton === 'premiere') {
        button = document.getElementById('send-to-premiere-button');
    } else if (lastClickedButton === 'clip') {
        button = document.getElementById('clip-button');
    }

    if (button) {
        button.innerText = `${data.percentage}`;
    }
});



socket.on('download-complete', () => {
    const button = document.getElementById('send-to-premiere-button');
    if (button) {
        button.innerText = 'Video';  // Reset the button text
    }
});

socket.on('download-complete', () => {
    const clipButton = document.getElementById('clip-button');
    if (clipButton) {
        clipButton.innerText = 'Clip';  // Reset the button text
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
    const videoId = new URLSearchParams(window.location.search).get('v');
    if (videoId) {
        currentVideoUrl = `https://www.youtube.com/watch?v=${videoId}`;
        console.log('Updated video URL:', currentVideoUrl);
    }
}

// Add this call in the checkUrlChange function
function checkUrlChange() {
    if (lastUrl !== window.location.href) {
        lastUrl = window.location.href;
        updateVideoUrl(); 
        addPremiereButton();  // Ensure the button is added on URL change
    }
}
updateVideoUrl();
// Function to check for URL changes every 500 milliseconds (replaces previous setInterval call)
setInterval(checkUrlChange, 500);

// Function to create the Premiere Pro button
function createPremiereProButton() {
    let button = document.getElementById('send-to-premiere-button');
    if (!button) {
        button = document.createElement('button');
        button.innerText = 'Video';
        button.id = 'send-to-premiere-button';
        button.style.cssText = buttonStyles;
        button.onmouseenter = () => button.style.backgroundColor = '#1E1E59';
        button.onmouseleave = () => button.style.backgroundColor = '#00005B';
    }
    // Only assign onclick event if it hasn't been assigned before
    if (!button.onclick) {
        button.onclick = () => {
            console.log("Premiere Pro button clicked");
            lastClickedButton = 'premiere';
            sendURL('full');
        };
    }
    return button;
}

// Function to create the Clip button
function createClipButton() {
    let button = document.getElementById('clip-button');
    if (!button) {
        button = document.createElement('button');
        button.innerText = 'Clip';
        button.id = 'clip-button';
        button.style.cssText = buttonStyles;
        button.onmouseenter = () => button.style.backgroundColor = '#2E2E5F';
        button.onmouseleave = () => button.style.backgroundColor = '#00005B';
    }
    // Only assign onclick event if it hasn't been assigned before
    if (!button.onclick) {
        button.onclick = () => {
            console.log("Clip button clicked");
            lastClickedButton = 'clip';
            sendClipRequest();
        };
    }
    return button;
}

// Modified function to add the 'Premiere Pro' button
function addPremiereButton() {
    if (!document.getElementById('send-to-premiere-button')) {
        const ownerContainer = document.querySelector('#owner');
        if (ownerContainer) {
            const premiereButton = createPremiereProButton();
            ownerContainer.appendChild(premiereButton);
            console.log('Premiere button added.');
        } else {
            console.log('Owner container not found, retrying...');
            setTimeout(addPremiereButton, 1000);
        }
    }
}

// Modified function to add the 'Clip' button
function addClipButton() {
    if (!document.getElementById('clip-button')) {
        const ownerContainer = document.querySelector('#owner');
        if (ownerContainer) {
            const clipButton = createClipButton();
            ownerContainer.appendChild(clipButton);
            console.log('Clip button added.');
        } else {
            console.log('Owner container not found, retrying...');
            setTimeout(addClipButton, 1000);
        }
    }
}

// Initial call to add the button if the page is already loaded
addPremiereButton();
addClipButton();

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