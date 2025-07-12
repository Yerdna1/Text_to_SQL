'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { UploadIcon, FolderIcon, DatabaseIcon, CheckCircleIcon } from 'lucide-react'

interface DataSetupProps {
  onSetupComplete: (complete: boolean) => void
}

export function DataSetup({ onSetupComplete }: DataSetupProps) {
  const [activeTab, setActiveTab] = useState<'upload' | 'demo'>('upload')
  const [files, setFiles] = useState<FileList | null>(null)

  // Check if data is already loaded
  const { data: dataStatus, refetch: refetchDataStatus } = useQuery({
    queryKey: ['data-status'],
    queryFn: async () => {
      const response = await fetch('/api/data-status')
      if (!response.ok) throw new Error('Failed to check data status')
      return response.json()
    },
    refetchInterval: 5000, // Check every 5 seconds
  })

  // Upload files mutation
  const uploadFilesMutation = useMutation({
    mutationFn: async (files: FileList) => {
      const formData = new FormData()
      Array.from(files).forEach((file) => {
        formData.append('files', file)
      })
      
      const response = await fetch('/api/upload-data', {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) throw new Error('Failed to upload files')
      return response.json()
    },
    onSuccess: (data) => {
      toast.success(`Successfully uploaded ${data.files_processed} files`)
      onSetupComplete(true)
      refetchDataStatus()
    },
    onError: (error) => {
      toast.error('Failed to upload files')
      console.error(error)
    },
  })

  // Load demo data mutation
  const loadDemoMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/load-demo-data', {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to load demo data')
      return response.json()
    },
    onSuccess: (data) => {
      toast.success(`Demo data loaded: ${data.tables_created} tables created`)
      onSetupComplete(true)
      refetchDataStatus()
    },
    onError: (error) => {
      toast.error('Failed to load demo data')
      console.error(error)
    },
  })

  const handleFileUpload = () => {
    if (!files || files.length === 0) {
      toast.error('Please select files to upload')
      return
    }
    uploadFilesMutation.mutate(files)
  }

  const handleLoadDemo = () => {
    loadDemoMutation.mutate()
  }

  const isDataLoaded = dataStatus?.tables_loaded > 0

  return (
    <div className="space-y-6">
      {/* Status Banner */}
      {isDataLoaded ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircleIcon className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">Data Loaded Successfully</span>
          </div>
          <p className="text-green-700 mt-1">
            {dataStatus.tables_loaded} tables loaded with {dataStatus.total_rows} total rows
          </p>
        </div>
      ) : (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <DatabaseIcon className="w-5 h-5 text-blue-600" />
            <span className="text-blue-800 font-medium">No Data Loaded</span>
          </div>
          <p className="text-blue-700 mt-1">
            Please upload your MQT data files or load demo data to get started.
          </p>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('upload')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'upload'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <UploadIcon className="w-4 h-4 inline mr-2" />
            Upload Files
          </button>
          <button
            onClick={() => setActiveTab('demo')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'demo'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <DatabaseIcon className="w-4 h-4 inline mr-2" />
            Demo Data
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'upload' && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-2xl">📤</span>
            <h3 className="text-lg font-semibold text-gray-900">Upload MQT Data Files</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">
                Select CSV or Excel Files
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setFiles(e.target.files)}
                  className="hidden"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center space-y-2"
                >
                  <FolderIcon className="w-8 h-8 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    Click to select files or drag and drop
                  </span>
                  <span className="text-xs text-gray-500">
                    Supports CSV and Excel files (.csv, .xlsx, .xls)
                  </span>
                </label>
              </div>
            </div>

            {files && files.length > 0 && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Files:</h4>
                <ul className="space-y-1">
                  {Array.from(files).map((file, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-center space-x-2">
                      <span>📄</span>
                      <span>{file.name}</span>
                      <span className="text-gray-400">
                        ({(file.size / (1024 * 1024)).toFixed(1)} MB)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <button
              onClick={handleFileUpload}
              disabled={uploadFilesMutation.isPending || !files || files.length === 0}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploadFilesMutation.isPending ? 'Uploading...' : 'Upload Files'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'demo' && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-2xl">🎯</span>
            <h3 className="text-lg font-semibold text-gray-900">Load Demo Data</h3>
          </div>

          <div className="space-y-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-800 mb-2">Demo Dataset Includes:</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Consulting Pipeline Data (100+ opportunities)</li>
                <li>• Software SaaS Opportunities</li>
                <li>• Budget and Revenue Actuals</li>
                <li>• Geographic and Market Segmentation</li>
                <li>• Multiple Sales Stages and Time Periods</li>
              </ul>
            </div>

            <p className="text-sm text-gray-600">
              This will create sample IBM sales pipeline data that you can use to test 
              the natural language to SQL functionality without uploading your own files.
            </p>

            <button
              onClick={handleLoadDemo}
              disabled={loadDemoMutation.isPending}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loadDemoMutation.isPending ? 'Loading Demo Data...' : 'Load Demo Data'}
            </button>
          </div>
        </div>
      )}

      {/* Data Dictionary Section */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-2xl">📚</span>
          <h3 className="text-lg font-semibold text-gray-900">Data Dictionary</h3>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircleIcon className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">Built-in Data Dictionary Loaded</span>
          </div>
          <p className="text-green-700 mt-1">
            Comprehensive IBM sales pipeline data dictionary with column descriptions, 
            relationships, and business context is automatically available.
          </p>
        </div>
      </div>
    </div>
  )
}