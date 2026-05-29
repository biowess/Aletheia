import React from 'react';
import { PhysicalExamData } from '../../types/case';
import { FormField } from './FormField';
import { CollapsibleSection } from './CollapsibleSection';

interface PhysicalExamFormProps {
  value: PhysicalExamData;
  onChange: (data: PhysicalExamData) => void;
}

export function PhysicalExamForm({ value, onChange }: PhysicalExamFormProps) {
  const handleChange = (field: keyof PhysicalExamData, newValue: string) => {
    onChange({ ...value, [field]: newValue });
  };

  return (
    <div className="space-y-6">
      {/* ── General ─────────────────────────────────────────── */}
      <CollapsibleSection title="General" defaultOpen={true}>
        <FormField
          label="General Appearance"
          value={value.general_appearance || ''}
          onChange={(val) => handleChange('general_appearance', val)}
          placeholder="e.g., Well-developed, well-nourished, in no acute distress"
        />
      </CollapsibleSection>

      {/* ── Head & Neck ─────────────────────────────────────── */}
      <CollapsibleSection title="Head & Neck" defaultOpen={true}>
        <FormField
          label="HEENT"
          value={value.heent || ''}
          onChange={(val) => handleChange('heent', val)}
          placeholder="e.g., Normocephalic, atraumatic; PERRL; oropharynx clear; TMs intact"
        />
        <FormField
          label="Neck"
          value={value.neck || ''}
          onChange={(val) => handleChange('neck', val)}
          placeholder="e.g., Supple, no lymphadenopathy, no thyromegaly, no JVD"
        />
      </CollapsibleSection>

      {/* ── Cardiopulmonary ─────────────────────────────────── */}
      <CollapsibleSection title="Cardiopulmonary" defaultOpen={true}>
        <FormField
          label="Cardiovascular"
          value={value.cardiovascular || ''}
          onChange={(val) => handleChange('cardiovascular', val)}
          placeholder="e.g., Regular rate and rhythm, no murmurs, rubs, or gallops"
        />
        <FormField
          label="Respiratory"
          value={value.respiratory || ''}
          onChange={(val) => handleChange('respiratory', val)}
          placeholder="e.g., Clear to auscultation bilaterally, no wheezes or crackles"
        />
        <FormField
          label="Vascular / Peripheral Perfusion"
          value={value.vascular || ''}
          onChange={(val) => handleChange('vascular', val)}
          placeholder="e.g., Pulses 2+ bilaterally, capillary refill <2s, no edema"
        />
      </CollapsibleSection>

      {/* ── Abdomen & GU ────────────────────────────────────── */}
      <CollapsibleSection title="Abdomen & Genitourinary" defaultOpen={true}>
        <FormField
          label="Abdominal"
          value={value.abdominal || ''}
          onChange={(val) => handleChange('abdominal', val)}
          placeholder="e.g., Soft, non-tender, non-distended, active bowel sounds"
        />
        <FormField
          label="Genitourinary"
          value={value.genitourinary || ''}
          onChange={(val) => handleChange('genitourinary', val)}
          placeholder="e.g., No flank tenderness, no costovertebral angle tenderness"
        />
      </CollapsibleSection>

      {/* ── Neurologic & Psychiatric ─────────────────────────── */}
      <CollapsibleSection title="Neurologic & Psychiatric" defaultOpen={true}>
        <FormField
          label="Neurologic"
          value={value.neurologic || ''}
          onChange={(val) => handleChange('neurologic', val)}
          placeholder="e.g., Alert and oriented ×3, cranial nerves II–XII intact, no focal deficits"
        />
        <FormField
          label="Psychiatric / Mental Status"
          value={value.psychiatric || ''}
          onChange={(val) => handleChange('psychiatric', val)}
          placeholder="e.g., Cooperative, appropriate affect, normal speech, no SI/HI"
        />
      </CollapsibleSection>

      {/* ── Endocrine & Other ───────────────────────────────── */}
      <CollapsibleSection title="Endocrine & Other Systems" defaultOpen={false}>
        <FormField
          label="Endocrine"
          value={value.endocrine || ''}
          onChange={(val) => handleChange('endocrine', val)}
          placeholder="e.g., No thyroid enlargement, no cushingoid features"
        />
        <FormField
          label="Dermatologic"
          value={value.dermatologic || ''}
          onChange={(val) => handleChange('dermatologic', val)}
          placeholder="e.g., Warm, dry, intact; no rashes, lesions, or jaundice"
        />
        <FormField
          label="Lymphatic"
          value={value.lymphatic || ''}
          onChange={(val) => handleChange('lymphatic', val)}
          placeholder="e.g., No cervical, axillary, or inguinal lymphadenopathy"
        />
        <FormField
          label="Musculoskeletal"
          value={value.musculoskeletal || ''}
          onChange={(val) => handleChange('musculoskeletal', val)}
          placeholder="e.g., Normal range of motion in all extremities, no joint swelling"
        />
      </CollapsibleSection>

      {/* ── Optional / Sensitive Exams ───────────────────────── */}
      <CollapsibleSection title="Sensitive Examinations (Optional)" defaultOpen={false}>
        <p
          className="text-xs mb-4 px-1"
          style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}
        >
          Complete only if clinically indicated and properly consented.
        </p>
        <FormField
          label="Breast Exam"
          value={value.breast || ''}
          onChange={(val) => handleChange('breast', val)}
          placeholder="e.g., No masses, skin changes, or nipple discharge bilaterally"
        />
        <FormField
          label="Pelvic Exam"
          value={value.pelvic || ''}
          onChange={(val) => handleChange('pelvic', val)}
          placeholder="e.g., Normal external genitalia, no cervical motion tenderness"
        />
        <FormField
          label="Rectal Exam"
          value={value.rectal || ''}
          onChange={(val) => handleChange('rectal', val)}
          placeholder="e.g., Normal sphincter tone, no masses, guaiac negative"
        />
      </CollapsibleSection>
    </div>
  );
}
