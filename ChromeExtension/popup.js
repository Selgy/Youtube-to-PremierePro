document.addEventListener('DOMContentLoaded', () => {
    // Load settings from Local Storage
    const settings = JSON.parse(localStorage.getItem('settings')) || {
        resolution: '1080p',
        framerate: '30',
        downloadPath: '',
        downloadMP3: false
    };

    // Initialize settings
    document.getElementById('resolution').value = settings.resolution;
    document.getElementById('framerate').value = settings.framerate;
    document.getElementById('download-path').value = settings.downloadPath;
    document.getElementById('download-mp3').checked = settings.downloadMP3;

    // Event listeners for each setting
    document.getElementById('resolution').addEventListener('change', saveAndSendSettings);
    document.getElementById('framerate').addEventListener('change', saveAndSendSettings);
    document.getElementById('download-path').addEventListener('change', saveAndSendSettings);
    document.getElementById('download-mp3').addEventListener('change', saveAndSendSettings);
});

function saveAndSendSettings() {
    const settings = {
        resolution: document.getElementById('resolution').value,
        framerate: document.getElementById('framerate').value,
        downloadPath: document.getElementById('download-path').value,
        downloadMP3: document.getElementById('download-mp3').checked
    };

    // Save to Local Storage
    localStorage.setItem('settings', JSON.stringify(settings));

    // Send to server
    sendSettingsToServer(settings);
}

async function sendSettingsToServer(settings) {
    try {
        const response = await fetch('http://localhost:3001/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings),
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Success:', data);
    } catch (error) {
        console.error('Error:', error);
    }
}
