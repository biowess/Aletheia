'use strict';

/**
 * main.js — Aletheia Electron main process
 *
 * Flow:
 *   1. Show splash window immediately
 *   2. Spawn launcher.py (which handles venv / pip / npm / uvicorn / vite)
 *   3. Poll http://localhost:5173 until it responds
 *   4. Open main BrowserWindow pointing at http://localhost:5173
 *   5. Close splash
 *   6. On quit → send SIGTERM to launcher.py (which cascades to children)
 */

const {
  app,
  BrowserWindow,
  ipcMain,
  dialog,
  shell,
  Menu,
} = require('electron');

const path  = require('path');
const http  = require('http');
const { spawn } = require('child_process');
const Store = require('electron-store');

// ── Persistent store (tracks whether first-install is done) ─────────────────
const store = new Store();

// ── Dev mode flag ────────────────────────────────────────────────────────────
const IS_DEV = process.argv.includes('--dev');

// ── Resolve project root (works both in dev and in packaged app) ─────────────
function projectRoot() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, '..');
  }
  // In dev: electron/ is one level below the project root
  return path.resolve(__dirname, '..');
}

// ── Globals ──────────────────────────────────────────────────────────────────
let splashWin   = null;
let mainWin     = null;
let launcherProc = null;

// ── Splash window ─────────────────────────────────────────────────────────────
function createSplash() {
  splashWin = new BrowserWindow({
    width: 860,
    height: 486,
    frame: false,
    transparent: false,
    resizable: false,
    center: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      enableRemoteModule: false,
    },
  });

  splashWin.loadFile(path.join(__dirname, 'splash.html'));
  splashWin.once('ready-to-show', () => splashWin.show());
}

function sendSplashProgress(message, percent) {
  if (splashWin && !splashWin.isDestroyed()) {
    splashWin.webContents.send('splash:progress', { message, percent });
  }
}

// ── Main app window ───────────────────────────────────────────────────────────
function createMainWindow() {
  mainWin = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    show: false,                    // hidden until backend is ready
    title: 'Aletheia',
    icon: path.join(__dirname, '../appicon.png'),
    backgroundColor: '#0a0f1e',    // matches your dark theme; prevents white flash
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      enableRemoteModule: false,
    },
  });

  // Intercept external links → open in system browser, not Electron
  mainWin.webContents.setWindowOpenHandler(({ url: requestUrl }) => {
    try {
      const parsedUrl = new URL(requestUrl);
      if (parsedUrl.hostname === 'localhost' && (parsedUrl.port === '5173' || parsedUrl.port === '8000')) {
        return { action: 'allow' };
      }
    } catch (e) {
      // Invalid URL
    }
    shell.openExternal(requestUrl);
    return { action: 'deny' };
  });

  // Prevent internal navigation to external sites
  mainWin.webContents.on('will-navigate', (event, navigationUrl) => {
    try {
      const parsedUrl = new URL(navigationUrl);
      if (parsedUrl.hostname === 'localhost' && (parsedUrl.port === '5173' || parsedUrl.port === '8000')) {
        return;
      }
    } catch (e) {}
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });

  mainWin.once('ready-to-show', () => {
    if (splashWin && !splashWin.isDestroyed()) {
      splashWin.destroy();
      splashWin = null;
    }
    mainWin.show();
    mainWin.focus();
  });

  Menu.setApplicationMenu(null);

  mainWin.on('closed', () => {
    mainWin = null;
  });
}

// ── Poll until a local URL is ready (progressive backoff) ───────────────────
function waitForUrl(url, initialIntervalMs = 500, timeoutMs = 180_000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;
    let currentInterval = initialIntervalMs;

    function attempt() {
      http.get(url, (res) => {
        res.resume(); // consume response
        if (res.statusCode < 500) return resolve();
        scheduleRetry();
      }).on('error', scheduleRetry);
    }

    function scheduleRetry() {
      if (Date.now() >= deadline) {
        return reject(new Error(`Timed out waiting for ${url}`));
      }
      setTimeout(attempt, currentInterval);
      // Progressive backoff up to 2 seconds
      currentInterval = Math.min(currentInterval + 200, 2000);
    }

    attempt();
  });
}

