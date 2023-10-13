const express = require('express');
const fs = require('fs');
const socketIo = require('socket.io');
const { exec } = require('child_process');
const cors = require('cors'); 
const app = express();
const port = 3000;

app.use(express.json());
app.use(cors({
    origin: 'https://www.youtube.com',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type']
}));

app.get('/', (req, res) => {
    res.send('Server is running');
});

const server = app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});

let settings = {
    resolution: '1080p',
    framerate: '30',
    downloadPath: 'D:/youtube download',
};

let latestVideoUrl = '';  // New variable to store the latest video URL

app.post('/settings', (req, res) => {
    console.log('Received settings:', req.body);
    settings = req.body; 
    fs.writeFileSync('settings.json', JSON.stringify(settings, null, 2));
    res.json(settings);    
});

const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

io.on('connection', (socket) => {
    console.log('New socket connection:', socket.id);

    socket.on('identify', (identity) => {
        if (identity === 'CEP panel') {
            console.log('CEP panel connected');
        }
    });

    socket.on('disconnect', (reason) => {
        console.log('Socket disconnected:', reason);
    });

    socket.on('error', (error) => {
        console.error('Socket error:', error);
    });
});

io.on('connect_error', (error) => {
    console.error('Connection error:', error);
});

app.post('/handle-video-url', (req, res) => {
    console.log('Received request on /handle-video-url');
    const videoUrl = req.body.videoUrl;
    latestVideoUrl = videoUrl;  // Store the latest video URL
    console.log('Video URL:', videoUrl);
    console.log('Request body:', req.body);

    exec(`python Youtube-download.py "${videoUrl}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing script: ${error}`);
            res.status(500).json({ error: 'Internal Server Error' });
            return;
        }

        console.log('Python script output:', stdout);
        console.error('Python script errors:', stderr);

        io.emit('import', 'D:\\youtube download');
        res.sendStatus(200);
    });
});

app.get('/get-video-url', (req, res) => {  // New endpoint to get the latest video URL
    res.json({ videoUrl: latestVideoUrl });
});
