'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { PlayIcon, CopyIcon, DownloadIcon } from 'lucide-react'
import { QueryResults } from './QueryResults'
import { AgentSteps } from './AgentSteps'

interface QueryInterfaceProps {
  disabled?: boolean
}

export function QueryInterface({ disabled = false }: QueryInterfaceProps) {
  const [question, setQuestion] = useState('')
  const [currentResult, setCurrentResult] = useState<any>(null)

  const generateQueryMutation = useMutation({
    mutationFn: async (question: string) => {
      const response = await fetch('/api/generate-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      if (!response.ok) throw new Error('Failed to generate query')
      return response.json()
    },
    onSuccess: (data) => {
      setCurrentResult(data)
      toast.success('Query generated successfully!')
    },
    onError: (error) => {
      toast.error('Failed to generate query')
      console.error(error)
    },
  })

  const executeQueryMutation = useMutation({
    mutationFn: async (sqlQuery: string) => {
      const response = await fetch('/api/execute-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql_query: sqlQuery }),
      })
      if (!response.ok) throw new Error('Failed to execute query')
      return response.json()
    },
    onSuccess: (data) => {
      setCurrentResult(prev => ({ ...prev, execution_result: data }))
      toast.success('Query executed successfully!')
    },
    onError: (error) => {
      toast.error('Failed to execute query')
      console.error(error)
    },
  })

  const exampleQuestions = [
    "What is the total pipeline value by geography?",
    "Show me win rates by market segment",
    "Which clients have the largest opportunities?",
    "What's the PPV coverage vs budget?",
    "Show pipeline by sales stage",
    "Compare this quarter vs last quarter performance"
  ]

  const handleGenerateQuery = () => {
    if (!question.trim()) {
      toast.error('Please enter a question')
      return
    }
    generateQueryMutation.mutate(question)
  }

  const handleExecuteQuery = () => {
    if (!currentResult?.final_query) {
      toast.error('No query to execute')
      return
    }
    executeQueryMutation.mutate(currentResult.final_query)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  return (
    <div className="space-y-6">
      {/* Query Input Section */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-2xl">🔍</span>
          <h2 className="text-xl font-semibold text-gray-900">Ask Questions About Your Sales Pipeline</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., What is the total pipeline value by geography?"
              className="input h-24 resize-none"
              disabled={disabled}
            />
          </div>

          <div className="flex justify-between items-center">
            <button
              onClick={handleGenerateQuery}
              disabled={disabled || generateQueryMutation.isPending || !question.trim()}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PlayIcon className="w-4 h-4" />
              <span>
                {generateQueryMutation.isPending ? 'Generating...' : 'Generate SQL Query'}
              </span>
            </button>

            {disabled && (
              <span className="text-sm text-gray-500">
                Complete setup in Data Setup and LLM Setup tabs first
              </span>
            )}
          </div>
        </div>

        {/* Example Questions */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">💡 Example Questions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {exampleQuestions.map((example, index) => (
              <button
                key={index}
                onClick={() => setQuestion(example)}
                disabled={disabled}
                className="text-left text-sm text-primary-600 hover:text-primary-700 p-2 rounded hover:bg-primary-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Query Results Section */}
      {currentResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* SQL Query Display */}
          <div className="lg:col-span-2 space-y-4">
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Generated SQL Query</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => copyToClipboard(currentResult.final_query)}
                    className="btn-secondary flex items-center space-x-1"
                  >
                    <CopyIcon className="w-4 h-4" />
                    <span>Copy</span>
                  </button>
                  <button
                    onClick={handleExecuteQuery}
                    disabled={executeQueryMutation.isPending}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <PlayIcon className="w-4 h-4" />
                    <span>
                      {executeQueryMutation.isPending ? 'Executing...' : 'Execute Query'}
                    </span>
                  </button>
                </div>
              </div>
              <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{currentResult.final_query}</code>
              </pre>
            </div>

            {/* Agent Processing Steps */}
            {currentResult.processing_log && (
              <AgentSteps steps={currentResult.processing_log} />
            )}

            {/* Query Results */}
            {currentResult.execution_result && (
              <QueryResults data={currentResult.execution_result} />
            )}
          </div>

          {/* Query Details Sidebar */}
          <div className="space-y-4">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Query Details</h3>
              
              {currentResult.explanation && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">💡 Explanation</h4>
                  <p className="text-sm text-gray-600">{currentResult.explanation}</p>
                </div>
              )}

              {currentResult.overall_confidence && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">🎯 Confidence</h4>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${currentResult.overall_confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">
                      {Math.round(currentResult.overall_confidence * 100)}%
                    </span>
                  </div>
                </div>
              )}

              {currentResult.improvements && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">🔧 Improvements Made</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {currentResult.improvements.syntax_corrections > 0 && (
                      <li>• Fixed {currentResult.improvements.syntax_corrections} syntax issues</li>
                    )}
                    {currentResult.improvements.where_enhancements > 0 && (
                      <li>• Added {currentResult.improvements.where_enhancements} WHERE clause enhancements</li>
                    )}
                    {currentResult.improvements.optimizations > 0 && (
                      <li>• Applied {currentResult.improvements.optimizations} optimizations</li>
                    )}
                    {currentResult.improvements.column_fixes > 0 && (
                      <li>• Fixed {currentResult.improvements.column_fixes} column issues</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}