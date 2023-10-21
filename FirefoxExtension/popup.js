document.addEventListener('DOMContentLoaded', () => {
    const saveSettingsButton = document.getElementById('save-settings');

    if (saveSettingsButton) {  // Check if the element exists
        saveSettingsButton.addEventListener('click', () => {
            const resolution = document.getElementById('resolution').value;
            const framerate = document.getElementById('framerate').value;
            const downloadPath = document.getElementById('download-path').value;

            fetch('http://localhost:3001/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    resolution,
                    framerate,
                    downloadPath,
                }),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    } else {
        console.error('save-settings button not found');
    }
});
