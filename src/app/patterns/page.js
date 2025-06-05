'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Patterns() {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatterns();
  }, []);


const fetchPatterns = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/patterns');
    const data = await response.json();
    setPatterns(data.patterns || []);
    
    if (data.source === 'ai_agents') {
      console.log('Live AI data loaded!');
    } else {
      console.log('Using fallback data - submit entries to see live AI patterns');
    }
  } catch (error) {
    console.error('Error fetching patterns:', error);
  } finally {
    setLoading(false);
  }
};

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-blue-600';
    if (confidence >= 0.4) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getStatusColor = (status) => {
    if (status.includes('helping')) return 'bg-green-100 text-green-800';
    if (status.includes('hurting')) return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getEffectIcon = (change) => {
    if (change > 2) return '📈';
    if (change > 0) return '↗️';
    if (change < -2) return '📉';
    if (change < 0) return '↘️';
    return '➡️';
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="content-wrapper text-center">
          <div className="text-2xl">Analyzing your behavioral patterns...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <div className="page-header">
          <h1 className="page-title">Discovered Patterns</h1>
          <p className="page-subtitle">
            AI-discovered correlations between your activities and wellbeing
          </p>
        </div>

        <div className="card mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">{patterns.length}</div>
              <div className="text-sm text-muted">Total Patterns</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {patterns.filter(p => p.confidence >= 0.7).length}
              </div>
              <div className="text-sm text-muted">High Confidence</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {patterns.filter(p => p.mood_change_from_avg > 0).length}
              </div>
              <div className="text-sm text-muted">Mood Boosters</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {patterns.map((pattern) => (
            <div key={pattern.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-primary">{pattern.name}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(pattern.status)}`}>
                  {pattern.status}
                </span>
              </div>

              <p className="text-secondary mb-4">{pattern.description}</p>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-center mb-1">
                    <span className="mr-2">😊</span>
                    <span className="text-sm text-muted">Mood Effect</span>
                  </div>
                  <div className="text-lg font-bold text-blue-600">
                    {pattern.mood_effect.toFixed(1)}/10
                  </div>
                  <div className="text-xs text-secondary flex items-center justify-center">
                    {getEffectIcon(pattern.mood_change_from_avg)}
                    {pattern.mood_change_from_avg > 0 ? '+' : ''}
                    {pattern.mood_change_from_avg.toFixed(1)} avg
                  </div>
                </div>

                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center justify-center mb-1">
                    <span className="mr-2">⚡</span>
                    <span className="text-sm text-muted">Energy Effect</span>
                  </div>
                  <div className="text-lg font-bold text-green-600">
                    {pattern.energy_effect.toFixed(1)}/10
                  </div>
                  <div className="text-xs text-secondary flex items-center justify-center">
                    {getEffectIcon(pattern.energy_change_from_avg)}
                    {pattern.energy_change_from_avg > 0 ? '+' : ''}
                    {pattern.energy_change_from_avg.toFixed(1)} avg
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <span className="text-sm text-muted mr-2">Confidence:</span>
                  <span className={`font-semibold ${getConfidenceColor(pattern.confidence)}`}>
                    {(pattern.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      pattern.confidence >= 0.8 ? 'bg-green-500' :
                      pattern.confidence >= 0.6 ? 'bg-blue-500' :
                      pattern.confidence >= 0.4 ? 'bg-yellow-500' : 'bg-gray-400'
                    }`}
                    style={{ width: `${pattern.confidence * 100}%` }}
                  ></div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="text-xs text-muted">
                  Activities: {pattern.activities.slice(0, 3).join(', ')}
                  {pattern.activities.length > 3 && `, +${pattern.activities.length - 3} more`}
                </div>
                <Link 
                  href={`/recommendations?pattern=${pattern.id}`}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  View AI Insights →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}