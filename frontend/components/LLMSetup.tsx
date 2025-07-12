'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { BrainIcon, CheckCircleIcon, XCircleIcon, KeyIcon } from 'lucide-react'

interface LLMSetupProps {
  onSetupComplete: (complete: boolean) => void
}

type LLMProvider = 'gemini' | 'deepseek' | 'openai' | 'anthropic' | 'ollama'

interface LLMConfig {
  provider: LLMProvider
  apiKey: string
  model: string
}

export function LLMSetup({ onSetupComplete }: LLMSetupProps) {
  const [config, setConfig] = useState<LLMConfig>({
    provider: 'gemini',
    apiKey: '',
    model: 'gemini-2.5-pro'
  })

  // Check LLM connection status
  const { data: llmStatus, refetch: refetchLLMStatus } = useQuery({
    queryKey: ['llm-status'],
    queryFn: async () => {
      const response = await fetch('/api/llm-status')
      if (!response.ok) throw new Error('Failed to check LLM status')
      return response.json()
    },
    refetchInterval: 10000, // Check every 10 seconds
  })

  // Connect to LLM mutation
  const connectLLMMutation = useMutation({
    mutationFn: async (config: LLMConfig) => {
      const response = await fetch('/api/connect-llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      if (!response.ok) throw new Error('Failed to connect to LLM')
      return response.json()
    },
    onSuccess: (data) => {
      toast.success(`Successfully connected to ${config.provider}`)
      onSetupComplete(true)
      refetchLLMStatus()
    },
    onError: (error) => {
      toast.error('Failed to connect to LLM. Please check your API key.')
      console.error(error)
    },
  })

  // Test LLM connection mutation
  const testLLMMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/test-llm', {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to test LLM')
      return response.json()
    },
    onSuccess: (data) => {
      toast.success('LLM connection test successful!')
    },
    onError: (error) => {
      toast.error('LLM connection test failed')
      console.error(error)
    },
  })

  const handleConnect = () => {
    if (!config.apiKey.trim()) {
      toast.error('Please enter an API key')
      return
    }
    connectLLMMutation.mutate(config)
  }

  const handleTest = () => {
    testLLMMutation.mutate()
  }

  const providerInfo = {
    gemini: {
      name: 'Google Gemini',
      icon: '🔍',
      description: 'Latest Google AI models with superior reasoning capabilities',
      models: ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash'],
      keyUrl: 'https://ai.google.dev/gemini-api',
      recommended: true
    },
    deepseek: {
      name: 'DeepSeek',
      icon: '🧠',
      description: 'Advanced reasoning models optimized for coding and analysis',
      models: ['deepseek-r1', 'deepseek-coder'],
      keyUrl: 'https://platform.deepseek.com',
      recommended: true
    },
    openai: {
      name: 'OpenAI',
      icon: '🤖',
      description: 'GPT models for natural language processing',
      models: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
      keyUrl: 'https://platform.openai.com/api-keys',
      recommended: false
    },
    anthropic: {
      name: 'Anthropic Claude',
      icon: '💭',
      description: 'Constitutional AI with strong reasoning capabilities',
      models: ['claude-3-5-sonnet', 'claude-3-opus', 'claude-3-haiku'],
      keyUrl: 'https://console.anthropic.com',
      recommended: false
    },
    ollama: {
      name: 'Ollama (Local)',
      icon: '🏠',
      description: 'Run models locally with Ollama',
      models: ['llama3.1', 'mistral', 'codellama'],
      keyUrl: 'https://ollama.ai',
      recommended: false
    }
  }

  const isConnected = llmStatus?.connected

  return (
    <div className="space-y-6">
      {/* Status Banner */}
      {isConnected ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircleIcon className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">LLM Connected Successfully</span>
          </div>
          <p className="text-green-700 mt-1">
            Connected to {llmStatus.provider} using model {llmStatus.model}
          </p>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <XCircleIcon className="w-5 h-5 text-yellow-600" />
            <span className="text-yellow-800 font-medium">No LLM Connected</span>
          </div>
          <p className="text-yellow-700 mt-1">
            Please configure and connect to an LLM provider to enable natural language to SQL functionality.
          </p>
        </div>
      )}

      {/* Provider Selection */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-2xl">🧠</span>
          <h3 className="text-lg font-semibold text-gray-900">Choose LLM Provider</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {(Object.keys(providerInfo) as LLMProvider[]).map((provider) => {
            const info = providerInfo[provider]
            return (
              <div
                key={provider}
                onClick={() => setConfig(prev => ({ 
                  ...prev, 
                  provider, 
                  model: info.models[0] 
                }))}
                className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                  config.provider === provider
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${info.recommended ? 'ring-2 ring-green-200' : ''}`}
              >
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-2xl">{info.icon}</span>
                  <div>
                    <h4 className="font-medium text-gray-900">{info.name}</h4>
                    {info.recommended && (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        Recommended
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-600">{info.description}</p>
              </div>
            )
          })}
        </div>

        {/* Model Selection */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model
            </label>
            <select
              value={config.model}
              onChange={(e) => setConfig(prev => ({ ...prev, model: e.target.value }))}
              className="input"
            >
              {providerInfo[config.provider].models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>

          {/* API Key Input */}
          {config.provider !== 'ollama' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <div className="relative">
                <KeyIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="password"
                  value={config.apiKey}
                  onChange={(e) => setConfig(prev => ({ ...prev, apiKey: e.target.value }))}
                  placeholder="Enter your API key"
                  className="input pl-10"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Get your API key from:{' '}
                <a
                  href={providerInfo[config.provider].keyUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-700"
                >
                  {providerInfo[config.provider].keyUrl}
                </a>
              </p>
            </div>
          )}

          {/* Ollama Setup Instructions */}
          {config.provider === 'ollama' && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-800 mb-2">Ollama Setup Instructions:</h4>
              <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                <li>Install Ollama from https://ollama.ai</li>
                <li>Run: <code className="bg-blue-100 px-1 rounded">ollama pull {config.model}</code></li>
                <li>Start Ollama server: <code className="bg-blue-100 px-1 rounded">ollama serve</code></li>
                <li>Click "Connect to Ollama" below</li>
              </ol>
            </div>
          )}

          {/* Connect Button */}
          <div className="flex space-x-4">
            <button
              onClick={handleConnect}
              disabled={connectLLMMutation.isPending || (config.provider !== 'ollama' && !config.apiKey.trim())}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {connectLLMMutation.isPending ? 'Connecting...' : `Connect to ${providerInfo[config.provider].name}`}
            </button>

            {isConnected && (
              <button
                onClick={handleTest}
                disabled={testLLMMutation.isPending}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {testLLMMutation.isPending ? 'Testing...' : 'Test Connection'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Multi-Agent Enhancement */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-2xl">🤖</span>
          <h3 className="text-lg font-semibold text-gray-900">Multi-Agent SQL Enhancement</h3>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircleIcon className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">Multi-Agent System Active</span>
          </div>
          <p className="text-green-700 mt-1">
            Your SQL queries will be automatically enhanced by our multi-agent system including:
          </p>
          <ul className="text-green-700 mt-2 space-y-1 text-sm">
            <li>• DB2 Syntax Validation & Conversion</li>
            <li>• WHERE Clause Enhancement</li>
            <li>• Query Optimization</li>
            <li>• Column Validation & Substitution</li>
            <li>• Automatic SQL Regeneration</li>
          </ul>
        </div>
      </div>
    </div>
  )
}