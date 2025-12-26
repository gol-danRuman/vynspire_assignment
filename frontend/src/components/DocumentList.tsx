/**
 * Document list component showing uploaded documents.
 * Allows selection and deletion of documents.
 */
'use client';

import React, { useState } from 'react';
import { FileText, Trash2, Calendar, FileCode } from 'lucide-react';
import { Document, deleteDocument } from '@/lib/api';

interface DocumentListProps {
  documents: Document[];
  selectedDocument?: Document;
  onSelectDocument: (document: Document | undefined) => void;
  onDocumentDeleted: (documentId: number) => void;
}

export default function DocumentList({
  documents,
  selectedDocument,
  onSelectDocument,
  onDocumentDeleted,
}: DocumentListProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (e: React.MouseEvent, documentId: number) => {
    e.stopPropagation();

    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    setDeletingId(documentId);

    try {
      await deleteDocument(documentId);
      onDocumentDeleted(documentId);

      // Clear selection if deleted document was selected
      if (selectedDocument?.id === documentId) {
        onSelectDocument(undefined);
      }
    } catch (err) {
      alert('Failed to delete document: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setDeletingId(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getFileIcon = (fileType: string) => {
    return <FileText className="w-5 h-5" />;
  };

  if (documents.length === 0) {
    return (
      <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Uploaded Documents</h2>
        <div className="flex flex-col items-center justify-center py-8 text-gray-400">
          <FileCode className="w-16 h-16 mb-4" />
          <p className="text-lg font-medium">No documents uploaded</p>
          <p className="text-sm mt-2">Upload a document to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800">Uploaded Documents</h2>
        <span className="text-sm text-gray-600">{documents.length} document{documents.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="space-y-2">
        {documents.map((doc) => (
          <div
            key={doc.id}
            onClick={() => onSelectDocument(selectedDocument?.id === doc.id ? undefined : doc)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              selectedDocument?.id === doc.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div
                  className={`p-2 rounded-lg ${
                    selectedDocument?.id === doc.id ? 'bg-blue-100' : 'bg-gray-100'
                  }`}
                >
                  {getFileIcon(doc.file_type)}
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-800 truncate">{doc.filename}</h3>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-xs text-gray-600">
                    <span className="flex items-center">
                      <Calendar className="w-3 h-3 mr-1" />
                      {formatDate(doc.upload_date)}
                    </span>
                    <span>{formatFileSize(doc.file_size)}</span>
                    <span>{doc.chunk_count} chunks</span>
                    <span className="uppercase">{doc.file_type.replace('.', '')}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={(e) => handleDelete(e, doc.id)}
                disabled={deletingId === doc.id}
                className="ml-2 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                title="Delete document"
              >
                {deletingId === doc.id ? (
                  <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Trash2 className="w-5 h-5" />
                )}
              </button>
            </div>

            {selectedDocument?.id === doc.id && (
              <div className="mt-3 pt-3 border-t border-blue-200">
                <p className="text-xs text-blue-700 font-medium">
                  ✓ Questions will be answered using this document only
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedDocument && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Tip:</strong> Click the selected document again to query all documents
          </p>
        </div>
      )}
    </div>
  );
}
