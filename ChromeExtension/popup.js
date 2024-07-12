document.addEventListener('DOMContentLoaded', async () => {
  console.log('DOM fully loaded and parsed');

  // Show loading state immediately
  toggleContentVisibility(false, true);

  // Always check version when popup opens
  console.log('Performing version check...');
  await checkVersionMismatch();

  // Check license key only if not checked this Chrome session
  await checkLicenseKeyIfNeeded();

  // Load settings immediately
  loadSettings();

  // Setup listeners for settings changes
  setupSettingsListeners();

  // Setup listener for license key submission
  const submitLicenseKeyButton = document.getElementById('submitLicenseKeyButton');
  if (submitLicenseKeyButton) {
    submitLicenseKeyButton.addEventListener('click', async () => {
      const licenseKey = document.getElementById('licenseKeyInput').value;
      if (licenseKey) {
        await saveLicenseKey(licenseKey);
        await checkLicenseKeyAndValidation();
      }
    });
  } else {
    console.error('License key submit button not found');
  }
});

async function getVersionCheckStatus() {
  return new Promise(resolve => {
    chrome.storage.local.get(['hasCheckedVersion'], function(result) {
      resolve(result.hasCheckedVersion || false);
    });
  });
}

async function setVersionCheckStatus(status) {
  return new Promise(resolve => {
    chrome.storage.local.set({ hasCheckedVersion: status }, () => {
      console.log('Version Check Status saved:', status);
      resolve();
    });
  });
}

function saveSettings() {
  console.log('Saving settings');
  const settings = {
    resolution: document.getElementById('resolution').value,
    downloadPath: document.getElementById('download-path').value,
    downloadMP3: document.getElementById('download-mp3')?.checked ?? false,
    secondsBefore: document.getElementById('seconds-before').value,
    secondsAfter: document.getElementById('seconds-after').value
  };
  localStorage.setItem('settings', JSON.stringify(settings));
  console.log('Settings saved:', settings);
}

function loadSettings() {
  console.log('Loading settings');
  const settings = JSON.parse(localStorage.getItem('settings')) || {
    resolution: '1080',
    downloadPath: '',
    secondsBefore: 15,
    secondsAfter: 15
  };

  document.getElementById('resolution').value = settings.resolution;
  document.getElementById('download-path').value = settings.downloadPath;
  if (document.getElementById('download-mp3')) {
    document.getElementById('download-mp3').checked = settings.downloadMP3;
  }
  document.getElementById('seconds-before').value = settings.secondsBefore;
  document.getElementById('seconds-after').value = settings.secondsAfter;
}

function setupSettingsListeners() {
  console.log('Setting up settings listeners');
  document.getElementById('resolution').addEventListener('change', saveSettings);
  document.getElementById('download-path').addEventListener('input', saveSettings);
  if (document.getElementById('download-mp3')) {
    document.getElementById('download-mp3').addEventListener('change', saveSettings);
  }
  document.getElementById('seconds-before').addEventListener('change', saveSettings);
  document.getElementById('seconds-after').addEventListener('change', saveSettings);
}

async function getHasCheckedLicense() {
  return new Promise(resolve => {
    chrome.storage.local.get(['hasCheckedLicense'], function(result) {
      resolve(result.hasCheckedLicense || false);
    });
  });
}

async function setHasCheckedLicense(status) {
  return new Promise(resolve => {
    chrome.storage.local.set({ hasCheckedLicense: status }, () => {
      console.log('Has Checked License saved:', status);
      resolve();
    });
  });
}

async function checkLicenseKeyIfNeeded() {
  const hasCheckedLicense = await getHasCheckedLicense();
  if (!hasCheckedLicense) {
    console.log('Checking license key...');
    await checkLicenseKeyAndValidation();
    await setHasCheckedLicense(true);
  } else {
    console.log('License already checked this Chrome session');
    const { isLicenseValidated } = await getLicenseKeyAndValidationStatus();
    toggleContentVisibility(!!isLicenseValidated, false);
  }
}

async function checkLicenseKeyAndValidation() {
  console.log('checkLicenseKeyAndValidation function called');
  const { licenseKey, isLicenseValidated } = await getLicenseKeyAndValidationStatus();
  console.log('License Key:', licenseKey);
  console.log('Is License Validated:', isLicenseValidated);

  if (isLicenseValidated) {
    toggleContentVisibility(true, false);
  } else if (licenseKey) {
    console.log('Validating license key...');
    const isValid = await validateLicenseKey(licenseKey);
    console.log('License key validation result:', isValid);
    if (isValid) {
      await setLicenseValidationStatus(true);
      toggleContentVisibility(true, false);
    } else {
      toggleContentVisibility(false, false);
    }
  } else {
    toggleContentVisibility(false, false);
  }
}

