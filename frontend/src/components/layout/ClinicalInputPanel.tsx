import React, { useState, useEffect } from 'react';
import { Save, Loader2, AlertCircle } from 'lucide-react';
import { TabNav } from './TabNav';
import { AnamnesisForm } from '../forms/AnamnesisForm';
import { PhysicalExamForm } from '../forms/PhysicalExamForm';
import { LaboratoryForm } from '../forms/LaboratoryForm';
import { MorphologicalForm } from '../forms/MorphologicalForm';
import { useCaseStore } from '../../stores/caseStore';
import { updateCase } from '../../api/cases';
import {
  AnamnesisData,
  PhysicalExamData,
  LaboratoryData,
  MorphologicalData
} from '../../types';

const TABS = ['Anamnesis', 'Physical Exam', 'Laboratory', 'Morphological'];

export interface ClinicalInputPanelProps {
  anamnesis: AnamnesisData;
  setAnamnesis: React.Dispatch<React.SetStateAction<AnamnesisData>>;
  physicalExam: PhysicalExamData;
  setPhysicalExam: React.Dispatch<React.SetStateAction<PhysicalExamData>>;
  labData: LaboratoryData;
  setLabData: React.Dispatch<React.SetStateAction<LaboratoryData>>;
  morphData: MorphologicalData;
  setMorphData: React.Dispatch<React.SetStateAction<MorphologicalData>>;
  notes: string;
  setNotes: React.Dispatch<React.SetStateAction<string>>;
}

export const ClinicalInputPanel: React.FC<ClinicalInputPanelProps> = ({
  anamnesis, setAnamnesis,
  physicalExam, setPhysicalExam,
  labData, setLabData,
  morphData, setMorphData,
  notes, setNotes
}) => {
  const { activeCase, fetchCase } = useCaseStore();

  const [activeTab, setActiveTab] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpdate = async () => {
    if (!activeCase) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await updateCase(activeCase.id, {
        anamnesis,
        physical_exam: physicalExam,
        laboratory_data: labData,
        morphological_data: morphData,
        notes: notes.trim() ? notes.trim() : undefined,
      });
      await fetchCase(activeCase.id);
    } catch (err: any) {
      setError(err.message || 'Failed to update case.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!activeCase) {
    return (
      <div className="p-6 text-[13px]" style={{ color: 'var(--text-muted)' }}>
        No active case selected.
      </div>
    );
  }

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
    <div className="flex flex-col h-full bg-white relative">
      {/* Header and Actions */}
      <div
        className="px-5 py-3 flex justify-between items-center sticky top-0 z-10"
        style={{
          backgroundColor: 'var(--surface-primary)',
          borderBottom: '1px solid var(--border-default)',
        }}
      >
        <h2
          className="text-sm font-semibold tracking-tight"
          style={{ color: 'var(--aletheia-navy)' }}
        >
          Clinical Data
        </h2>
        <button
          onClick={handleUpdate}
          disabled={isSubmitting}
          className="btn-ghost"
          style={{ height: '28px', padding: '0 12px', fontSize: '11px' }}
        >
          {isSubmitting ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Save className="w-3.5 h-3.5 text-[var(--text-secondary)]" />
          )}
          {isSubmitting ? 'Saving…' : 'Update'}
        </button>
      </div>

      {/* Error Banner */}
      {error && (
        <div
          className="mx-5 mt-4 p-3 flex items-start gap-2 text-[12px]"
          style={{
            backgroundColor: 'var(--cf-error-container)',
            border: '1px solid var(--state-declined)',
            borderRadius: 'var(--radius-1)',
            color: 'var(--cf-on-error-container)',
          }}
        >
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-px" />
          {error}
        </div>
      )}

      {/* Tabs and Form */}
      <div className="flex-1 overflow-y-auto">
        <div className="pt-2 px-1">
          <TabNav tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />
        </div>

        <div className="px-5 py-5 animate-fade-in">
          {renderActiveTab()}
        </div>

        {/* Internal Notes */}
        <div
          className="px-5 py-6 mt-4"
          style={{ borderTop: '1px dashed var(--border-default)' }}
        >
          <label htmlFor="case-notes" className="form-label">
            Internal Notes
          </label>
          <textarea
            id="case-notes"
            rows={4}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any internal notes, reminders, or observations here…"
            className="textarea-field"
          />
        </div>
      </div>
    </div>
  );
};
