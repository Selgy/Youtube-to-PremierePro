document.addEventListener('DOMContentLoaded', async () => {
    // Perform version check immediately after the popup loads
    await checkVersionMismatch();

    console.log('DOM fully loaded and parsed');
    const licenseKey = await getLicenseKey();
    console.log('License Key:', licenseKey);
    
    if (licenseKey) {
        // Updated to use validateLicenseKey instead of validateGumroadLicense
        const isValid = await validateLicenseKey(licenseKey);
        toggleContentVisibility(isValid);
    } else {
        toggleContentVisibility(false);
    }

    document.getElementById('submitKey').addEventListener('click', async () => {
        console.log('Submit Key button clicked');
        const key = document.getElementById('licenseKey').value;
        console.log('Entered Key:', key);
        const isValid = await validateLicenseKey(key);
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
    
    // Call the function to check for version mismatch
    await checkVersionMismatch();
});

async function getLicenseKey() {
    return new Promise(resolve => {
        chrome.storage.sync.get(['licenseKey'], function(result) {
            console.log('Retrieved License Key from Storage:', result.licenseKey);
            resolve(result.licenseKey);
        });
    });
}

async function fetchBackendVersion() {
    try {
        console.log('Fetching backend version...');
        const response = await fetch('http://localhost:3001/get-version');

        if (!response.ok) {
            if (response.status === 404) {
                console.error('get_version endpoint not found. Please update your backend.');
                return 'endpoint-missing';
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
        }

        const data = await response.json();
        console.log('Fetched backend version:', data.version);
        return data.version;
    } catch (error) {
        console.error('Error fetching backend version:', error);
        return null;
    }
}

async function checkVersionMismatch() {
    console.log('Checking for version mismatch...');
    const backendVersion = await fetchBackendVersion();
    const extensionVersion = chrome.runtime.getManifest().version;
    console.log('Extension version:', extensionVersion);

    if (backendVersion === 'endpoint-missing') {
        console.log('Backend version endpoint missing, suggesting update...');
        showVersionMismatchMessage('Update available.');
    } else if (backendVersion && extensionVersion !== backendVersion) {
        console.log('Version mismatch detected');
        showVersionMismatchMessage();
    } else {
        console.log('Version match confirmed or unable to retrieve backend version');
    }
}

function showVersionMismatchMessage(message = 'Update available.') {
    const messageDiv = document.getElementById('versionMismatchMessage');
    
    // Clear any existing content
    messageDiv.innerHTML = '';

    // Create the text node
    const textNode = document.createTextNode(message + ' Click ');

    // Create the clickable link
    const updateLink = document.createElement('a');
    updateLink.href = '#';
    updateLink.textContent = 'here';
    updateLink.style.color = 'yellow';
    updateLink.addEventListener('click', function(event) {
        event.preventDefault();
        openUpdateLink();
    });

    // Append text node and link to the message div
    messageDiv.appendChild(textNode);
    messageDiv.appendChild(updateLink);
    
    messageDiv.style.display = 'block'; // Make the <p> element visible
}

function openUpdateLink() {
    const os = window.navigator.platform.toLowerCase();
    const userAgent = window.navigator.userAgent.toLowerCase();
    let updateUrl = '';
  
    if (os.indexOf('mac') !== -1) {
      // Mac OS detected
      if (userAgent.indexOf('arm64') !== -1) {
        // Apple Silicon (ARM64) detected
        updateUrl = 'https://github.com/Selgy/Youtube-to-PremierePro/releases/download/V1.1/YoutubetoPremiere_Mac_arm64.pkg';
      } else {
        // Intel (x64) detected
        updateUrl = 'https://github.com/Selgy/Youtube-to-PremierePro/releases/download/V1.1/YoutubetoPremiere_Mac_x64.pkg';
      }
    } else if (os.indexOf('win') !== -1) {
      // Windows OS detected
      updateUrl = 'https://github.com/Selgy/Youtube-to-PremierePro/releases/download/V1.1/YoutubetoPremiereInstaller.exe';
    } else {
      // If the OS is neither Mac nor Windows, you can choose to do nothing or handle it differently
      console.log('Unsupported OS for automatic download.');
      return;
    }
  
    window.open(updateUrl, '_blank'); // Open the URL in a new tab
  }
  

  async function validateLicenseKey(key) {
    console.log('Validating License Key:', key);
    // Assuming you have the logic for Gumroad validation here
    const isValidGumroad = await validateGumroadLicense(key); 
    const isValidShopify = await validateShopifyLicense(key);
    return isValidGumroad || isValidShopify;
}

async function validateShopifyLicense(key) {
    console.log('Validating Shopify License:', key);
    const apiToken = 'eHyU10yFizUV5qUJaFS8koE1nIx2UCDFNSoPVdDRJDI7xtunUK6ZWe40vfwp';
    const endpoint = `https://app-easy-product-downloads.fr/api/get-license-key?license_key=${encodeURIComponent(key)}&api_token=${encodeURIComponent(apiToken)}`;
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Shopify API Response Data:', data);
        return data.status === 'success';
    } catch (error) {
        console.error('Error in validateShopifyLicense:', error);
        return false;
    }
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
                product_id: '9yYJT15dJO3wB4Z74N-EUg==', 
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
        resolution: '1080',
        downloadPath: '',
        downloadMP3: false,
        secondsBefore: 15, // Default value for seconds before
        secondsAfter: 15   // Default value for seconds after
    };

    // Apply the settings to the form
    document.getElementById('resolution').value = settings.resolution;
    document.getElementById('download-path').value = settings.downloadPath;
    document.getElementById('download-mp3').checked = settings.downloadMP3;
    document.getElementById('seconds-before').value = settings.secondsBefore;
    document.getElementById('seconds-after').value = settings.secondsAfter;
}
