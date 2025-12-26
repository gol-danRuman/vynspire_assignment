/**
 * File upload component for document submission.
 * Handles file selection, validation, and upload progress.
 */
'use client';

import React, { useState, useRef } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadDocument, Document } from '@/lib/api';

interface FileUploadProps {
  onUploadSuccess: (document: Document) => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = ['.pdf', '.txt', '.md', '.markdown'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setError(null);
    setSuccess(false);

    if (!file) return;

    // Validate file type
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(fileExt)) {
      setError(`Invalid file type. Allowed: ${allowedTypes.join(', ')}`);
      return;
    }

    // Validate file size
    if (file.size > maxSize) {
      setError(`File too large. Maximum size: ${maxSize / (1024 * 1024)}MB`);
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);

    try {
      const document = await uploadDocument(selectedFile);
      setSuccess(true);
      onUploadSuccess(document);

      // Reset after 2 seconds
      setTimeout(() => {
        setSelectedFile(null);
        setSuccess(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    setSelectedFile(null);
    setError(null);
    setSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Upload Document</h2>
        <p className="text-sm text-gray-600">
          Upload a PDF, TXT, or Markdown file to start asking questions
        </p>
      </div>

      {/* File Input */}
      <div className="mb-4">
        <label
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload className="w-10 h-10 mb-2 text-gray-400" />
            <p className="mb-2 text-sm text-gray-500">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">
              PDF, TXT, MD (MAX. 10MB)
            </p>
          </div>
          <input
            id="file-upload"
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept={allowedTypes.join(',')}
            onChange={handleFileSelect}
            disabled={uploading}
          />
        </label>
      </div>

      {/* Selected File */}
      {selectedFile && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-800">{selectedFile.name}</p>
                <p className="text-xs text-gray-600">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            {!uploading && !success && (
              <button
                onClick={handleCancel}
                className="p-1 hover:bg-blue-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-2">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-800">Document uploaded successfully!</p>
        </div>
      )}

      {/* Upload Button */}
      {selectedFile && !success && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {uploading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing...
            </span>
          ) : (
            'Upload Document'
          )}
        </button>
      )}
    </div>
  );
}
