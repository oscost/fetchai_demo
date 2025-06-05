'use client';
import { useState, useEffect } from 'react';

export default function History() {
  const [entries, setEntries] = useState([]);
  const [timeframe, setTimeframe] = useState('all');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/history');
      const data = await response.json();
      setEntries(data.entries || []);
      calculateStats(data.entries || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (allEntries) => {
    if (allEntries.length === 0) return;

    const moodAvg = allEntries.reduce((sum, entry) => sum + entry.mood_rating, 0) / allEntries.length;
    const energyAvg = allEntries.reduce((sum, entry) => sum + entry.energy_rating, 0) / allEntries.length;
    
    const recentEntries = allEntries.slice(0, 7);
    const recentMoodAvg = recentEntries.reduce((sum, entry) => sum + entry.mood_rating, 0) / recentEntries.length;
    const recentEnergyAvg = recentEntries.reduce((sum, entry) => sum + entry.energy_rating, 0) / recentEntries.length;

    setStats({
      totalEntries: allEntries.length,
      baselineEntries: allEntries.filter(e => e.type === 'baseline').length,
      userEntries: allEntries.filter(e => e.type === 'user').length,
      avgMood: moodAvg,
      avgEnergy: energyAvg,
      recentMoodAvg,
      recentEnergyAvg,
      moodTrend: recentMoodAvg - moodAvg,
      energyTrend: recentEnergyAvg - energyAvg
    });
  };

  const filterEntriesByTimeframe = (allEntries) => {
    if (timeframe === 'all') return allEntries;
    
    const now = new Date();
    const cutoffDate = new Date();
    
    switch (timeframe) {
      case 'week':
        cutoffDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        cutoffDate.setMonth(now.getMonth() - 1);
        break;
      case '3months':
        cutoffDate.setMonth(now.getMonth() - 3);
        break;
      default:
        return allEntries;
    }
    
    return allEntries.filter(entry => new Date(entry.date) >= cutoffDate);
  };

  const getMoodEmoji = (mood) => {
    if (mood >= 8) return '😊';
    if (mood >= 6) return '🙂';
    if (mood >= 4) return '😐';
    if (mood >= 2) return '😕';
    return '😢';
  };

  const getEnergyIcon = (energy) => {
    if (energy >= 8) return '⚡⚡⚡';
    if (energy >= 6) return '⚡⚡';
    if (energy >= 4) return '⚡';
    return '🔋';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  const filteredEntries = filterEntriesByTimeframe(entries);

  if (loading) {
    return (
      <div className="page-container">
        <div className="content-wrapper text-center">
          <div className="text-2xl">Loading your wellness journey...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <div className="page-header">
          <h1 className="page-title">Your Wellness Journey</h1>
          <p className="page-subtitle">
            Track your patterns and see how your insights have evolved
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="stat-card">
            <div className="stat-label">Total Entries</div>
            <div className="stat-value primary">{stats.totalEntries}</div>
            <div className="text-xs text-muted">
              {stats.baselineEntries} baseline + {stats.userEntries} personal
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Average Mood</div>
            <div className="stat-value accent">{stats.avgMood?.toFixed(1)}/10</div>
            <div className={`text-xs ${stats.moodTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {stats.moodTrend >= 0 ? '↗' : '↘'} {Math.abs(stats.moodTrend || 0).toFixed(1)} recent
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Average Energy</div>
            <div className="stat-value warning">{stats.avgEnergy?.toFixed(1)}/10</div>
            <div className={`text-xs ${stats.energyTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {stats.energyTrend >= 0 ? '↗' : '↘'} {Math.abs(stats.energyTrend || 0).toFixed(1)} recent
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Journey Length</div>
            <div className="stat-value positive">{Math.ceil(stats.totalEntries / 7)} weeks</div>
            <div className="text-xs text-muted">of tracking</div>
          </div>
        </div>

        {/* Time Filter */}
        <div className="card mb-8">
          <div className="flex flex-wrap gap-2">
            {[
              { value: 'all', label: 'All Time' },
              { value: 'week', label: 'Past Week' },
              { value: 'month', label: 'Past Month' },
              { value: '3months', label: 'Past 3 Months' }
            ].map(period => (
              <button
                key={period.value}
                onClick={() => setTimeframe(period.value)}
                className={`btn ${
                  timeframe === period.value 
                    ? 'btn-primary' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {period.label}
              </button>
            ))}
          </div>
          <div className="mt-4 text-sm text-muted">
            Showing {filteredEntries.length} entries
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Entry Timeline */}
          <div className="lg:col-span-2">
            <div className="card">
              <h2 className="card-header">Entry Timeline</h2>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {filteredEntries.map((entry, index) => (
                  <div key={`${entry.date}-${index}`} className="timeline-entry">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-primary font-medium flex items-center">
                        {formatDate(entry.date)}
                        {entry.type === 'baseline' && (
                          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            Baseline
                          </span>
                        )}
                      </h3>
                      <div className="flex space-x-4 text-sm">
                        <span className="flex items-center text-secondary">
                          {getEnergyIcon(entry.energy_rating)} {entry.energy_rating}/10
                        </span>
                        <span className="flex items-center text-secondary">
                          {getMoodEmoji(entry.mood_rating)} {entry.mood_rating}/10
                        </span>
                      </div>
                    </div>
                    <p className="text-secondary text-sm leading-relaxed">
                      {entry.entry_text.length > 200 
                        ? `${entry.entry_text.substring(0, 200)}...` 
                        : entry.entry_text
                      }
                    </p>
                  </div>
                ))}
                
                {filteredEntries.length === 0 && (
                  <div className="text-center text-muted py-8">
                    <div className="text-4xl mb-2">📝</div>
                    <p>No entries found for this time period</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Pattern Evolution */}
            <div className="card">
              <h3 className="card-header">Pattern Discovery Timeline</h3>
              <div className="space-y-3">
                <div className="text-sm">
                  <p className="text-primary font-medium">Baseline Period</p>
                  <p className="text-secondary">30 entries processed</p>
                  <p className="text-xs text-muted">5 patterns discovered</p>
                </div>
                <div className="text-sm">
                  <p className="text-primary font-medium">Exercise Pattern</p>
                  <p className="text-secondary">High confidence achieved</p>
                  <p className="text-xs text-muted">Perfect 1.00 reliability</p>
                </div>
                <div className="text-sm">
                  <p className="text-primary font-medium">Social Media Pattern</p>
                  <p className="text-secondary">Negative correlation found</p>
                  <p className="text-xs text-muted">0.89 confidence</p>
                </div>
                <div className="text-sm">
                  <p className="text-primary font-medium">Cooking Benefits</p>
                  <p className="text-secondary">Mood boost identified</p>
                  <p className="text-xs text-muted">0.79 confidence</p>
                </div>
              </div>
            </div>

            {/* Key Insights */}
            <div className="card">
              <h3 className="card-header">Key Insights Discovered</h3>
              <div className="space-y-3 text-sm">
                <div className="insight-card insight" style={{background: '#F0FDF4', padding: '0.75rem', borderRadius: '0.5rem'}}>
                  <p className="font-medium" style={{color: '#065F46'}}>Exercise Boost</p>
                  <p style={{color: '#047857'}}>+4.9 mood increase on exercise days</p>
                  <p className="text-xs text-muted">1.00 confidence</p>
                </div>
                <div className="insight-card pattern" style={{background: '#FEF3C7', padding: '0.75rem', borderRadius: '0.5rem'}}>
                  <p className="font-medium" style={{color: '#92400E'}}>Social Media Drain</p>
                  <p style={{color: '#B45309'}}>-1.1 mood decrease on heavy usage</p>
                  <p className="text-xs text-muted">0.89 confidence</p>
                </div>
                <div className="insight-card spawned" style={{background: '#EBF8FF', padding: '0.75rem', borderRadius: '0.5rem'}}>
                  <p className="font-medium" style={{color: '#1E40AF'}}>Cooking Benefits</p>
                  <p style={{color: '#1D4ED8'}}>+2.9 mood boost from meal prep</p>
                  <p className="text-xs text-muted">0.79 confidence</p>
                </div>
              </div>
            </div>

            {/* Progress Summary */}
            <div className="card">
              <h3 className="card-header">Journey Summary</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-secondary">Days tracked:</span>
                  <span className="font-medium">{stats.totalEntries}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary">Patterns found:</span>
                  <span className="font-medium">5</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary">Insights generated:</span>
                  <span className="font-medium">12+</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary">Avg wellbeing:</span>
                  <span className="font-medium">
                    {((stats.avgMood + stats.avgEnergy) / 2).toFixed(1)}/10
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}