document.addEventListener('DOMContentLoaded', () => {
    // Load settings from Local Storage
    const settings = JSON.parse(localStorage.getItem('settings'));
    if (settings) {
        document.getElementById('resolution').value = settings.resolution || '1080p';
        document.getElementById('framerate').value = settings.framerate || '30';
        document.getElementById('download-path').value = settings.downloadPath || 'TEST';
        document.getElementById('download-mp3').checked = settings.downloadMP3 || false;
    }

    const button = document.getElementById('save-settings');
    const message = document.getElementById('message');

    button.addEventListener('click', () => {
        const settings = {
            resolution: document.getElementById('resolution').value,
            framerate: document.getElementById('framerate').value,
            downloadPath: document.getElementById('download-path').value,
            downloadMP3: document.getElementById('download-mp3').checked
        };
        sendSettingsToServer(settings);
        localStorage.setItem('settings', JSON.stringify(settings));
        showMessage(message, 'Settings saved');
    });
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
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Success:', data);
    } catch (error) {
        console.error('Error:', error);
    }
}

function showMessage(element, text) {
    element.innerText = text;
    element.style.display = 'block';
    setTimeout(() => {
        element.style.opacity = '1';
        setTimeout(() => {
            element.style.opacity = '0';
            setTimeout(() => {
                element.style.display = 'none';
            }, 500);
        }, 2000);
    }, 10);
}