// ── Spawn launcher.py or backend binary ───────────────────────────────────────
function spawnLauncher(root) {
  if (app.isPackaged) {
    const backendExe = path.join(root, 'backend', 'backend');
    launcherProc = spawn(
      backendExe,
      [],
      {
        cwd: path.join(root, 'backend'),
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: false,
      }
    );
  } else {
    const python = process.platform === 'win32' ? 'python' : 'python3';
    launcherProc = spawn(
      python,
      [path.join(root, 'launcher.py'), '--no-browser'],
      {
        cwd: root,
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: false,
      }
    );
  }

  launcherProc.stdout.on('data', (chunk) => {
    process.stdout.write('[BACKEND] ' + chunk.toString());
  });

  launcherProc.stderr.on('data', (chunk) => {
    process.stderr.write('[BACKEND ERR] ' + chunk.toString());
  });

  launcherProc.on('error', (err) => {
    console.error(`[ELECTRON] launcher.py failed to spawn: ${err.message}`);
    if (splashWin && !splashWin.isDestroyed()) splashWin.destroy();
    let msg = `Could not start the backend process.\n\nError: ${err.message}`;
    if (err.code === 'ENOENT') {
      msg = 'Backend binary or Python executable not found. Ensure it is installed correctly.';
    }
    dialog.showErrorBox('Aletheia Backend Error', msg);
    app.quit();
  });

  launcherProc.on('exit', (code) => {
    console.log(`[ELECTRON] launcher.py exited with code ${code}`);
    if (mainWin && !mainWin.isDestroyed() && code !== 0) {
      let reason = `code ${code}`;
      // Basic exit code mapping for common issues
      if (code === 98 || code === 48) reason = "Port 8000 already in use";
      else if (code === 127) reason = "Missing binary or dependency";
      else if (code === 1) reason = "General runtime error (see terminal for Python stack trace)";
      
      dialog.showErrorBox(
        'Aletheia Backend Error',
        `The backend process exited unexpectedly (${reason}).\n\nCheck the terminal for details. Possible DB corruption or Keyring failure.`
      );
      app.quit();
    }
  });

  return launcherProc;
}

// ── Shutdown helper ──────────────────────────────────────────────────────────
function shutdownLauncher() {
  if (!launcherProc) return;
  if (launcherProc.exitCode !== null) return; // already dead

  console.log('[ELECTRON] Sending SIGTERM to launcher.py...');
  try {
    // launcher.py's graceful_shutdown() catches SIGTERM and kills uvicorn+vite
    if (process.platform === 'win32') {
      launcherProc.kill('SIGTERM');
    } else {
      process.kill(-launcherProc.pid, 'SIGTERM'); // kill process group
    }
  } catch (e) {
    console.error('[ELECTRON] Failed to kill launcher:', e.message);
  }

  // Hard kill after 6 seconds
  setTimeout(() => {
    if (launcherProc && launcherProc.exitCode === null) {
      console.warn('[ELECTRON] Force-killing launcher.py...');
      launcherProc.kill('SIGKILL');
    }
  }, 6000);
}

// ── App lifecycle ────────────────────────────────────────────────────────────
app.whenReady().then(async () => {
  // 1. Show splash immediately
  createSplash();

  const root = projectRoot();
  console.log('[ELECTRON] Project root:', root);

  // 2. Detect first launch (no venv yet)
  const venvPath = path.join(root, 'backend', '.venv');
  const { existsSync } = require('fs');
  const isFirstLaunch = !app.isPackaged && !existsSync(venvPath);

  // 3. Progress messages (timed estimates — launcher.py doesn't emit IPC)
  sendSplashProgress('Starting services…', 5);

  if (isFirstLaunch) {
    sendSplashProgress('First launch: creating Python environment…', 10);
  } else {
    sendSplashProgress('Starting backend and frontend…', 20);
  }

  // 4. Spawn launcher.py
  spawnLauncher(root);

  // 5. Animate progress while waiting
  const steps = isFirstLaunch
    ? [
        [15000, 'Installing Python dependencies…',   30],
        [35000, 'Installing Node modules…',           55],
        [50000, 'Starting backend server…',           70],
        [60000, 'Starting frontend server…',          85],
      ]
    : [
        [3000,  'Starting backend server…',           45],
        [7000,  'Starting frontend server…',          75],
      ];

  for (const [delay, msg, pct] of steps) {
    setTimeout(() => sendSplashProgress(msg, pct), delay);
  }

  // 6. Wait for servers
  try {
    sendSplashProgress('Waiting for app to be ready…', 90);
    if (!app.isPackaged) {
      await waitForUrl('http://localhost:5173', 600, 180_000);
    }
    await Promise.all([
      waitForUrl('http://localhost:8000/api/health', 600, 180_000),
      new Promise(r => setTimeout(r, 4500)),
    ]);
  } catch (err) {
    if (splashWin && !splashWin.isDestroyed()) splashWin.destroy();
    dialog.showErrorBox(
      'Startup Timeout',
      'The frontend did not start within 3 minutes.\n\nCheck that Python 3.11+ and Node.js 20+ are in your PATH and try again.\n\n' + err.message
    );
    app.quit();
    return;
  }

  sendSplashProgress('Launching Aletheia…', 100);

  // Small grace period so the 100% bar is visible
  await new Promise(r => setTimeout(r, 400));

  // 7. Open main window
  createMainWindow();
  if (app.isPackaged) {
    mainWin.loadFile(path.join(root, 'frontend', 'dist', 'index.html'));
  } else {
    mainWin.loadURL('http://localhost:5173');
  }
});

// ── Quit behaviour ───────────────────────────────────────────────────────────
app.on('window-all-closed', () => {
  shutdownLauncher();
  app.quit();
});

app.on('before-quit', () => {
  shutdownLauncher();
});

// macOS: re-open on dock click
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
    if (mainWin) if (app.isPackaged) {
    mainWin.loadFile(path.join(root, 'frontend', 'dist', 'index.html'));
  } else {
    mainWin.loadURL('http://localhost:5173');
  }
  }
});
