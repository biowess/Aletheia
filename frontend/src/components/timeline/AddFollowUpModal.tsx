import React, { useState, useEffect } from 'react';
import { X, Loader2 } from 'lucide-react';
import { FollowUpCreatePayload } from '../../types';
import {
  AnamnesisData,
  PhysicalExamData,
  LaboratoryData,
  MorphologicalData,
} from '../../types/case';
import { createFollowUp } from '../../api/followUps';
import { useReportStore } from '../../stores/reportStore';
import { useCaseStore } from '../../stores/caseStore';
import { useToast } from '../../hooks/useToast';

interface AddFollowUpModalProps {
  caseId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

type EntryType = FollowUpCreatePayload['entry_type'];

const ENTRY_TYPE_OPTIONS: { value: EntryType; label: string }[] = [
  { value: 'general_note',  label: 'General Note' },
  { value: 'anamnesis',     label: 'Anamnesis / History' },
  { value: 'physical_exam', label: 'Physical Exam' },
  { value: 'laboratory',    label: 'Laboratory' },
  { value: 'imaging',       label: 'Imaging' },
  { value: 'procedure',     label: 'Procedure' },
  { value: 'other',         label: 'Other' },
];

/* ── tiny inline field components ──────────────────────────────── */
function FieldTextarea({
  label,
  value,
  onChange,
  placeholder,
  minHeight = 72,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  minHeight?: number;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="form-label">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={2}
        style={{ minHeight }}
        className="textarea-field resize-y"
      />
    </div>
  );
}

/* ── per-type form sections ─────────────────────────────────────── */

function AnamnesisFields({
  value,
  onChange,
}: {
  value: AnamnesisData;
  onChange: (d: AnamnesisData) => void;
}) {
  const set = (field: keyof AnamnesisData) => (v: string) =>
    onChange({ ...value, [field]: v });

  return (
    <div className="space-y-3">
      <FieldTextarea label="Chief Complaint"                   value={value.chief_complaint || ''}            onChange={set('chief_complaint')}            placeholder="e.g. Shortness of breath for 3 days" />
      <FieldTextarea label="History of Present Illness (HPI)" value={value.history_of_present_illness || ''} onChange={set('history_of_present_illness')} placeholder="e.g. Patient states symptoms began gradually…" />
      <FieldTextarea label="Past Medical History"             value={value.past_medical_history || ''}       onChange={set('past_medical_history')}       placeholder="e.g. Hypertension (diagnosed 2015)" />
      <FieldTextarea label="Medications"                      value={value.medications || ''}                onChange={set('medications')}                placeholder="e.g. Lisinopril 10mg daily" />
      <FieldTextarea label="Allergies"                        value={value.allergies || ''}                  onChange={set('allergies')}                  placeholder="e.g. Penicillin (hives)" />
      <FieldTextarea label="Family History"                   value={value.family_history || ''}             onChange={set('family_history')}             placeholder="e.g. Father had MI at 55" />
      <FieldTextarea label="Social History"                   value={value.social_history || ''}             onChange={set('social_history')}             placeholder="e.g. Smokes 1 pack/day for 20 years" />
      <FieldTextarea label="Travel History"                   value={value.travel_history || ''}             onChange={set('travel_history')}             placeholder="e.g. Recent travel to Southeast Asia" />
      <FieldTextarea label="Constitutional Symptoms"          value={value.constitutional_symptoms || ''}    onChange={set('constitutional_symptoms')}    placeholder="e.g. Fever, chills, weight loss" />
    </div>
  );
}

function PhysicalExamFields({
  value,
  onChange,
}: {
  value: PhysicalExamData;
  onChange: (d: PhysicalExamData) => void;
}) {
  const set = (field: keyof PhysicalExamData) => (v: string) =>
    onChange({ ...value, [field]: v });

  return (
    <div className="space-y-3">
      <FieldTextarea label="General Appearance"           value={value.general_appearance || ''} onChange={set('general_appearance')} placeholder="e.g. Well-developed, in no acute distress" />
      <FieldTextarea label="HEENT"                        value={value.heent || ''}              onChange={set('heent')}              placeholder="e.g. Normocephalic; PERRL; oropharynx clear" />
      <FieldTextarea label="Neck"                         value={value.neck || ''}               onChange={set('neck')}               placeholder="e.g. Supple, no lymphadenopathy, no JVD" />
      <FieldTextarea label="Cardiovascular"               value={value.cardiovascular || ''}     onChange={set('cardiovascular')}     placeholder="e.g. Regular rate and rhythm, no murmurs" />
      <FieldTextarea label="Respiratory"                  value={value.respiratory || ''}        onChange={set('respiratory')}        placeholder="e.g. Clear to auscultation bilaterally" />
      <FieldTextarea label="Vascular / Peripheral Perf."  value={value.vascular || ''}           onChange={set('vascular')}           placeholder="e.g. Pulses 2+ bilaterally, no edema" />
      <FieldTextarea label="Abdominal"                    value={value.abdominal || ''}          onChange={set('abdominal')}          placeholder="e.g. Soft, non-tender, active bowel sounds" />
      <FieldTextarea label="Genitourinary"                value={value.genitourinary || ''}      onChange={set('genitourinary')}      placeholder="e.g. No CVA tenderness, no flank pain" />
      <FieldTextarea label="Neurologic"                   value={value.neurologic || ''}         onChange={set('neurologic')}         placeholder="e.g. Alert and oriented ×3, CNs intact" />
      <FieldTextarea label="Psychiatric / Mental Status"  value={value.psychiatric || ''}        onChange={set('psychiatric')}        placeholder="e.g. Cooperative, appropriate affect, no SI" />
      <FieldTextarea label="Endocrine"                    value={value.endocrine || ''}          onChange={set('endocrine')}          placeholder="e.g. No thyroid enlargement, no cushingoid features" />
      <FieldTextarea label="Dermatologic"                 value={value.dermatologic || ''}       onChange={set('dermatologic')}       placeholder="e.g. Warm, dry, no rashes" />
      <FieldTextarea label="Lymphatic"                    value={value.lymphatic || ''}          onChange={set('lymphatic')}          placeholder="e.g. No cervical or axillary adenopathy" />
      <FieldTextarea label="Musculoskeletal"              value={value.musculoskeletal || ''}    onChange={set('musculoskeletal')}    placeholder="e.g. Normal range of motion, no swelling" />
      <FieldTextarea label="Breast Exam (if indicated)"   value={value.breast || ''}             onChange={set('breast')}             placeholder="e.g. No masses, no nipple discharge" />
      <FieldTextarea label="Pelvic Exam (if indicated)"   value={value.pelvic || ''}             onChange={set('pelvic')}             placeholder="e.g. Normal external genitalia, no CMT" />
      <FieldTextarea label="Rectal Exam (if indicated)"   value={value.rectal || ''}             onChange={set('rectal')}             placeholder="e.g. Normal tone, no masses, guaiac negative" />
    </div>
  );
}

function LaboratoryFields({
  value,
  onChange,
  freeNote,
  onFreeNoteChange,
}: {
  value: LaboratoryData;
  onChange: (d: LaboratoryData) => void;
  freeNote: string;
  onFreeNoteChange: (v: string) => void;
}) {
  const set = (field: keyof LaboratoryData) => (v: string) =>
    onChange({ ...value, [field]: v });

  return (
    <div className="space-y-3">
      <FieldTextarea label="Complete Blood Count (CBC)" value={value.cbc || ''}                 onChange={set('cbc')}                 placeholder="e.g. WBC 8.5 K/uL, Hgb 14.2 g/dL, Plt 250 K/uL" />
      <FieldTextarea label="Differential"               value={value.differential || ''}         onChange={set('differential')}         placeholder="e.g. Neutrophils 60%, Lymphocytes 30%" />
      <FieldTextarea label="Coagulation"                value={value.coagulation || ''}           onChange={set('coagulation')}           placeholder="e.g. PT 12 s, INR 1.0, aPTT 30 s" />
      <FieldTextarea label="Chemistry / Metabolic Panel" value={value.chemistry || ''}            onChange={set('chemistry')}            placeholder="e.g. Na 140, K 4.0, Cr 0.9 mg/dL" />
      <FieldTextarea label="Inflammatory Markers"       value={value.inflammatory_markers || ''} onChange={set('inflammatory_markers')} placeholder="e.g. CRP <5 mg/L, ESR 10 mm/hr" />
      <FieldTextarea label="Iron Studies"               value={value.iron_studies || ''}          onChange={set('iron_studies')}          placeholder="e.g. Ferritin 150 ng/mL, Iron 80 μg/dL" />
      <FieldTextarea label="Hemolysis Markers"          value={value.hemolysis_markers || ''}     onChange={set('hemolysis_markers')}     placeholder="e.g. LDH 180 U/L, Haptoglobin 100 mg/dL" />
      <FieldTextarea label="Endocrine Panels"           value={value.endocrine_panels || ''}      onChange={set('endocrine_panels')}      placeholder="e.g. TSH 2.0 mIU/L, Free T4 1.2 ng/dL" />
      {/* free-text at the end */}
      <div className="border-t border-clinical-outline-variant pt-3">
        <FieldTextarea
          label="Additional Notes"
          value={freeNote}
          onChange={onFreeNoteChange}
          placeholder="Any additional context, pending results, or interpretive notes…"
          minHeight={88}
        />
      </div>
    </div>
  );
}

function ImagingFields({
  value,
  onChange,
  freeNote,
  onFreeNoteChange,
}: {
  value: MorphologicalData;
  onChange: (d: MorphologicalData) => void;
  freeNote: string;
  onFreeNoteChange: (v: string) => void;
}) {
  const set = (field: keyof MorphologicalData) => (v: string) =>
    onChange({ ...value, [field]: v });

  return (
    <div className="space-y-3">
      <FieldTextarea label="X-Ray"           value={value.xray || ''}            onChange={set('xray')}            placeholder="e.g. CXR: Clear lung fields, normal heart size" />
      <FieldTextarea label="CT Scan"         value={value.ct || ''}              onChange={set('ct')}              placeholder="e.g. CT Abdomen: No acute intra-abdominal abnormalities" />
      <FieldTextarea label="MRI"             value={value.mri || ''}             onChange={set('mri')}             placeholder="e.g. MRI Brain: Unremarkable" />
      <FieldTextarea label="Ultrasound"      value={value.ultrasound || ''}      onChange={set('ultrasound')}      placeholder="e.g. RUQ US: Normal gallbladder, no stones" />
      <FieldTextarea label="Pathology"       value={value.pathology || ''}       onChange={set('pathology')}       placeholder="e.g. Benign tissue, no evidence of malignancy" />
      <FieldTextarea label="Peripheral Smear" value={value.peripheral_smear || ''} onChange={set('peripheral_smear')} placeholder="e.g. Normochromic, normocytic RBCs" />
      <FieldTextarea label="Biopsy"          value={value.biopsy || ''}          onChange={set('biopsy')}          placeholder="e.g. Skin biopsy: Consistent with psoriasis" />
      <FieldTextarea label="Flow Cytometry"  value={value.flow_cytometry || ''} onChange={set('flow_cytometry')} placeholder="e.g. Normal CD4/CD8 ratio, no aberrant populations" />
      {/* free-text at the end */}
      <div className="border-t border-clinical-outline-variant pt-3">
        <FieldTextarea
          label="Additional Notes"
          value={freeNote}
          onChange={onFreeNoteChange}
          placeholder="Any additional radiological context or interpretive notes…"
          minHeight={88}
        />
      </div>
    </div>
  );
}

/* ── Main Modal ─────────────────────────────────────────────────── */

export function AddFollowUpModal({ caseId, isOpen, onClose, onSuccess }: AddFollowUpModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useToast();

  const [entryType, setEntryType] = useState<EntryType>('general_note');
  const [title, setTitle] = useState('');
  const [generateReport, setGenerateReport] = useState(false);

  // per-type state
  const [freeTextNote, setFreeTextNote]     = useState('');   // general_note / procedure / other
  const [anamnesisData, setAnamnesisData]   = useState<AnamnesisData>({});
  const [physExamData, setPhysExamData]     = useState<PhysicalExamData>({});
  const [labData, setLabData]               = useState<LaboratoryData>({});
  const [labNote, setLabNote]               = useState('');
  const [imagingData, setImagingData]       = useState<MorphologicalData>({});
  const [imagingNote, setImagingNote]       = useState('');

  // Reset all fields when entry type changes
  useEffect(() => {
    setFreeTextNote('');
    setAnamnesisData({});
    setPhysExamData({});
    setLabData({});
    setLabNote('');
    setImagingData({});
    setImagingNote('');
    setError(null);
  }, [entryType]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  const triggerGenerateReport = useReportStore(state => state.generateReport);
  const activeCase = useCaseStore(state => state.activeCase);

  if (!isOpen) return null;

  /* derive the combined free_text_note to send to backend */
  const derivedFreeText = (): string | undefined => {
    switch (entryType) {
      case 'general_note':
      case 'procedure':
      case 'other':
        return freeTextNote.trim() || undefined;
      case 'laboratory':
        return labNote.trim() || undefined;
      case 'imaging':
        return imagingNote.trim() || undefined;
      default:
        return undefined;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const payload: FollowUpCreatePayload = {
        entry_type: entryType,
        title: title.trim(),
        free_text_note: derivedFreeText(),
        ...(entryType === 'anamnesis'     && { anamnesis_delta:     anamnesisData }),
        ...(entryType === 'physical_exam' && { physical_exam_delta: physExamData }),
        ...(entryType === 'laboratory'    && { laboratory_delta:    labData }),
        ...(entryType === 'imaging'       && { morphological_delta: imagingData }),
      };

      await createFollowUp(caseId, payload);

      if (generateReport && activeCase) {
        triggerGenerateReport({
          case_id: caseId,
          anamnesis: activeCase.anamnesis,
          physical_exam: activeCase.physical_exam,
          laboratory_data: activeCase.laboratory_data,
          morphological_data: activeCase.morphological_data,
          follow_up_context: derivedFreeText() || title.trim(),
          use_grounding: true,
        }).catch(() => {
          showToast('Report generation failed', 'error');
        });
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create follow-up');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderFields = () => {
    switch (entryType) {
      case 'general_note':
        return (
          <FieldTextarea
            label="Note"
            value={freeTextNote}
            onChange={setFreeTextNote}
            placeholder="Enter your general note here…"
            minHeight={160}
          />
        );
      case 'anamnesis':
        return <AnamnesisFields value={anamnesisData} onChange={setAnamnesisData} />;
      case 'physical_exam':
        return <PhysicalExamFields value={physExamData} onChange={setPhysExamData} />;
      case 'laboratory':
        return (
          <LaboratoryFields
            value={labData}
            onChange={setLabData}
            freeNote={labNote}
            onFreeNoteChange={setLabNote}
          />
        );
      case 'imaging':
        return (
          <ImagingFields
            value={imagingData}
            onChange={setImagingData}
            freeNote={imagingNote}
            onFreeNoteChange={setImagingNote}
          />
        );
      case 'procedure':
        return (
          <FieldTextarea
            label="Procedure Description"
            value={freeTextNote}
            onChange={setFreeTextNote}
            placeholder="Describe the procedure, findings, and outcome…"
            minHeight={160}
          />
        );
      case 'other':
      default:
        return (
          <FieldTextarea
            label="Notes"
            value={freeTextNote}
            onChange={setFreeTextNote}
            placeholder="Enter any additional notes here…"
            minHeight={160}
          />
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-clinical-inverse-surface/40 backdrop-blur-sm animate-fade-up">
      <div
        className="bg-clinical-surface-bright rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden border border-clinical-outline-variant"
        style={{ boxShadow: 'var(--cf-shadow-card-elevated)' }}
        role="dialog"
        aria-modal="true"
      >
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-clinical-outline-variant flex items-center justify-between bg-clinical-surface-container-low flex-shrink-0">
          <h2 className="text-headline-md font-semibold text-clinical-on-surface">Add Follow-Up Entry</h2>
          <button
            onClick={onClose}
            className="text-clinical-on-surface-variant hover:text-clinical-on-surface hover:bg-clinical-surface-container p-2 rounded-lg transition-colors duration-fast ease-clinical focus:outline-none focus-visible:shadow-focus"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-5">
          {error && (
            <div className="p-3 bg-clinical-error-container text-clinical-on-error-container border border-clinical-error rounded-lg text-body-md">
              {error}
            </div>
          )}

          {/* Type + Title row */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="form-label">Entry Type</label>
              <select
                autoFocus
                value={entryType}
                onChange={(e) => setEntryType(e.target.value as EntryType)}
                className="input-field"
              >
                {ENTRY_TYPE_OPTIONS.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="form-label">
                Title{' '}
                <span className="text-clinical-error normal-case tracking-normal font-bold">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Follow-up visit 2 weeks"
                className="input-field"
                required
              />
            </div>
          </div>

          {/* Contextual fields based on entry type */}
          <div>{renderFields()}</div>

          {/* Generate Report Toggle */}
          <div className="bg-clinical-primary-container border border-clinical-primary rounded-lg p-4 flex items-start gap-3">
            <div className="flex items-center h-5 mt-0.5">
              <input
                id="generate-report"
                type="checkbox"
                checked={generateReport}
                onChange={(e) => setGenerateReport(e.target.checked)}
                className="w-4 h-4 rounded accent-[var(--cf-inverse-primary)] border border-clinical-outline focus-visible:shadow-focus"
              />
            </div>
            <div className="flex-1">
              <label
                htmlFor="generate-report"
                className="text-body-md font-semibold text-clinical-on-primary-container block cursor-pointer"
              >
                Generate new report after adding this follow-up
              </label>
              <p className="text-label-sm text-clinical-on-primary-container/80 mt-1 tracking-wide">
                Checking this will incorporate the new follow-up information and automatically synthesise an updated clinical reasoning report.
              </p>
            </div>
          </div>
        </form>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-clinical-outline-variant bg-clinical-surface-container-low flex justify-end gap-3 flex-shrink-0">
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="btn-ghost"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="btn-primary"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving…
              </>
            ) : (
              'Save Follow-Up'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
