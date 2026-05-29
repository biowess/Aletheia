export interface AppSetting {
  key: string;
  value: string;
  value_type: string;
  label: string;
  description?: string;
  updated_at: string;
}

export interface AppSettingsBulk {
  settings: AppSetting[];
}
