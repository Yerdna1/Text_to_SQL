'use client'

import { useState } from 'react'
import { QueryInterface } from '@/components/QueryInterface'
import { DataSetup } from '@/components/DataSetup'
import { LLMSetup } from '@/components/LLMSetup'

export default function HomePage() {
  const [currentTab, setCurrentTab] = useState('query')
  const [setupComplete, setSetupComplete] = useState({
    data: false,
    llm: false
  })

  const tabs = [
    { id: 'query', name: 'Query Interface', icon: '🔍' },
    { id: 'data', name: 'Data Setup', icon: '📊' },
    { id: 'llm', name: 'LLM Setup', icon: '🧠' },
  ]

  return (
    <div className="space-y-6">
      {/* Status Banner */}
      {(!setupComplete.data || !setupComplete.llm) && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-yellow-600">⚠️</span>
            <span className="text-yellow-800 font-medium">Setup Required</span>
          </div>
          <p className="text-yellow-700 mt-1">
            Please complete the data and LLM setup before using the query interface.
          </p>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setCurrentTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                currentTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {currentTab === 'query' && (
          <QueryInterface disabled={!setupComplete.data || !setupComplete.llm} />
        )}
        {currentTab === 'data' && (
          <DataSetup onSetupComplete={(complete) => setSetupComplete(prev => ({ ...prev, data: complete }))} />
        )}
        {currentTab === 'llm' && (
          <LLMSetup onSetupComplete={(complete) => setSetupComplete(prev => ({ ...prev, llm: complete }))} />
        )}
      </div>
    </div>
  )
}