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
    cmd = `chmod +x "${macExecutablePath}" && "${macExecutablePath}"`;  // Set execute permissions and then run
} else if (os.platform() === 'win32') {
    // Windows specific command
    cmd = `"${path.join(execPath, 'YoutubetoPremiere.exe')}"`;
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
