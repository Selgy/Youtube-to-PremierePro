document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');
    initializeSettings();
    setupEventListeners();
});

function initializeSettings() {
    console.log('Initializing settings...');
    const defaultSettings = {
        resolution: '1080p',
        downloadPath: '',
        downloadMP3: false,
        secondsBefore: '15',
        secondsAfter: '15'
    };
    const settings = JSON.parse(localStorage.getItem('settings')) || defaultSettings;
    console.log('Loaded settings:', settings);

    document.getElementById('resolution').value = settings.resolution;
    document.getElementById('download-path').value = settings.downloadPath;
    document.getElementById('download-mp3').checked = settings.downloadMP3;
    document.getElementById('seconds-before').value = settings.secondsBefore;
    document.getElementById('seconds-after').value = settings.secondsAfter;
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    const elements = {
        resolution: document.getElementById('resolution'),
        downloadPath: document.getElementById('download-path'),
        downloadMP3: document.getElementById('download-mp3'),
        secondsBefore: document.getElementById('seconds-before'),
        secondsAfter: document.getElementById('seconds-after'),
        showLastPathsButton: document.getElementById('show-last-paths')
    };

    elements.resolution.addEventListener('change', saveAndSendSettings);
    elements.downloadPath.addEventListener('change', handleDownloadPathChange);
    elements.downloadMP3.addEventListener('change', saveAndSendSettings);
    elements.secondsBefore.addEventListener('change', saveAndSendSettings);
    elements.secondsAfter.addEventListener('change', saveAndSendSettings);

    if (elements.showLastPathsButton) {
        elements.showLastPathsButton.addEventListener('click', handleShowLastPathsClick);
    }

    document.addEventListener('click', closeDropdownOnClickOutside);
}

function handleDownloadPathChange() {
    const newPath = document.getElementById('download-path').value;
    updateLastPaths(newPath);
    saveAndSendSettings();
}

function handleShowLastPathsClick(event) {
    event.stopPropagation();
    toggleDropdown();
}

function closeDropdownOnClickOutside() {
    const dropdown = document.getElementById('last-paths-dropdown');
    if (dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
    }
}

function toggleDropdown() {
    const dropdown = document.getElementById('last-paths-dropdown');
    if (dropdown.style.display === 'none' || !dropdown.style.display) {
        populateLastPathsDropdown();
        dropdown.style.display = 'block';
    } else {
        dropdown.style.display = 'none';
    }
}

function populateLastPathsDropdown() {
    let lastPaths = JSON.parse(localStorage.getItem('lastPaths')) || [];
    lastPaths = lastPaths.reverse();
    
    const dropdown = document.getElementById('last-paths-dropdown');
    dropdown.innerHTML = '';

    lastPaths.forEach(path => {
        const listItem = document.createElement('li');
        listItem.textContent = path;
        listItem.onclick = () => selectPath(path);
        listItem.style.cursor = 'pointer';
        listItem.style.padding = '5px';
        listItem.style.background = '#2e2f77';
        listItem.style.color = 'white';
        listItem.style.borderBottom = '1px solid #ddd';
        dropdown.appendChild(listItem);
    });
}

function selectPath(path) {
    document.getElementById('download-path').value = path;
    updateLastPaths(path);
    document.getElementById('last-paths-dropdown').style.display = 'none';
    saveAndSendSettings();
}

function saveAndSendSettings() {
    console.log('Saving and sending settings...');
    const settings = {
        resolution: document.getElementById('resolution').value,
        downloadPath: document.getElementById('download-path').value,
        downloadMP3: document.getElementById('download-mp3').checked,
        secondsBefore: document.getElementById('seconds-before').value,
        secondsAfter: document.getElementById('seconds-after').value
    };
    console.log('Settings to save:', settings);

    localStorage.setItem('settings', JSON.stringify(settings));
    updateLastPaths(settings.downloadPath);

    sendSettingsToServer(settings);
}

async function sendSettingsToServer(settings) {
    console.log('Sending settings to server:', settings);
    try {
        const response = await fetch('http://localhost:3001/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings),
        });
        if (!response.ok) {
            console.error('Server response not ok:', response.statusText);
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Server response:', data);
        if (!data.success) {
            console.error('Server returned an error:', data.error);
        }
    } catch (error) {
        console.error('Error sending settings to server:', error);
    }
}


function updateLastPaths(newPath) {
    if (newPath.trim() === '') return;

    let lastPaths = JSON.parse(localStorage.getItem('lastPaths')) || [];
    if (!lastPaths.includes(newPath)) {
        lastPaths.push(newPath);
        if (lastPaths.length > 5) {
            lastPaths = lastPaths.slice(-5);
        }
        localStorage.setItem('lastPaths', JSON.stringify(lastPaths));
    }
    populateLastPathsDropdown();
}
