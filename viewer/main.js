const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
// Load dotenv to allow local .env configuration
require('dotenv').config({ path: path.join(__dirname, '.env') });

let win;
let allowClose = false;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    resizable: false,
    movable: true,
    minimizable: false,
    maximizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    }
  });

  win.removeMenu();
  win.loadFile(path.join(__dirname, 'viewer.html'));

  // Prevent close unless allowClose true
  win.on('close', (e) => {
    if (!allowClose) {
      e.preventDefault();
      // send a message so the renderer can show a warning if desired
      win.webContents.send('close-attempt');
    }
  });
}

ipcMain.handle('unlock', (event, reason) => {
  // Called by renderer when timer ends or correct password entered
  allowClose = true;
  // Close the window gracefully
  if (win) win.close();
  return true;
});

app.whenReady().then(() => {
  createWindow();
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Ensure full exit when all windows are closed
app.on('window-all-closed', function () {
  // On Windows/linux we quit the app; killing the process from Task Manager will also stop it
  app.quit();
});
