import { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Clock, Database, RefreshCw } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type UploadType = 'delays' | 'failures' | 'maintenance' | 'manuals';

const HistoricalDataUpload: React.FC = () => {
  const [uploadType, setUploadType] = useState<UploadType>('delays');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [uploadHistory, setUploadHistory] = useState<Array<{ type: string; count: number; timestamp: string }>>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'Please select a file first' });
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10_000_000) {
      setMessage({ type: 'error', text: 'File too large. Maximum 10MB allowed' });
      return;
    }

    if (file.size === 0) {
      setMessage({ type: 'error', text: 'Cannot upload empty file' });
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      let endpoint = '';
      switch (uploadType) {
        case 'delays':
          endpoint = `${API_BASE}/historical/delays/upload`;
          break;
        case 'failures':
          endpoint = `${API_BASE}/historical/failures/upload`;
          break;
        case 'maintenance':
          endpoint = `${API_BASE}/historical/maintenance/upload`;
          break;
        case 'manuals':
          endpoint = `${API_BASE}/rag/upload`;
          break;
      }

      const response = await axios.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          setUploadProgress(percentCompleted);
        },
        timeout: 120000, // 2 minute timeout for large files
      });

      const recordsCount = response.data.records_imported || response.data.num_chunks || 0;
      
      setMessage({
        type: 'success',
        text: `Successfully uploaded ${file.name}. ${recordsCount} records imported.`,
      });

      // Add to upload history
      setUploadHistory((prev) => [
        {
          type: uploadType,
          count: recordsCount,
          timestamp: new Date().toLocaleString(),
        },
        ...prev.slice(0, 9), // Keep last 10
      ]);

      // Reset file input
      setFile(null);
      setUploadProgress(0);
      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error: any) {
      console.error('Upload failed:', error);
      
      let errorMessage = 'Upload failed. Please check file format and try again.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Upload timeout. File may be too large or server is slow.';
      } else if (error.response) {
        errorMessage = error.response?.data?.detail || errorMessage;
      } else if (error.request) {
        errorMessage = 'Network error. Please check your connection and try again.';
      }
      
      setMessage({
        type: 'error',
        text: errorMessage,
      });
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const getUploadTypeInfo = (type: UploadType) => {
    switch (type) {
      case 'delays':
        return {
          title: 'Equipment Delay Logs',
          description: 'Upload historical equipment delay records',
          format: 'CSV: equipment_id, delay_date, duration_hours, reason, impact, resolved',
          example: 'AC-001, 2024-01-15, 4.5, Bearing failure, Production stopped, true',
        };
      case 'failures':
        return {
          title: 'Failure Analysis Reports',
          description: 'Upload failure analysis and breakdown reports',
          format: 'CSV: equipment_id, failure_date, failure_type, root_cause, downtime_hours, repair_cost, parts_replaced',
          example: 'CF-003, 2024-02-20, Motor failure, Overheating, 8.0, 1200, Motor;Bearing',
        };
      case 'maintenance':
        return {
          title: 'Historical Maintenance Logs',
          description: 'Upload past maintenance activity records',
          format: 'CSV: equipment_id, maintenance_date, maintenance_type, technician, actions_taken, parts_used, duration_hours',
          example: 'RM-005, 2024-03-10, Preventive, John Doe, Lubrication and inspection, Grease, 2.0',
        };
      case 'manuals':
        return {
          title: 'Equipment Manuals & SOPs',
          description: 'Upload equipment manuals and maintenance procedures (PDF)',
          format: 'PDF format only',
          example: 'compressor_manual.pdf, maintenance_sop_v2.pdf',
        };
    }
  };

  const typeInfo = getUploadTypeInfo(uploadType);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-xs font-mono tracking-widest mb-1" style={{ color: 'var(--accent-cyan)' }}>
          📤 HISTORICAL DATA IMPORT
        </h2>
        <p className="text-2xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
          Import records and documentation to enhance AI analysis
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 flex-1">
        {/* Left Column - Upload Form */}
        <div className="flex flex-col">
          <div 
            className="rounded-sm p-4 border flex-1"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-mono uppercase" style={{ color: 'var(--text-primary)' }}>
                Upload Data
              </h3>
              <Database className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
            </div>

            {/* Upload Type Selection */}
            <div className="mb-4">
              <label className="block text-2xs font-mono uppercase mb-2" style={{ color: 'var(--text-tertiary)' }}>
                Data Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { key: 'delays', label: 'Delay Logs' },
                  { key: 'failures', label: 'Failure Reports' },
                  { key: 'maintenance', label: 'Maintenance Logs' },
                  { key: 'manuals', label: 'Manuals/SOPs' },
                ].map((type) => (
                  <button
                    key={type.key}
                    onClick={() => setUploadType(type.key as UploadType)}
                    className="px-3 py-2 rounded-sm text-xs font-mono transition-all"
                    style={{
                      backgroundColor: uploadType === type.key ? 'var(--accent-cyan)' : 'var(--bg-elevated)',
                      color: uploadType === type.key ? '#000' : 'var(--text-primary)',
                      border: `1px solid ${uploadType === type.key ? 'var(--accent-cyan)' : 'var(--border-default)'}`,
                    }}
                  >
                    {type.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Type Info */}
            <div 
              className="mb-4 p-3 rounded-sm border"
              style={{
                backgroundColor: 'var(--bg-base)',
                borderColor: 'var(--accent-cyan)'
              }}
            >
              <h4 className="text-xs font-mono mb-1" style={{ color: 'var(--accent-cyan)' }}>
                {typeInfo.title}
              </h4>
              <p className="text-2xs font-sans mb-2" style={{ color: 'var(--text-secondary)' }}>
                {typeInfo.description}
              </p>
              <div className="text-2xs">
                <div className="font-mono uppercase mb-1" style={{ color: 'var(--text-tertiary)' }}>Format:</div>
                <div 
                  className="font-mono p-2 rounded-sm mb-2"
                  style={{ 
                    backgroundColor: 'var(--bg-elevated)', 
                    color: 'var(--text-primary)',
                    fontSize: '10px'
                  }}
                >
                  {typeInfo.format}
                </div>
                <div className="font-mono uppercase mb-1" style={{ color: 'var(--text-tertiary)' }}>Example:</div>
                <div 
                  className="font-mono p-2 rounded-sm"
                  style={{ 
                    backgroundColor: 'var(--bg-elevated)', 
                    color: 'var(--text-secondary)',
                    fontSize: '9px',
                    lineHeight: '1.3'
                  }}
                >
                  {typeInfo.example}
                </div>
              </div>
            </div>

            {/* File Upload */}
            <div className="mb-4">
              <label className="block text-2xs font-mono uppercase mb-2" style={{ color: 'var(--text-tertiary)' }}>
                Select File {uploadType === 'manuals' ? '(PDF)' : '(CSV or JSON)'}
              </label>
              <div className="relative">
                <input
                  id="file-upload"
                  type="file"
                  accept={uploadType === 'manuals' ? '.pdf' : '.csv,.json'}
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div 
                  className="px-3 py-2 rounded-sm border flex items-center justify-between"
                  style={{
                    backgroundColor: 'var(--bg-elevated)',
                    borderColor: 'var(--border-default)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  <span className="text-xs font-mono">
                    {file ? file.name : 'Choose file...'}
                  </span>
                  <Upload className="w-3.5 h-3.5" style={{ color: 'var(--text-tertiary)' }} />
                </div>
              </div>
              {file && (
                <p className="mt-2 text-2xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                  Size: <span style={{ color: 'var(--text-primary)' }}>{(file.size / 1024).toFixed(1)} KB</span>
                </p>
              )}
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full py-2.5 px-4 rounded-sm text-xs font-mono uppercase transition-all flex items-center justify-center space-x-2"
              style={{
                backgroundColor: !file || uploading ? '#4b5563' : 'var(--accent-cyan)',
                color: !file || uploading ? '#9ca3af' : '#000',
                cursor: !file || uploading ? 'not-allowed' : 'pointer',
                opacity: !file || uploading ? 0.5 : 1,
              }}
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Uploading... {uploadProgress}%</span>
                </>
              ) : (
                <>
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload</span>
                </>
              )}
            </button>

            {/* Progress Bar */}
            {uploading && uploadProgress > 0 && (
              <div className="mt-3">
                <div 
                  className="w-full h-1.5 rounded-full overflow-hidden"
                  style={{ backgroundColor: 'var(--bg-elevated)' }}
                >
                  <div
                    className="h-full transition-all duration-300"
                    style={{ 
                      width: `${uploadProgress}%`,
                      backgroundColor: 'var(--accent-cyan)'
                    }}
                  ></div>
                </div>
              </div>
            )}

            {/* Message */}
            {message && (
              <div
                className="mt-4 p-3 rounded-sm border flex items-start space-x-2"
                style={{
                  backgroundColor: message.type === 'success' ? '#15803d20' : '#7f1d1d20',
                  borderColor: message.type === 'success' ? '#22c55e' : '#ef4444',
                }}
              >
                {message.type === 'success' ? (
                  <CheckCircle className="w-4 h-4 flex-shrink-0" style={{ color: '#22c55e' }} />
                ) : (
                  <AlertCircle className="w-4 h-4 flex-shrink-0" style={{ color: '#ef4444' }} />
                )}
                <span 
                  className="text-xs font-sans"
                  style={{ color: message.type === 'success' ? '#22c55e' : '#ef4444' }}
                >
                  {message.text}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - History & Guidelines */}
        <div className="flex flex-col space-y-4">
          {/* Upload History */}
          <div 
            className="rounded-sm p-4 border"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-mono uppercase" style={{ color: 'var(--text-primary)' }}>
                Recent Uploads
              </h3>
              <Clock className="w-4 h-4" style={{ color: 'var(--accent-orange)' }} />
            </div>
            {uploadHistory.length === 0 ? (
              <div className="text-center py-6">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-30" style={{ color: 'var(--text-tertiary)' }} />
                <p className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>No uploads yet</p>
              </div>
            ) : (
              <div className="space-y-2">
                {uploadHistory.map((item, index) => (
                  <div 
                    key={index} 
                    className="flex items-center justify-between text-xs border-b pb-2"
                    style={{ borderColor: 'var(--border-subtle)' }}
                  >
                    <div>
                      <span className="font-mono capitalize" style={{ color: 'var(--text-primary)' }}>
                        {item.type}
                      </span>
                      <span className="font-mono ml-2" style={{ color: 'var(--text-tertiary)' }}>
                        ({item.count})
                      </span>
                    </div>
                    <span className="text-2xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                      {item.timestamp}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Guidelines */}
          <div 
            className="rounded-sm p-4 border flex-1"
            style={{
              backgroundColor: 'var(--bg-surface)',
              borderColor: 'var(--border-default)'
            }}
          >
            <h3 className="text-xs font-mono uppercase mb-3" style={{ color: 'var(--text-primary)' }}>
              📋 Upload Guidelines
            </h3>
            <ul className="space-y-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
              <li className="flex items-start">
                <span style={{ color: 'var(--accent-cyan)' }} className="mr-2">•</span>
                <span className="font-sans">CSV files must include headers matching the required format</span>
              </li>
              <li className="flex items-start">
                <span style={{ color: 'var(--accent-cyan)' }} className="mr-2">•</span>
                <span className="font-sans">Equipment IDs must match: AC-001, AC-002, CF-003, RM-005, CM-007</span>
              </li>
              <li className="flex items-start">
                <span style={{ color: 'var(--accent-cyan)' }} className="mr-2">•</span>
                <span className="font-sans">Dates should be in YYYY-MM-DD format</span>
              </li>
              <li className="flex items-start">
                <span style={{ color: 'var(--accent-cyan)' }} className="mr-2">•</span>
                <span className="font-sans">Multiple parts should be separated by semicolons (;)</span>
              </li>
              <li className="flex items-start">
                <span style={{ color: 'var(--accent-cyan)' }} className="mr-2">•</span>
                <span className="font-sans">PDF manuals will be processed and indexed for AI retrieval</span>
              </li>
              <li className="flex items-start">
                <span style={{ color: 'var(--accent-cyan)' }} className="mr-2">•</span>
                <span className="font-sans">Larger files may take a few minutes to process</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoricalDataUpload;
