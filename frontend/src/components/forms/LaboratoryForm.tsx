import React from 'react';
import { LaboratoryData } from '../../types/case';
import { FormField } from './FormField';
import { CollapsibleSection } from './CollapsibleSection';

interface LaboratoryFormProps {
  value: LaboratoryData;
  onChange: (data: LaboratoryData) => void;
}

export function LaboratoryForm({ value, onChange }: LaboratoryFormProps) {
  const handleChange = (field: keyof LaboratoryData, newValue: string) => {
    onChange({ ...value, [field]: newValue });
  };

  return (
    <div className="space-y-6">
      <CollapsibleSection title="Hematology" defaultOpen={true}>
        <FormField
          label="Complete Blood Count (CBC)"
          value={value.cbc || ''}
          onChange={(val) => handleChange('cbc', val)}
          placeholder="e.g., WBC: 8.5 K/uL, Hgb: 14.2 g/dL, Plt: 250 K/uL"
        />
        <FormField
          label="Differential"
          value={value.differential || ''}
          onChange={(val) => handleChange('differential', val)}
          placeholder="e.g., Neutrophils 60%, Lymphocytes 30%"
        />
        <FormField
          label="Coagulation"
          value={value.coagulation || ''}
          onChange={(val) => handleChange('coagulation', val)}
          placeholder="e.g., PT: 12s, INR: 1.0, aPTT: 30s"
        />
      </CollapsibleSection>

      <CollapsibleSection title="Chemistry & Metabolic" defaultOpen={true}>
        <FormField
          label="Basic/Comprehensive Metabolic Panel"
          value={value.chemistry || ''}
          onChange={(val) => handleChange('chemistry', val)}
          placeholder="e.g., Na: 140 mEq/L, K: 4.0 mEq/L, Cr: 0.9 mg/dL"
        />
      </CollapsibleSection>

      <CollapsibleSection title="Specialized Panels" defaultOpen={false}>
        <FormField
          label="Inflammatory Markers"
          value={value.inflammatory_markers || ''}
          onChange={(val) => handleChange('inflammatory_markers', val)}
          placeholder="e.g., CRP: <5 mg/L, ESR: 10 mm/hr"
        />
        <FormField
          label="Iron Studies"
          value={value.iron_studies || ''}
          onChange={(val) => handleChange('iron_studies', val)}
          placeholder="e.g., Ferritin: 150 ng/mL, Iron: 80 ug/dL"
        />
        <FormField
          label="Hemolysis Markers"
          value={value.hemolysis_markers || ''}
          onChange={(val) => handleChange('hemolysis_markers', val)}
          placeholder="e.g., LDH: 180 U/L, Haptoglobin: 100 mg/dL"
        />
        <FormField
          label="Endocrine Panels"
          value={value.endocrine_panels || ''}
          onChange={(val) => handleChange('endocrine_panels', val)}
          placeholder="e.g., TSH: 2.0 mIU/L, Free T4: 1.2 ng/dL"
        />
      </CollapsibleSection>
    </div>
  );
}
