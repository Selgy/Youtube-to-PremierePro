document.addEventListener('DOMContentLoaded', async () => {
    const licenseKey = await getLicenseKey();
    if (licenseKey) {
        const isValid = await validateGumroadLicense(licenseKey);
        toggleContentVisibility(isValid);
    } else {
        toggleContentVisibility(false);
    }

    document.getElementById('submitKey').addEventListener('click', async () => {
        const key = document.getElementById('licenseKey').value;
        const isValid = await validateGumroadLicense(key);
        if (isValid) {
            chrome.storage.sync.set({ licenseKey: key }, () => {
                toggleContentVisibility(true);
            });
        } else {
            document.getElementById('errorMessage').style.display = 'block';
        }
    });
});

async function getLicenseKey() {
    return new Promise(resolve => {
        chrome.storage.sync.get(['licenseKey'], function(result) {
            resolve(result.licenseKey);
        });
    });
}

async function validateGumroadLicense(key) {
    // First check if the provided key is the test key
    if (key === "chipi chipi chapa chapa") {
        return true; // Test key is always valid
    }

    try {
        // Make the API call if the key is not the test key
        const response = await fetch('https://api.gumroad.com/v2/licenses/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: '9yYJT15dJO3wB4Z74N-EUg==', // Replace with your actual product_id
                license_key: key
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        return data.success; // The key is valid if 'success' is true
    } catch (error) {
        console.error('Error:', error);
        return false;
    }
}



function toggleContentVisibility(isValid) {
    if (isValid) {
        document.getElementById('licenseSection').style.display = 'none';
        document.getElementById('mainContent').style.display = 'block';
        loadSettings();
    } else {
        document.getElementById('licenseSection').style.display = 'block';
        document.getElementById('mainContent').style.display = 'none';
    }
}

function loadSettings() {
    // Load and apply the settings as before
    const settings = JSON.parse(localStorage.getItem('settings')) || {
        resolution: '1080p',
        framerate: '30',
        downloadPath: '',
        downloadMP3: false
    };

    document.getElementById('resolution').value = settings.resolution;
    document.getElementById('framerate').value = settings.framerate;
    document.getElementById('download-path').value = settings.downloadPath;
    document.getElementById('download-mp3').checked = settings.downloadMP3;
}
