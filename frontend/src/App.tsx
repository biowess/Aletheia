import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { CasebookPage } from './pages/CasebookPage';
import { NewCasePage } from './pages/NewCasePage';
import { CaseWorkspacePage } from './pages/CaseWorkspacePage';
import { SettingsPage } from './pages/SettingsPage';
import { useSettingsStore } from './stores/settingsStore';

function App() {

  useEffect(() => {
    // Fetch settings; the returned promise resolves when the store call settles.
    useSettingsStore.getState().fetchSettings();
  }, []);

  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<CasebookPage />} />
        <Route path="/cases/new" element={<NewCasePage />} />
        <Route path="/cases/:caseId" element={<CaseWorkspacePage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
