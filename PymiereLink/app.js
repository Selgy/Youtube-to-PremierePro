var child_process = require('child_process');
var exec = child_process.exec;
var os = require('os');
var path = require('path');

// Construct the executable path relative to the current script's location
var execPath = path.join(__dirname, 'exec');

var cmd;

if (os.platform() === 'darwin') {
    // macOS specific command for a standalone executable
    cmd = `"${path.join(execPath, 'YoutubetoPremiere')}"`;
} else if (os.platform() === 'win32') {
    // Windows specific command
    cmd = `"${path.join(execPath, 'YoutubetoPremiere.exe')}"`; // Replace 'YourWindowsApp.exe' with your Windows app name
}

if (cmd) {
    exec(cmd, function(err, stdout, stderr) {
        // Handle execution results here
    });
} else {
    console.error('Unsupported operating system.');
}
