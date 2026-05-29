import React from 'react';
import { MorphologicalData } from '../../types/case';
import { FormField } from './FormField';
import { CollapsibleSection } from './CollapsibleSection';

interface MorphologicalFormProps {
  value: MorphologicalData;
  onChange: (data: MorphologicalData) => void;
}

export function MorphologicalForm({ value, onChange }: MorphologicalFormProps) {
  const handleChange = (field: keyof MorphologicalData, newValue: string) => {
    onChange({ ...value, [field]: newValue });
  };

  return (
    <div className="space-y-6">
      <CollapsibleSection title="Radiology & Imaging" defaultOpen={true}>
        <FormField
          label="X-Ray"
          value={value.xray || ''}
          onChange={(val) => handleChange('xray', val)}
          placeholder="e.g., CXR: Clear lung fields, normal heart size"
        />
        <FormField
          label="CT Scan"
          value={value.ct || ''}
          onChange={(val) => handleChange('ct', val)}
          placeholder="e.g., CT Abdomen: No acute intra-abdominal abnormalities"
        />
        <FormField
          label="MRI"
          value={value.mri || ''}
          onChange={(val) => handleChange('mri', val)}
          placeholder="e.g., MRI Brain: Unremarkable"
        />
        <FormField
          label="Ultrasound"
          value={value.ultrasound || ''}
          onChange={(val) => handleChange('ultrasound', val)}
          placeholder="e.g., RUQ US: Normal gallbladder, no stones"
        />
      </CollapsibleSection>

      <CollapsibleSection title="Pathology & Cytology" defaultOpen={true}>
        <FormField
          label="Pathology"
          value={value.pathology || ''}
          onChange={(val) => handleChange('pathology', val)}
          placeholder="e.g., Benign tissue, no evidence of malignancy"
        />
        <FormField
          label="Peripheral Smear"
          value={value.peripheral_smear || ''}
          onChange={(val) => handleChange('peripheral_smear', val)}
          placeholder="e.g., Normochromic, normocytic RBCs"
        />
        <FormField
          label="Biopsy"
          value={value.biopsy || ''}
          onChange={(val) => handleChange('biopsy', val)}
          placeholder="e.g., Skin biopsy: Consistent with psoriasis"
        />
        <FormField
          label="Flow Cytometry"
          value={value.flow_cytometry || ''}
          onChange={(val) => handleChange('flow_cytometry', val)}
          placeholder="e.g., Normal CD4/CD8 ratio, no aberrant populations"
        />
      </CollapsibleSection>
    </div>
  );
}
