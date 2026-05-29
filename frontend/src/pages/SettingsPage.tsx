import React, { useEffect, useState } from 'react';
import { useSettingsStore } from '../stores/settingsStore';
import { SettingRow } from '../components/settings/SettingRow';
import { ToggleSwitch } from '../components/settings/ToggleSwitch';
import { generateReport } from '../api/reasoning';
import { cleanupCache, getCacheStats } from '../api/settings';
import { useToast } from '../hooks/useToast';
import { Settings, Database, Key, RefreshCw } from 'lucide-react';

export const SettingsPage = () => {
  const { settings, fetchSettings, updateSetting, isLoading } = useSettingsStore();
  const { showToast } = useToast();
  const [cacheStats, setCacheStats] = useState<{
    total_entries: number;
    expired_entries: number;
    valid_entries: number;
  } | null>(null);

  const [showApiKey, setShowApiKey] = useState(false);
  const [localApiKey, setLocalApiKey] = useState('');
  const [showNcbiApiKey, setShowNcbiApiKey] = useState(false);
  const [localNcbiApiKey, setLocalNcbiApiKey] = useState('');
  const [localTtl, setLocalTtl] = useState('');

  const loadCacheStats = async () => {
    try {
      const stats = await getCacheStats();
      setCacheStats(stats);
    } catch (e) {
      showToast('Failed to load cache stats', 'error');
    }
  };

  useEffect(() => {
    fetchSettings();
    loadCacheStats();
  }, [fetchSettings]);

  useEffect(() => {
    const apiKeySetting = settings.find(s => s.key === 'gemini_api_key');
    if (apiKeySetting) setLocalApiKey(apiKeySetting.value);
    const ncbiApiKeySetting = settings.find(s => s.key === 'ncbi_api_key');
    if (ncbiApiKeySetting) setLocalNcbiApiKey(ncbiApiKeySetting.value);
    const ttlSetting = settings.find(s => s.key === 'cache_ttl_hours');
    if (ttlSetting) setLocalTtl(ttlSetting.value);
  }, [settings]);

  const handleToggle = (key: string, value: boolean) => {
    updateSetting(key, String(value));
    showToast('Setting updated', 'success');
  };

  const handleBlurApiKey = () => {
    const currentSetting = settings.find(s => s.key === 'gemini_api_key')?.value || '';
    if (localApiKey !== currentSetting) {
      updateSetting('gemini_api_key', localApiKey);
      showToast('API Key updated', 'success');
    }
  };

  const handleBlurNcbiApiKey = () => {
    const currentSetting = settings.find(s => s.key === 'ncbi_api_key')?.value || '';
    if (localNcbiApiKey !== currentSetting) {
      if (localNcbiApiKey && !/^[a-f0-9]{36}$/i.test(localNcbiApiKey)) {
        showToast('Invalid NCBI API Key format', 'error');
        setLocalNcbiApiKey(currentSetting);
        return;
      }
      updateSetting('ncbi_api_key', localNcbiApiKey);
      showToast('NCBI API Key updated', 'success');
    }
  };

  const handleBlurTtl = () => {
    const currentSetting = settings.find(s => s.key === 'cache_ttl_hours')?.value || '';
    if (localTtl !== currentSetting) {
      updateSetting('cache_ttl_hours', localTtl);
      showToast('Cache TTL updated', 'success');
    }
  };

  const handleVerifyApiKey = async () => {
    try {
      showToast('Verifying API Key…', 'info');
      await generateReport({
        case_id: 'test_verify_key',
        anamnesis: {},
        physical_exam: {},
        laboratory_data: {},
        morphological_data: {},
      });
      showToast('API Key verified successfully!', 'success');
    } catch (error) {
      showToast('API Key verification failed', 'error');
    }
  };

  const handleClearCache = async () => {
    try {
      showToast('Clearing cache…', 'info');
      const { deleted_entries } = await cleanupCache();
      showToast(`Cleared ${deleted_entries} expired entries.`, 'success');
      loadCacheStats();
    } catch (error) {
      showToast('Failed to clear cache', 'error');
    }
  };

  const getBooleanSetting = (key: string, defaultValue: boolean = false) => {
    const setting = settings.find(s => s.key === key);
    return setting ? setting.value === 'true' : defaultValue;
  };

  return (
    <div className="max-w-3xl mx-auto p-6 md:p-10 space-y-10 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center gap-3 border-b border-[var(--border-subtle)] pb-4">
        <div
          className="w-8 h-8 rounded-sm flex items-center justify-center"
          style={{ backgroundColor: 'var(--aletheia-navy)' }}
        >
          <Settings className="w-4 h-4 text-white" />
        </div>
        <div>
          <h1
            className="text-xl font-semibold tracking-tight leading-tight"
            style={{ color: 'var(--text-primary)' }}
          >
            Settings
          </h1>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            System configuration and preferences
          </p>
        </div>
      </div>

      {/* AI Provider Section */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 mb-2">
          <Key className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
          <h2
            className="text-[11px] font-semibold tracking-widest uppercase"
            style={{ color: 'var(--text-secondary)' }}
          >
            AI Provider Configuration
          </h2>
        </div>

        {isLoading && settings.length === 0 ? (
          <div className="text-xs" style={{ color: 'var(--text-muted)' }}>Loading settings…</div>
        ) : (
          <div
            className="rounded-md overflow-hidden bg-white"
            style={{ border: '1px solid var(--border-default)', boxShadow: 'var(--cf-shadow-card)' }}
          >
            <SettingRow
              label="Gemini API Key"
              description="Your Google Gemini API key used for reasoning generation."
            >
              <div className="flex items-center gap-2">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={localApiKey}
                  onChange={(e) => setLocalApiKey(e.target.value)}
                  onBlur={handleBlurApiKey}
                  placeholder="Enter API Key"
                  className="input-field w-64"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="text-[10px] font-semibold w-10 text-center uppercase tracking-widest outline-none transition-colors"
                  style={{ color: 'var(--state-info)' }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = 'var(--aletheia-navy)'; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = 'var(--state-info)'; }}
                >
                  {showApiKey ? 'Hide' : 'Show'}
                </button>
              </div>
            </SettingRow>

            <SettingRow
              label="Enable Search Grounding"
              description="Use web search to ground reasoning in recent medical literature."
            >
              <ToggleSwitch
                value={getBooleanSetting('grounding_enabled', true)}
                onChange={(val) => handleToggle('grounding_enabled', val)}
              />
            </SettingRow>

            <SettingRow
              label="NCBI API Key"
              description={
                <>
                  Increases PubMed rate limit from 3 to 10 req/s.{' '}
                  <a href="https://www.ncbi.nlm.nih.gov/account/" target="_blank" rel="noreferrer" className="hover:underline" style={{ color: 'var(--state-info)' }}>
                    Get key
                  </a>
                </>
              }
            >
              <div className="flex items-center gap-2">
                <input
                  type={showNcbiApiKey ? 'text' : 'password'}
                  value={localNcbiApiKey}
                  onChange={(e) => setLocalNcbiApiKey(e.target.value)}
                  onBlur={handleBlurNcbiApiKey}
                  placeholder="Paste your NCBI key (optional)"
                  className="input-field w-64"
                />
                <button
                  type="button"
                  onClick={() => setShowNcbiApiKey(!showNcbiApiKey)}
                  className="text-[10px] font-semibold w-10 text-center uppercase tracking-widest outline-none transition-colors"
                  style={{ color: 'var(--state-info)' }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = 'var(--aletheia-navy)'; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = 'var(--state-info)'; }}
                >
                  {showNcbiApiKey ? 'Hide' : 'Show'}
                </button>
              </div>
            </SettingRow>
          </div>
        )}
      </section>

      {/* Evidence Cache Section */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 mb-2">
          <Database className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
          <h2
            className="text-[11px] font-semibold tracking-widest uppercase"
            style={{ color: 'var(--text-secondary)' }}
          >
            Evidence Cache
          </h2>
        </div>

        <div
          className="rounded-md overflow-hidden bg-white"
          style={{ border: '1px solid var(--border-default)', boxShadow: 'var(--cf-shadow-card)' }}
        >
          <SettingRow
            label="Cache TTL"
            description="Time to live for cached evidence in hours."
          >
            <input
              type="number"
              min="1"
              value={localTtl}
              onChange={(e) => setLocalTtl(e.target.value)}
              onBlur={handleBlurTtl}
              className="input-field w-20 text-center num-tabular"
            />
          </SettingRow>

          <SettingRow
            label="Cache Status"
            description="Current status of the global reasoning evidence cache."
          >
            {cacheStats ? (
              <div className="flex items-center gap-2 text-[10px]">
                <span className="badge-secondary">{cacheStats.total_entries} total</span>
                <span className="badge-primary">{cacheStats.valid_entries} valid</span>
                <span className="badge-error">{cacheStats.expired_entries} expired</span>
              </div>
            ) : (
              <span className="text-[11px]" style={{ color: 'var(--text-muted)' }}>Loading…</span>
            )}
          </SettingRow>
        </div>
      </section>

      {/* PDF Export Section */}
      <section className="space-y-3">
        <div className="flex items-center gap-2 mb-2">
          <RefreshCw className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
          <h2
            className="text-[11px] font-semibold tracking-widest uppercase"
            style={{ color: 'var(--text-secondary)' }}
          >
            PDF Export
          </h2>
        </div>

        <div
          className="rounded-md overflow-hidden bg-white"
          style={{ border: '1px solid var(--border-default)', boxShadow: 'var(--cf-shadow-card)' }}
        >
          <SettingRow
            label="Include Timeline in PDF"
            description="Automatically include patient timeline in exported PDF reports."
          >
            <ToggleSwitch
              value={getBooleanSetting('pdf_include_timeline', true)}
              onChange={(val) => handleToggle('pdf_include_timeline', val)}
            />
          </SettingRow>
        </div>
      </section>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-6 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
        <button onClick={handleVerifyApiKey} className="btn-primary">
          Verify API Key
        </button>
        <button onClick={handleClearCache} className="btn-ghost">
          Clear Expired Cache
        </button>
      </div>
    </div>
  );
};
