document.addEventListener('DOMContentLoaded', (event) => {
    // Load settings from Local Storage
    const settings = JSON.parse(localStorage.getItem('settings'));
    if (settings) {
        document.getElementById('resolution').value = settings.resolution || '1080p';
        document.getElementById('framerate').value = settings.framerate || '30';
        document.getElementById('download-path').value = settings.downloadPath || 'D:/youtube download';
    }
});

const button = document.getElementById('save-settings');
const message = document.getElementById('message');


button.addEventListener('click', () => {
    // Save settings to Local Storage
    const settings = {
        resolution: document.getElementById('resolution').value,
        framerate: document.getElementById('framerate').value,
        downloadPath: (document.getElementById('download-path').value),
    };
    sendSettingsToServer(settings);  // Send settings to the server

    startServer();  // Start the server if it's not already running

    localStorage.setItem('settings', JSON.stringify(settings));
    console.log('Settings saved');

    // Show the "Settings saved" message
    message.style.display = 'block';  // Show message
    setTimeout(() => {
        message.style.opacity = '1';
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';  // Hide message
            }, 500);
        }, 2000);  // Display for 2 seconds
    }, 10);
});


async function sendSettingsToServer(settings) {
    try {
        const response = await fetch('http://localhost:3001/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings),
        });

        const data = await response.json();
        console.log('Success:', data);
    } catch (error) {
        console.error('Error:', error);
    }
}