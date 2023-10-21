// background.js
browser.runtime.onMessage.addListener((message) => {
    if(message.type === 'sendUrl') {
        const serverUrl = 'http://localhost:3001/handle-video-url';  // Updated to your local server
        fetch(serverUrl, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ videoUrl: message.videoUrl }),
            credentials: 'include'  // Include credentials if necessary
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });  // Throw an error with the response text
            }
            return response.json();  // Use json() if the response is in JSON
        })
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
});