async function getLicenseKeyAndValidationStatus() {
  return new Promise(resolve => {
    chrome.storage.sync.get(['licenseKey', 'isLicenseValidated'], function(result) {
      chrome.storage.local.get(['hasCheckedVersionAndLicense'], function(localResult) {
        console.log('Retrieved License Key and Validation Status from Storage:', result);
        console.log('Retrieved Version and License Check Status from Local Storage:', localResult);
        resolve({
          licenseKey: result.licenseKey,
          isLicenseValidated: result.isLicenseValidated,
          hasCheckedVersionAndLicense: localResult.hasCheckedVersionAndLicense || false
        });
      });
    });
  });
}

async function setLicenseValidationStatus(isValid) {
  return new Promise(resolve => {
    chrome.storage.sync.set({ isLicenseValidated: isValid }, () => {
      console.log('License Validation Status saved:', isValid);
      resolve();
    });
  });
}

async function setHasCheckedVersionAndLicense(hasChecked) {
  return new Promise(resolve => {
    chrome.storage.local.set({ hasCheckedVersionAndLicense: hasChecked }, () => {
      console.log('Has Checked Version and License saved:', hasChecked);
      resolve();
    });
  });
}

async function saveLicenseKey(key) {
  return new Promise(resolve => {
    chrome.storage.sync.set({ licenseKey: key }, () => {
      console.log('License Key saved:', key);
      resolve();
    });
  });
}

async function getVersionCheckedStatus() {
  return new Promise(resolve => {
    chrome.storage.local.get(['versionChecked'], function(result) {
      resolve(result.versionChecked || false);
    });
  });
}

async function setVersionCheckedStatus(status) {
  return new Promise(resolve => {
    chrome.storage.local.set({ versionChecked: status }, () => {
      console.log('Version Checked Status saved:', status);
      resolve();
    });
  });
}

async function fetchBackendVersion() {
  try {
    console.log('Fetching backend version...');
    const response = await fetch('http://localhost:3001/get-version');
    console.log('Response status:', response.status);

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
  console.log('Backend version:', backendVersion);

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
  console.log('Showing version mismatch message:', message);
  const messageDiv = document.getElementById('versionMismatchMessage');

  messageDiv.innerHTML = `${message} Click <a href="#" id="updateLink" style="color: yellow;">here</a>`;
  messageDiv.style.display = 'block';
  messageDiv.style.color = 'red';

  document.getElementById('updateLink').addEventListener('click', function(event) {
    event.preventDefault();
    openUpdateLink();
  });
}

function openUpdateLink() {
  const os = window.navigator.platform.toLowerCase();
  const userAgent = window.navigator.userAgent.toLowerCase();
  let updateUrl = '';

  if (os.includes('mac')) {
    updateUrl = userAgent.includes('arm64') 
      ? 'https://github.com/Selgy/Youtube-to-PremierePro/releases/download/V2.1/YoutubetoPremiere_Mac_arm64.pkg'
      : 'https://github.com/Selgy/Youtube-to-PremierePro/releases/download/V2.1/YoutubetoPremiere_Mac_x64.pkg';
  } else if (os.includes('win')) {
    updateUrl = 'https://github.com/Selgy/Youtube-to-PremierePro/releases/download/V2.1/YoutubetoPremiere_Win.exe';
  } else {
    console.log('Unsupported OS for automatic download.');
    return;
  }

  window.open(updateUrl, '_blank');
}

async function validateLicenseKey(key) {
  console.log('Validating License Key:', key);
  const isValidGumroad = await validateGumroadLicense(key);
  const isValidShopify = await validateShopifyLicense(key);
  return isValidGumroad || isValidShopify;
}

async function validateShopifyLicense(key) {
  console.log('Validating Shopify License:', key);
  const apiToken = 'eHyU10yFizUV5qUJaFS8koE1nIx2UCDFNSoPVdDRJDI7xtunUK6ZWe40vfwp';
  const endpoint = `https://app-easy-product-downloads.fr/api/get-license-key?license_key=${encodeURIComponent(key)}&api_token=${encodeURIComponent(apiToken)}`;
  
  try {
    const response = await fetch(endpoint, { method: 'POST' });

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

    if (!response.ok) {
      if (response.status === 404) {
        console.error('Gumroad license not found. Trying Shopify validation...');
        return false;
      } else {
        throw new Error('Network response was not ok');
      }
    }

    const data = await response.json();
    console.log('API Response Data:', data);
    return data.success;
  } catch (error) {
    console.error('Error in validateGumroadLicense:', error);
    return false;
  }
}

function toggleContentVisibility(isValid, isLoading = false) {
  console.log('Toggling content visibility. Is Valid:', isValid, 'Is Loading:', isLoading);
  if (isLoading) {
    document.getElementById('loadingSection').style.display = 'block';
    document.getElementById('licenseSection').style.display = 'none';
    document.getElementById('mainContent').style.display = 'none';
  } else if (isValid) {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('licenseSection').style.display = 'none';
    document.getElementById('mainContent').style.display = 'block';
    loadSettings();
  } else {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('licenseSection').style.display = 'block';
    document.getElementById('mainContent').style.display = 'none';
  }
}
