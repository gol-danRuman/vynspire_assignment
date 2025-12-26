/**
 * Main page component - RAG System Interface
 * Orchestrates file upload, document management, and chat interface
 */
'use client';

import { useEffect, useState } from 'react';
import FileUpload from '@/components/FileUpload';
import DocumentList from '@/components/DocumentList';
import ChatInterface from '@/components/ChatInterface';
import { Document, getDocuments, checkHealth } from '@/lib/api';
import { AlertCircle, CheckCircle, Database, Cpu, Zap } from 'lucide-react';

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | undefined>();
  const [loading, setLoading] = useState(true);
  const [healthStatus, setHealthStatus] = useState<any>(null);

  useEffect(() => {
    loadDocuments();
    checkSystemHealth();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const status = await checkHealth();
      setHealthStatus(status);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'unhealthy' });
    }
  };

  const handleUploadSuccess = (document: Document) => {
    setDocuments((prev) => [document, ...prev]);
  };

  const handleDocumentDeleted = (documentId: number) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));
  };

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Simple RAG System
          </h1>
          <p className="text-lg text-gray-600">
            Upload documents and ask questions using AI-powered retrieval
          </p>

          {/* Health Status */}
          {healthStatus && (
            <div className="mt-4 inline-flex items-center space-x-4 px-4 py-2 bg-white rounded-lg shadow-sm">
              <div className="flex items-center space-x-1">
                {healthStatus.status === 'healthy' ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-600" />
                )}
                <span className="text-sm font-medium text-gray-700">
                  {healthStatus.status === 'healthy' ? 'All Systems Operational' : 'System Issues Detected'}
                </span>
              </div>

              <div className="flex items-center space-x-3 text-xs text-gray-600">
                <div className="flex items-center space-x-1">
                  <Database className={`w-3 h-3 ${healthStatus.database ? 'text-green-600' : 'text-red-600'}`} />
                  <span>DB</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Cpu className={`w-3 h-3 ${healthStatus.embedding_service ? 'text-green-600' : 'text-red-600'}`} />
                  <span>Embeddings</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Zap className={`w-3 h-3 ${healthStatus.llm_service ? 'text-green-600' : 'text-red-600'}`} />
                  <span>LLM</span>
                </div>
              </div>
            </div>
          )}
        </header>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Upload Section */}
          <section>
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </section>

          {/* Documents Section */}
          {!loading && (
            <section>
              <DocumentList
                documents={documents}
                selectedDocument={selectedDocument}
                onSelectDocument={setSelectedDocument}
                onDocumentDeleted={handleDocumentDeleted}
              />
            </section>
          )}

          {/* Chat Section */}
          <section>
            <ChatInterface
              documents={documents}
              selectedDocument={selectedDocument}
            />
          </section>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500">
          <p>
            Built with FastAPI, PostgreSQL, pgvector, and Next.js
          </p>
          <p className="mt-1">
            Powered by Sentence Transformers and Google Gemini
          </p>
        </footer>
      </div>
    </main>
  );
}
