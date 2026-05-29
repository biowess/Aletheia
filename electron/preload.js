'use strict';

const { contextBridge, ipcRenderer } = require('electron');

// Exposed to the splash window renderer
contextBridge.exposeInMainWorld('splashBridge', {
  onProgress: (callback) => {
    ipcRenderer.on('splash:progress', (_event, data) => callback(data));
  },
});

// Exposed to the main app window renderer (optional, for future use)
contextBridge.exposeInMainWorld('electronBridge', {
  platform: process.platform,
  onBackendStatus: (callback) => {
    ipcRenderer.on('backend:status', (_event, data) => callback(data));
  },
});
