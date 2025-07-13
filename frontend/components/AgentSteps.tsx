'use client'

import { CheckCircle, XCircle, Info } from 'lucide-react'

interface AgentStep {
  agent: string
  success: boolean
  message: string
  confidence?: number
  enhancements?: string[]
  optimizations?: string[]
  missing_columns?: string[]
  substitutions?: string[]
}

interface AgentStepsProps {
  steps: AgentStep[]
}

export function AgentSteps({ steps }: AgentStepsProps) {
  const getAgentIcon = (agentName: string) => {
    switch (agentName) {
      case 'DB2SyntaxValidator':
        return '🔧'
      case 'WhereClauseEnhancer':
        return '🎯'
      case 'QueryOptimizer':
        return '⚡'
      case 'ColumnValidation':
        return '📋'
      case 'SQLRegeneration':
        return '🔄'
      default:
        return '🤖'
    }
  }

  const getAgentDisplayName = (agentName: string) => {
    switch (agentName) {
      case 'DB2SyntaxValidator':
        return 'DB2 Syntax Validator'
      case 'WhereClauseEnhancer':
        return 'WHERE Clause Enhancer'
      case 'QueryOptimizer':
        return 'Query Optimizer'
      case 'ColumnValidation':
        return 'Column Validation'
      case 'SQLRegeneration':
        return 'SQL Regeneration'
      default:
        return agentName
    }
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-4">
        <span className="text-2xl">🤖</span>
        <h3 className="text-lg font-semibold text-gray-900">Multi-Agent Processing Steps</h3>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                {step.success ? (
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-lg">{getAgentIcon(step.agent)}</span>
                  <h4 className="text-sm font-medium text-gray-900">
                    {index + 1}. {getAgentDisplayName(step.agent)}
                  </h4>
                  {step.confidence && (
                    <div className="flex items-center space-x-1">
                      <span className="text-xs text-gray-500">Confidence:</span>
                      <span className="text-xs font-medium text-primary-600">
                        {Math.round(step.confidence * 100)}%
                      </span>
                    </div>
                  )}
                </div>
                
                <p className="text-sm text-gray-600 mb-2">{step.message}</p>
                
                {/* Display additional details */}
                {step.enhancements && step.enhancements.length > 0 && (
                  <div className="mt-2">
                    <h5 className="text-xs font-medium text-gray-700 mb-1">Enhancements:</h5>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {step.enhancements.map((enhancement, idx) => (
                        <li key={idx} className="flex items-start space-x-1">
                          <span className="text-green-500 mt-0.5">•</span>
                          <span>{enhancement}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {step.optimizations && step.optimizations.length > 0 && (
                  <div className="mt-2">
                    <h5 className="text-xs font-medium text-gray-700 mb-1">Optimizations:</h5>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {step.optimizations.map((optimization, idx) => (
                        <li key={idx} className="flex items-start space-x-1">
                          <span className="text-blue-500 mt-0.5">•</span>
                          <span>{optimization}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {step.missing_columns && step.missing_columns.length > 0 && (
                  <div className="mt-2">
                    <h5 className="text-xs font-medium text-gray-700 mb-1">Missing Columns:</h5>
                    <ul className="text-xs text-red-600 space-y-1">
                      {step.missing_columns.map((column, idx) => (
                        <li key={idx} className="flex items-start space-x-1">
                          <span className="text-red-500 mt-0.5">•</span>
                          <span>{column}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {step.substitutions && step.substitutions.length > 0 && (
                  <div className="mt-2">
                    <h5 className="text-xs font-medium text-gray-700 mb-1">Column Substitutions:</h5>
                    <ul className="text-xs text-yellow-600 space-y-1">
                      {step.substitutions.map((substitution, idx) => (
                        <li key={idx} className="flex items-start space-x-1">
                          <span className="text-yellow-500 mt-0.5">•</span>
                          <span>{substitution}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {steps.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Info className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p>No processing steps available</p>
        </div>
      )}
    </div>
  )
}