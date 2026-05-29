import React from 'react';
import { AnamnesisData } from '../../types/case';
import { FormField } from './FormField';
import { CollapsibleSection } from './CollapsibleSection';

interface AnamnesisFormProps {
  value: AnamnesisData;
  onChange: (data: AnamnesisData) => void;
}

export function AnamnesisForm({ value, onChange }: AnamnesisFormProps) {
  const handleChange = (field: keyof AnamnesisData, newValue: string) => {
    onChange({ ...value, [field]: newValue });
  };

  return (
    <div className="space-y-6">
      <CollapsibleSection title="Primary Information" defaultOpen={true}>
        <FormField
          label="Chief Complaint"
          value={value.chief_complaint || ''}
          onChange={(val) => handleChange('chief_complaint', val)}
          placeholder="e.g., Shortness of breath for 3 days"
        />
        <FormField
          label="History of Present Illness (HPI)"
          value={value.history_of_present_illness || ''}
          onChange={(val) => handleChange('history_of_present_illness', val)}
          placeholder="e.g., Patient states that symptoms began gradually..."
        />
      </CollapsibleSection>

      <CollapsibleSection title="Medical & Family History" defaultOpen={false}>
        <FormField
          label="Past Medical History"
          value={value.past_medical_history || ''}
          onChange={(val) => handleChange('past_medical_history', val)}
          placeholder="e.g., Hypertension (diagnosed 2015)"
        />
        <FormField
          label="Family History"
          value={value.family_history || ''}
          onChange={(val) => handleChange('family_history', val)}
          placeholder="e.g., Father had MI at age 55"
        />
      </CollapsibleSection>

      <CollapsibleSection title="Medications & Allergies" defaultOpen={false}>
        <FormField
          label="Medications"
          value={value.medications || ''}
          onChange={(val) => handleChange('medications', val)}
          placeholder="e.g., Lisinopril 10mg daily"
        />
        <FormField
          label="Allergies"
          value={value.allergies || ''}
          onChange={(val) => handleChange('allergies', val)}
          placeholder="e.g., Penicillin (hives)"
        />
      </CollapsibleSection>

      <CollapsibleSection title="Social & Other History" defaultOpen={false}>
        <FormField
          label="Social History"
          value={value.social_history || ''}
          onChange={(val) => handleChange('social_history', val)}
          placeholder="e.g., Smokes 1 pack/day for 20 years"
        />
        <FormField
          label="Travel History"
          value={value.travel_history || ''}
          onChange={(val) => handleChange('travel_history', val)}
          placeholder="e.g., Recent travel to Southeast Asia"
        />
        <FormField
          label="Constitutional Symptoms"
          value={value.constitutional_symptoms || ''}
          onChange={(val) => handleChange('constitutional_symptoms', val)}
          placeholder="e.g., Fever, chills, weight loss"
        />
      </CollapsibleSection>
    </div>
  );
}
