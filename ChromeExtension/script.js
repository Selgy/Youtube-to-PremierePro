document.addEventListener('DOMContentLoaded', () => {
    // Load and initialize settings
    const settings = JSON.parse(localStorage.getItem('settings')) || {
        resolution: '1080p',
        //framerate: '30',
        downloadPath: '',
        downloadMP3: false,
        secondsBefore: '15',
        secondsAfter: '15'
    };

    // Initialize settings
    document.getElementById('resolution').value = settings.resolution;
    //document.getElementById('framerate').value = settings.framerate;
    document.getElementById('download-path').value = settings.downloadPath;
    document.getElementById('download-mp3').checked = settings.downloadMP3;
    document.getElementById('seconds-before').value = settings.secondsBefore;
    document.getElementById('seconds-after').value = settings.secondsAfter;

    // Add event listeners for settings changes
    document.getElementById('resolution').addEventListener('change', saveAndSendSettings);
    //document.getElementById('framerate').addEventListener('change', saveAndSendSettings);
    document.getElementById('download-path').addEventListener('change', function() {
        const newPath = document.getElementById('download-path').value;
        updateLastPaths(newPath); // Update the list of last paths
        saveAndSendSettings(); // Call this if you need to save/send settings on each change
    });
    document.getElementById('download-mp3').addEventListener('change', saveAndSendSettings);
    document.getElementById('seconds-before').addEventListener('change', saveAndSendSettings);
    document.getElementById('seconds-after').addEventListener('change', saveAndSendSettings);



    // Event listener for the arrow button to show/hide the dropdown
    const showLastPathsButton = document.getElementById('show-last-paths');
    if (showLastPathsButton) {
        console.log('Adding event listener to show-last-paths button');
        showLastPathsButton.addEventListener('click', function(event) {
            console.log('show-last-paths button clicked');
            event.stopPropagation(); // Prevent the event from propagating to the document
            toggleDropdown();
        });
    } else {
        console.log('show-last-paths button not found');
    }

    // Clicking anywhere else on the document will close the dropdown
    document.addEventListener('click', function() {
        console.log('Document clicked');
        const dropdown = document.getElementById('last-paths-dropdown');
        if (dropdown.style.display === 'block') {
            dropdown.style.display = 'none';
        }
    });
});

function toggleDropdown() {
    console.log('Toggling dropdown');
    const dropdown = document.getElementById('last-paths-dropdown');
    console.log('Dropdown current display:', dropdown.style.display);
    console.log('Toggling dropdown');
    if (dropdown.style.display === 'none' || !dropdown.style.display) {
        populateLastPathsDropdown();
        dropdown.style.display = 'block';
    } else {
        dropdown.style.display = 'none';
    }
}

function populateLastPathsDropdown() {
    console.log('Populating last paths dropdown');
    let lastPaths = JSON.parse(localStorage.getItem('lastPaths')) || [];
    lastPaths = lastPaths.reverse();  // Reverse the order to show most recent first
    console.log('Last paths:', lastPaths);

    const dropdown = document.getElementById('last-paths-dropdown');
    dropdown.innerHTML = ''; // Clear current list

    lastPaths.forEach(path => {
        const listItem = document.createElement('li');
        listItem.textContent = path;
        listItem.onclick = function() {
            selectPath(path);
        };
        listItem.style.cursor = 'pointer';
        listItem.style.padding = '5px';
        listItem.style.background = '#2e2f77';
        listItem.style.color = 'white';
        listItem.style.borderBottom = '1px solid #ddd';
        dropdown.appendChild(listItem);
    });
}

function selectPath(path) {
    console.log('Path selected:', path);
    const downloadPathInput = document.getElementById('download-path');
    downloadPathInput.value = path;
    updateLastPaths(path); // Update last paths with the selected path
    document.getElementById('last-paths-dropdown').style.display = 'none'; // Hide dropdown
    saveAndSendSettings(); // Save and send updated settings to the server
}

function saveAndSendSettings() {
    const settings = {
        resolution: document.getElementById('resolution').value,
        //framerate: document.getElementById('framerate').value,
        downloadPath: document.getElementById('download-path').value,
        downloadMP3: document.getElementById('download-mp3').checked,
        secondsBefore: document.getElementById('seconds-before').value,
        secondsAfter: document.getElementById('seconds-after').value
    };

    // Save to Local Storage
    localStorage.setItem('settings', JSON.stringify(settings));
    updateLastPaths(settings.downloadPath); // Update the list when settings are saved

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

function updateLastPaths(newPath) {
    if (newPath.trim() === '') return; // Ignore empty paths
    let lastPaths = JSON.parse(localStorage.getItem('lastPaths')) || [];
    if (!lastPaths.includes(newPath)) {
        lastPaths.push(newPath);
        if (lastPaths.length > 5) {
            lastPaths = lastPaths.slice(-5);
        }
        localStorage.setItem('lastPaths', JSON.stringify(lastPaths));
    }
    // Optional: Call to refresh the dropdown with new paths
    populateLastPathsDropdown();
}