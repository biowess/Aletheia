import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Loader2, AlertCircle } from 'lucide-react';
import { TabNav } from '../components/layout/TabNav';
import { AnamnesisForm } from '../components/forms/AnamnesisForm';
import { PhysicalExamForm } from '../components/forms/PhysicalExamForm';
import { LaboratoryForm } from '../components/forms/LaboratoryForm';
import { MorphologicalForm } from '../components/forms/MorphologicalForm';
import { createCase } from '../api/cases';
import {
  AnamnesisData,
  PhysicalExamData,
  LaboratoryData,
  MorphologicalData
} from '../types';

const TABS = ['Anamnesis', 'Physical Exam', 'Laboratory', 'Morphological'];

export const NewCasePage: React.FC = () => {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [title, setTitle] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [anamnesis, setAnamnesis] = useState<AnamnesisData>({});
  const [physicalExam, setPhysicalExam] = useState<PhysicalExamData>({});
  const [labData, setLabData] = useState<LaboratoryData>({});
  const [morphData, setMorphData] = useState<MorphologicalData>({});

  const handleSave = async () => {
    if (!title.trim()) {
      setError('Case title is required.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    const tags = tagsInput
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0);

    try {
      const newCase = await createCase({
        title: title.trim(),
        tags,
        anamnesis,
        physical_exam: physicalExam,
        laboratory_data: labData,
        morphological_data: morphData
      });
      navigate(`/cases/${newCase.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create case. Please try again.');
      setIsSubmitting(false);
    }
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 0: return <AnamnesisForm value={anamnesis} onChange={setAnamnesis} />;
      case 1: return <PhysicalExamForm value={physicalExam} onChange={setPhysicalExam} />;
      case 2: return <LaboratoryForm value={labData} onChange={setLabData} />;
      case 3: return <MorphologicalForm value={morphData} onChange={setMorphData} />;
      default: return null;
    }
  };

  return (
    <div className="flex flex-col h-full bg-[var(--bg-primary)] overflow-hidden">
      {/* ── Page Header ────────────────────────────────────────── */}
      <header
        className="px-6 py-4 flex items-center justify-between shrink-0"
        style={{
          backgroundColor: 'var(--surface-primary)',
          borderBottom: '1px solid var(--border-subtle)',
          boxShadow: 'var(--cf-shadow-card)',
          zIndex: 10,
        }}
      >
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="flex items-center justify-center w-8 h-8 rounded-sm outline-none transition-colors"
            style={{ color: 'var(--text-muted)' }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = 'var(--surface-secondary)';
              (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
              (e.currentTarget as HTMLElement).style.color = 'var(--text-muted)';
            }}
            aria-label="Back to Casebook"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <h1
            className="text-lg font-semibold tracking-tight leading-tight"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.01em' }}
          >
            New Case
          </h1>
        </div>

        <button
          onClick={handleSave}
          disabled={isSubmitting}
          className="btn-primary"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              Saving…
            </>
          ) : (
            <>
              <Save className="w-3.5 h-3.5" />
              Save Case
            </>
          )}
        </button>
      </header>

      {/* ── Main Content ───────────────────────────────────────── */}
      <main className="flex-1 w-full max-w-4xl mx-auto px-6 py-8 overflow-y-auto">
        {/* Error Banner */}
        {error && (
          <div
            className="mb-6 p-3 flex items-start gap-2 text-xs"
            style={{
              backgroundColor: 'var(--cf-error-container)',
              border: '1px solid var(--state-declined)',
              borderRadius: 'var(--radius-1)',
              color: 'var(--cf-on-error-container)',
            }}
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <p>{error}</p>
          </div>
        )}

        {/* Title & Tags Card */}
        <div
          className="mb-6 p-6 animate-fade-up"
          style={{
            backgroundColor: 'var(--surface-primary)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-2)',
            boxShadow: 'var(--cf-shadow-card)',
          }}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="title" className="form-label">
                Case Title <span style={{ color: 'var(--state-declined)' }}>*</span>
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. 45yo M with unexplained weight loss"
                className="input-field"
              />
            </div>

            <div>
              <label htmlFor="tags" className="form-label">
                Tags <span className="normal-case tracking-normal font-normal opacity-60 ml-1">(comma separated)</span>
              </label>
              <input
                id="tags"
                type="text"
                value={tagsInput}
                onChange={(e) => setTagsInput(e.target.value)}
                placeholder="e.g. oncology, urgent, follow-up"
                className="input-field"
              />
            </div>
          </div>
        </div>

        {/* Clinical Data Card */}
        <div
          className="animate-fade-up"
          style={{
            backgroundColor: 'var(--surface-primary)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-2)',
            boxShadow: 'var(--cf-shadow-card)',
            animationDelay: '60ms',
          }}
        >
          <div className="pt-2 px-2">
            <TabNav
              tabs={TABS}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />
          </div>
          <div className="p-6 min-h-[400px]">
            {renderActiveTab()}
          </div>
        </div>
      </main>
    </div>
  );
};
