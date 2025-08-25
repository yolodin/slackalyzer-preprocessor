import React, { useState, useEffect } from 'react'
import {
    Activity,
    Database,
    Brain,
    Clock,
    TrendingUp,
    AlertCircle,
    CheckCircle,
    Play, RefreshCw
} from 'lucide-react'

interface SystemStats {
    total_processed: number
    success_rate: number
    average_processing_time: number
    last_processed: string | null
}

interface SystemStatus {
    processing: boolean
    stats: SystemStats
    ml_available: boolean
    data_files: any[]
}

const HomePage: React.FC = () => {
    const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchSystemStatus()
        const interval = setInterval(fetchSystemStatus, 5000) // Update every 5 seconds
        return () => clearInterval(interval)
    }, [])

    const fetchSystemStatus = async () => {
        try {
            const response = await fetch('/api/python/api/system/status')
            const data = await response.json()
            setSystemStatus(data)
        } catch (error) {
            console.error('Error fetching system status:', error)
        } finally {
            setLoading(false)
        }
    }

    const startQuickProcessing = async () => {
        try {
            const response = await fetch('/api/python/api/processing/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data_file: 'data/standardized_slack_data.json',
                    use_ml: true,
                    use_lightweight: true,
                    max_threads: 10
                })
            })

            if (response.ok) {
                alert('Processing started! Check the Processing page for real-time updates.')
            } else {
                alert('Failed to start processing')
            }
        } catch (error) {
            console.error('Error starting processing:', error)
            alert('Error starting processing')
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="loading-spinner"></div>
                <span className="ml-3 text-gray-600">Loading system status...</span>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                        Hermes Intelligence Dashboard
                    </h1>
                    <p className="text-gray-600 mt-2">
                        AI-powered Slack thread analysis and processing system
                    </p>
                </div>
                <div className="flex space-x-3">
                    <button
                        onClick={startQuickProcessing}
                        className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                        <Play className="w-4 h-4 mr-2" />
                        Quick Process
                    </button>
                    <button
                        onClick={() => window.location.reload()}
                        className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </button>
                </div>
            </div>

            {/* System Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6 border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">System Status</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {systemStatus?.processing ? 'Processing' : 'Ready'}
                            </p>
                        </div>
                        <div className={`p-2 rounded-full ${systemStatus?.processing
                            ? 'bg-yellow-100 text-yellow-600'
                            : 'bg-green-100 text-green-600'
                            }`}>
                            {systemStatus?.processing ? (
                                <Activity className="w-6 h-6" />
                            ) : (
                                <CheckCircle className="w-6 h-6" />
                            )}
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Total Processed</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {systemStatus?.stats.total_processed || 0}
                            </p>
                        </div>
                        <div className="p-2 rounded-full bg-blue-100 text-blue-600">
                            <Database className="w-6 h-6" />
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Success Rate</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {systemStatus?.stats.success_rate.toFixed(1) || 0}%
                            </p>
                        </div>
                        <div className="p-2 rounded-full bg-green-100 text-green-600">
                            <TrendingUp className="w-6 h-6" />
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Avg Time</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {systemStatus?.stats.average_processing_time.toFixed(2) || 0}s
                            </p>
                        </div>
                        <div className="p-2 rounded-full bg-purple-100 text-purple-600">
                            <Clock className="w-6 h-6" />
                        </div>
                    </div>
                </div>
            </div>

            {/* ML Status */}
            <div className="bg-white rounded-lg shadow-sm p-6 border">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                        <Brain className="w-5 h-5 mr-2" />
                        Machine Learning Status
                    </h2>
                    <div className={`flex items-center px-3 py-1 rounded-full text-sm ${systemStatus?.ml_available
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                        }`}>
                        {systemStatus?.ml_available ? (
                            <CheckCircle className="w-4 h-4 mr-1" />
                        ) : (
                            <AlertCircle className="w-4 h-4 mr-1" />
                        )}
                        {systemStatus?.ml_available ? 'Available' : 'Unavailable'}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                        <h3 className="font-medium text-gray-900 mb-2">Classification Models</h3>
                        <ul className="text-sm text-gray-600 space-y-1">
                            <li>• DistilBERT (Transformer)</li>
                            <li>• MiniLM + Random Forest (Lightweight)</li>
                        </ul>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                        <h3 className="font-medium text-gray-900 mb-2">Summarization Models</h3>
                        <ul className="text-sm text-gray-600 space-y-1">
                            <li>• BART-large-CNN (Abstractive)</li>
                            <li>• Sentence Embeddings (Extractive)</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Data Files */}
            <div className="bg-white rounded-lg shadow-sm p-6 border">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Data Files</h2>
                {systemStatus?.data_files && systemStatus.data_files.length > 0 ? (
                    <div className="space-y-3">
                        {systemStatus.data_files.slice(0, 5).map((file, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div>
                                    <p className="font-medium text-gray-900">{file.name}</p>
                                    <p className="text-sm text-gray-600">
                                        {(file.size / 1024).toFixed(1)} KB • Modified: {new Date(file.modified).toLocaleDateString()}
                                    </p>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                                        Process
                                    </button>
                                    <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                                        View
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-600">No data files available</p>
                )}
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm p-6 border">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button
                        onClick={() => window.location.href = '/processing'}
                        className="p-4 text-left border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        <Activity className="w-6 h-6 text-primary-600 mb-2" />
                        <h3 className="font-medium text-gray-900">Start Processing</h3>
                        <p className="text-sm text-gray-600">Process latest Slack data</p>
                    </button>
                    <button
                        onClick={() => window.location.href = '/dashboard'}
                        className="p-4 text-left border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        <Database className="w-6 h-6 text-primary-600 mb-2" />
                        <h3 className="font-medium text-gray-900">View Analytics</h3>
                        <p className="text-sm text-gray-600">Browse processed results</p>
                    </button>
                </div>
            </div>
        </div>
    )
}

export default HomePage 