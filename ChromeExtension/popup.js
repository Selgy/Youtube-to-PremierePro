document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM fully loaded and parsed');
    const licenseKey = await getLicenseKey();
    console.log('License Key:', licenseKey);
    
    
    if (licenseKey) {
        const isValid = await validateGumroadLicense(licenseKey);
        toggleContentVisibility(isValid);
    } else {
        toggleContentVisibility(false);
    }

    document.getElementById('submitKey').addEventListener('click', async () => {
        console.log('Submit Key button clicked');
        const key = document.getElementById('licenseKey').value;
        console.log('Entered Key:', key);
        const isValid = await validateGumroadLicense(key);
        console.log('New Key Validation Result:', isValid);

        if (isValid) {
            chrome.storage.sync.set({ licenseKey: key }, () => {
                console.log('License Key saved:', key);
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
            console.log('Retrieved License Key from Storage:', result.licenseKey);
            resolve(result.licenseKey);
        });
    });
}

async function validateGumroadLicense(key) {
    console.log('Validating Gumroad License:', key);
    try {
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

        console.log('API Response:', response);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('API Response Data:', data);
        return data.success;
    } catch (error) {
        console.error('Error in validateGumroadLicense:', error);
        return false;
    }
}


function toggleContentVisibility(isValid) {
    console.log('Toggling content visibility. Is Valid:', isValid);
    if (isValid) {
        document.getElementById('licenseSection').style.display = 'none';
        document.getElementById('mainContent').style.display = 'block';
        // ... load settings or other initializations ...
    } else {
        document.getElementById('licenseSection').style.display = 'block';
        document.getElementById('mainContent').style.display = 'none';
    }
}

function loadSettings() {
    console.log('Loading settings');
    const settings = JSON.parse(localStorage.getItem('settings')) || {
        resolution: '1080p',
        framerate: '30',
        downloadPath: '',
        downloadMP3: false,
        secondsBefore: 15, // Default value for seconds before
        secondsAfter: 15   // Default value for seconds after
    };

    // Apply the settings to the form
    document.getElementById('resolution').value = settings.resolution;
    document.getElementById('framerate').value = settings.framerate;
    document.getElementById('download-path').value = settings.downloadPath;
    document.getElementById('download-mp3').checked = settings.downloadMP3;
    document.getElementById('seconds-before').value = settings.secondsBefore;
    document.getElementById('seconds-after').value = settings.secondsAfter;
}

