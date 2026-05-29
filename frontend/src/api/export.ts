import { BASE_URL } from './client';

/**
 * Triggers a download of a report version as a PDF.
 * @param reportId The unique identifier of the report.
 * @returns A promise that resolves when the download is triggered.
 */
export async function downloadReportPDF(reportId: string): Promise<void> {
  const url = `${BASE_URL}/export/reports/${reportId}/pdf`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/pdf',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to download PDF: ${response.statusText}`);
  }

  const blob = await response.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = `clinical_report_v${reportId}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(blobUrl);
}

/**
 * Triggers a download of a report version as a PowerPoint presentation.
 * @param reportId The unique identifier of the report.
 * @param versionNumber The version number, used for the filename.
 */
export async function downloadReportPPTX(reportId: string, versionNumber?: number): Promise<void> {
  const url = `${BASE_URL}/export/reports/${reportId}/pptx`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Accept': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to download PPTX: ${response.statusText}`);
  }

  const blob = await response.blob();
  const blobUrl = window.URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = `clinical_report_v${versionNumber ?? reportId}.pptx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(blobUrl);
}
