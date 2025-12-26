/**
 * Chat interface component for asking questions.
 * Displays conversation history and handles user interactions.
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Loader2, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { askQuestion, QuestionResponse, Document } from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: QuestionResponse['sources'];
  timestamp: Date;
}

interface ChatInterfaceProps {
  documents: Document[];
  selectedDocument?: Document;
}

export default function ChatInterface({ documents, selectedDocument }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) return;

    if (documents.length === 0) {
      setError('Please upload a document first');
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await askQuestion(
        userMessage.content,
        selectedDocument?.id
      );

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer');
      // Remove the user message if request failed
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="w-full max-w-4xl mx-auto h-[600px] flex flex-col bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <h2 className="text-xl font-bold text-gray-800">Chat Interface</h2>
        {selectedDocument ? (
          <div className="flex items-center mt-2 text-sm text-gray-600">
            <FileText className="w-4 h-4 mr-2" />
            <span>Querying: {selectedDocument.filename}</span>
          </div>
        ) : documents.length > 0 ? (
          <p className="text-sm text-gray-600 mt-1">
            Querying all {documents.length} document{documents.length !== 1 ? 's' : ''}
          </p>
        ) : (
          <p className="text-sm text-amber-600 mt-1">
            Please upload a document to start chatting
          </p>
        )}
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <FileText className="w-16 h-16 mx-auto mb-4" />
              <p className="text-lg font-medium">No messages yet</p>
              <p className="text-sm mt-2">
                {documents.length > 0
                  ? 'Ask a question about your documents'
                  : 'Upload a document to get started'}
              </p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="prose prose-sm max-w-none">
                  {message.role === 'user' ? (
                    <p className="text-white m-0">{message.content}</p>
                  ) : (
                    <ReactMarkdown className="text-gray-800">
                      {message.content}
                    </ReactMarkdown>
                  )}
                </div>

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-gray-600 mb-2">
                      Sources ({message.sources.length}):
                    </p>
                    <div className="space-y-2">
                      {message.sources.slice(0, 3).map((source, idx) => (
                        <div
                          key={idx}
                          className="text-xs bg-white rounded p-2 border border-gray-200"
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-gray-700">
                              {source.filename}
                            </span>
                            <span className="text-gray-500">
                              {Math.round(source.similarity * 100)}% match
                            </span>
                          </div>
                          <p className="text-gray-600 line-clamp-2">
                            {source.content_preview}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <p
                  className={`text-xs mt-2 ${
                    message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}
                >
                  {formatTime(message.timestamp)}
                </p>
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <Loader2 className="w-6 h-6 text-gray-600 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              documents.length > 0
                ? 'Ask a question about your documents...'
                : 'Upload a document first...'
            }
            disabled={isLoading || documents.length === 0}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || documents.length === 0}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
