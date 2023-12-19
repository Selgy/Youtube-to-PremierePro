var child_process = require('child_process');
var exec = child_process.exec;
var os = require('os');
var path = require('path');

// Construct the executable path relative to the current script's location
var execPath = path.join(__dirname, 'exec');
var cmd;

if (os.platform() === 'darwin') {
    // macOS specific command for a standalone executable
    var macExecutablePath = path.join(execPath, 'YoutubetoPremiere');
    // Use AppleScript to launch and hide the application
    var appleScriptCommand = `tell application "Finder" to launch application "${macExecutablePath}"`;
    cmd = `osascript -e '${appleScriptCommand}' -e 'delay 2' -e 'tell application "System Events" to set visible of process "YoutubetoPremiere" to false'`;
} else if (os.platform() === 'win32') {
    // Windows specific command
    var winExecutablePath = path.join(execPath, 'YoutubetoPremiere.exe');
    // Use a Windows batch command to launch the application without a window
    cmd = `start /B "" "${winExecutablePath}"`;
}

if (cmd) {
    exec(cmd, function(err, stdout, stderr) {
        if (err) {
            console.error('Error executing command:', err);
        }
        if (stdout) {
            console.log('Output:', stdout);
        }
        if (stderr) {
            console.error('Error output:', stderr);
        }
    });
} else {
    console.error('Unsupported operating system.');
}
