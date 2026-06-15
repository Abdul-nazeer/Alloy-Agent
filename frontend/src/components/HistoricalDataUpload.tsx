import React, { useState } from 'react';
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
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Historical Data Import</h2>
        <p className="text-gray-600">Import historical records and documentation to enhance AI analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Data</h3>

          {/* Upload Type Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Data Type</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setUploadType('delays')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  uploadType === 'delays'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Delay Logs
              </button>
              <button
                onClick={() => setUploadType('failures')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  uploadType === 'failures'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Failure Reports
              </button>
              <button
                onClick={() => setUploadType('maintenance')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  uploadType === 'maintenance'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Maintenance Logs
              </button>
              <button
                onClick={() => setUploadType('manuals')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  uploadType === 'manuals'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Manuals/SOPs
              </button>
            </div>
          </div>

          {/* Type Info */}
          <div className="mb-4 p-4 bg-blue-50 rounded-md">
            <h4 className="text-sm font-semibold text-blue-900 mb-1">{typeInfo.title}</h4>
            <p className="text-sm text-blue-800 mb-2">{typeInfo.description}</p>
            <div className="text-xs text-blue-700">
              <div className="font-semibold mb-1">Format:</div>
              <div className="font-mono bg-white p-2 rounded">{typeInfo.format}</div>
              <div className="font-semibold mt-2 mb-1">Example:</div>
              <div className="font-mono bg-white p-2 rounded text-xs">{typeInfo.example}</div>
            </div>
          </div>

          {/* File Upload */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select File {uploadType === 'manuals' ? '(PDF)' : '(CSV or JSON)'}
            </label>
            <input
              id="file-upload"
              type="file"
              accept={uploadType === 'manuals' ? '.pdf' : '.csv,.json'}
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
            {file && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: <span className="font-semibold">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className={`w-full py-2 px-4 rounded-md text-white font-medium ${
              !file || uploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading ? `Uploading... ${uploadProgress}%` : 'Upload'}
          </button>

          {/* Progress Bar */}
          {uploading && uploadProgress > 0 && (
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Message */}
          {message && (
            <div
              className={`mt-4 p-3 rounded-md ${
                message.type === 'success'
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {message.text}
            </div>
          )}
        </div>

        {/* Upload History & Guidelines */}
        <div className="space-y-6">
          {/* Upload History */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Uploads</h3>
            {uploadHistory.length === 0 ? (
              <p className="text-sm text-gray-500">No uploads yet</p>
            ) : (
              <div className="space-y-2">
                {uploadHistory.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm border-b pb-2">
                    <div>
                      <span className="font-medium text-gray-900 capitalize">{item.type}</span>
                      <span className="text-gray-500 ml-2">({item.count} records)</span>
                    </div>
                    <span className="text-xs text-gray-400">{item.timestamp}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Guidelines */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Upload Guidelines</h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>CSV files must include headers matching the required format</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Equipment IDs must match: AC-001, AC-002, CF-003, RM-005, CM-007</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Dates should be in YYYY-MM-DD format</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Multiple parts should be separated by semicolons (;)</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>PDF manuals will be processed and indexed for AI retrieval</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span>Larger files may take a few minutes to process</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoricalDataUpload;
