'use client'

import { useState } from 'react'
import { DownloadIcon } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

interface QueryResultsProps {
  data: {
    results: any[]
    columns: string[]
    row_count: number
  }
}

export function QueryResults({ data }: QueryResultsProps) {
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table')

  const downloadCSV = () => {
    if (!data.results.length) return

    const headers = data.columns.join(',')
    const rows = data.results.map(row => 
      data.columns.map(col => {
        const value = row[col]
        // Escape commas and quotes in CSV
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value
      }).join(',')
    )
    
    const csvContent = [headers, ...rows].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = 'query_results.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  const canCreateChart = () => {
    // Simple heuristic: if we have numeric columns and categories, we can chart
    if (data.results.length === 0) return false
    
    const firstRow = data.results[0]
    const numericColumns = data.columns.filter(col => 
      typeof firstRow[col] === 'number'
    )
    const categoryColumns = data.columns.filter(col => 
      typeof firstRow[col] === 'string'
    )
    
    return numericColumns.length > 0 && categoryColumns.length > 0
  }

  const getChartData = () => {
    if (!canCreateChart()) return []
    
    const firstRow = data.results[0]
    const categoryCol = data.columns.find(col => typeof firstRow[col] === 'string')
    const numericCols = data.columns.filter(col => typeof firstRow[col] === 'number')
    
    return data.results.slice(0, 10).map(row => ({
      category: row[categoryCol!],
      ...numericCols.reduce((acc, col) => ({ ...acc, [col]: row[col] }), {})
    }))
  }

  const getNumericColumns = () => {
    if (data.results.length === 0) return []
    const firstRow = data.results[0]
    return data.columns.filter(col => typeof firstRow[col] === 'number')
  }

  const formatValue = (value: any) => {
    if (typeof value === 'number') {
      if (value > 1000000) {
        return `${(value / 1000000).toFixed(1)}M`
      } else if (value > 1000) {
        return `${(value / 1000).toFixed(1)}K`
      }
      return value.toLocaleString()
    }
    return value
  }

  const chartData = getChartData()
  const numericColumns = getNumericColumns()

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-gray-900">📊 Query Results</h3>
          <span className="text-sm text-gray-500">
            {data.row_count} rows × {data.columns.length} columns
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {canCreateChart() && (
            <div className="flex rounded-lg border border-gray-300">
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-1 text-sm rounded-l-lg ${
                  viewMode === 'table' 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Table
              </button>
              <button
                onClick={() => setViewMode('chart')}
                className={`px-3 py-1 text-sm rounded-r-lg ${
                  viewMode === 'chart' 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Chart
              </button>
            </div>
          )}
          
          <button
            onClick={downloadCSV}
            className="btn-secondary flex items-center space-x-2"
          >
            <DownloadIcon className="w-4 h-4" />
            <span>Download CSV</span>
          </button>
        </div>
      </div>

      {viewMode === 'table' ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {data.columns.map((column) => (
                  <th
                    key={column}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.results.slice(0, 100).map((row, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  {data.columns.map((column) => (
                    <td
                      key={column}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {formatValue(row[column])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          
          {data.results.length > 100 && (
            <div className="mt-4 text-center text-sm text-gray-500">
              Showing first 100 rows of {data.row_count} total rows
            </div>
          )}
        </div>
      ) : (
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            {numericColumns.length === 1 ? (
              <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip formatter={(value) => [formatValue(value), numericColumns[0]]} />
                <Bar dataKey={numericColumns[0]} fill="#3b82f6" />
              </BarChart>
            ) : (
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                {numericColumns.slice(0, 3).map((col, index) => (
                  <Line 
                    key={col}
                    type="monotone" 
                    dataKey={col} 
                    stroke={['#3b82f6', '#ef4444', '#10b981'][index]} 
                    strokeWidth={2}
                  />
                ))}
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}