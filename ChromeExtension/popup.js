document.addEventListener('DOMContentLoaded', async () => {
  console.log('Popup DOM fully loaded and parsed');

  // Show loading while checking version
  toggleContentVisibility(false, true);

  // Perform version check every time the panel is opened
  await checkVersionMismatch();

  const { licenseKey, isLicenseValidated, hasCheckedVersionAndLicense } = await getLicenseKeyAndValidationStatus();
  console.log('License and version status:', { licenseKey, isLicenseValidated, hasCheckedVersionAndLicense });

  if (!hasCheckedVersionAndLicense) {
      if (licenseKey) {
          const isValid = await validateLicenseKey(licenseKey);
          console.log('License key validation result:', isValid);
          if (isValid) {
              await setLicenseValidationStatus(true);
          }
          toggleContentVisibility(isValid);
      } else {
          toggleContentVisibility(false);
      }
      await setHasCheckedVersionAndLicense(true);
  } else {
      toggleContentVisibility(isLicenseValidated);
  }

  document.getElementById('submitKey').addEventListener('click', async () => {
      console.log('Submit Key button clicked');
      const key = document.getElementById('licenseKey').value;
      console.log('Entered Key:', key);
      const isValid = await validateLicenseKey(key);
      console.log('New Key Validation Result:', isValid);

      if (isValid) {
          await saveLicenseKey(key);
          await setLicenseValidationStatus(true);
          toggleContentVisibility(true);
      } else {
          document.getElementById('errorMessage').style.display = 'block';
      }
  });
});

async function getLicenseKeyAndValidationStatus() {
  return new Promise(resolve => {
      chrome.storage.sync.get(['licenseKey', 'isLicenseValidated'], function(result) {
          chrome.storage.local.get(['hasCheckedVersionAndLicense'], function(localResult) {
              console.log('Retrieved License Key and Validation Status from Storage:', result);
              console.log('Retrieved Version and License Check Status from Local Storage:', localResult);
              resolve({ ...result, ...localResult });
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

async function fetchBackendVersion() {
  try {
      console.log('Fetching backend version...');
      const response = await fetch('http://localhost:3001/get-version');
      if (!response.ok) {
          console.error('Server response not ok:', response.statusText);
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
  
  messageDiv.innerHTML = `${message} Click <a href="#" id="updateLink" style="color: yellow;">here</a>`;
  messageDiv.style.display = 'block';

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
          console.error('Server response not ok:', response.statusText);
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

function loadSettings() {
  console.log('Loading settings');
  const settings = JSON.parse(localStorage.getItem('settings')) || {
      resolution: '1080',
      downloadPath: '',
      downloadMP3: false,
      secondsBefore: 15,
      secondsAfter: 15
  };
  console.log('Settings loaded:', settings);

  document.getElementById('resolution').value = settings.resolution;
  document.getElementById('download-path').value = settings.downloadPath;
  document.getElementById('download-mp3').checked = settings.downloadMP3;
  document.getElementById('seconds-before').value = settings.secondsBefore;
  document.getElementById('seconds-after').value = settings.secondsAfter;
}
