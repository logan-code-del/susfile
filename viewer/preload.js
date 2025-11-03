const { contextBridge, ipcRenderer } = require('electron');
const os = require('os');

// Note: we intentionally do NOT expose secret values (password or whitelist) directly to the renderer.
// Instead we expose functions that verify inputs in the preload (Node) context where process.env is available.

function splitList(s) {
  return (s || '')
    .split(',')
    .map(x => x.trim())
    .filter(Boolean);
}

const PASSWORD = process.env.PASSWORD || 'letmein';
const DURATION = parseInt(process.env.DURATION || '30', 10);
const ASCII_SECONDS = parseInt(process.env.ASCII_SECONDS || '3', 10);
const WHITELIST = splitList(process.env.WHITELIST || '');

contextBridge.exposeInMainWorld('electronAPI', {
  unlock: (reason) => ipcRenderer.invoke('unlock', reason),
  onCloseAttempt: (cb) => ipcRenderer.on('close-attempt', cb),
  // Expose non-secret numeric config values
  getConfig: () => ({ duration: DURATION, asciiSeconds: ASCII_SECONDS }),
  // Verify a GitHub username and/or password without exposing secret lists
  verifyCredentials: (githubUser, passwordAttempt) => {
    const isWhitelisted = WHITELIST.includes((githubUser || '').trim());
    const passwordOk = passwordAttempt === PASSWORD;
    return { isWhitelisted, passwordOk, allowed: isWhitelisted || passwordOk };
  },
  osUser: os.userInfo().username
});
