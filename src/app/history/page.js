'use client';
import { useState } from 'react';

export default function History() {
  const [timeframe, setTimeframe] = useState('week');
  
  const mockEntries = [
    { date: '2024-05-23', energy: 8, mood: 7, summary: 'Great day! Morning workout really helped.' },
    { date: '2024-05-22', energy: 6, mood: 6, summary: 'Productive work day, but felt a bit tired.' },
    { date: '2024-05-21', energy: 4, mood: 5, summary: 'Struggled with focus today.' },
    { date: '2024-05-20', energy: 7, mood: 8, summary: 'Good balance of work and relaxation.' },
  ];

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <div className="page-header">
          <h1 className="page-title">Your Journey</h1>
          <p className="page-subtitle">Track your patterns and see how your agents have evolved</p>
        </div>

        <div className="card mb-8">
          <div className="flex flex-wrap gap-2">
            {['week', 'month', '3months'].map(period => (
              <button
                key={period}
                onClick={() => setTimeframe(period)}
                className={`btn ${
                  timeframe === period 
                    ? 'btn-primary' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {period === '3months' ? '3 Months' : period.charAt(0).toUpperCase() + period.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="card">
              <h2 className="card-header">Entry Timeline</h2>
              <div className="space-y-6">
                {mockEntries.map(entry => (
                  <div key={entry.date} className="timeline-entry">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-primary font-medium">{entry.date}</h3>
                      <div className="flex space-x-4 text-sm">
                        <span className="flex items-center text-secondary">
                          ⚡ {entry.energy}/10
                        </span>
                        <span className="flex items-center text-secondary">
                          😊 {entry.mood}/10
                        </span>
                      </div>
                    </div>
                    <p className="text-secondary">{entry.summary}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="card">
              <h3 className="card-header">Pattern Evolution</h3>
              <div className="space-y-3">
                <div className="text-sm">
                  <p className="text-primary font-medium">Week 1</p>
                  <p className="text-secondary">Baseline patterns established</p>
                </div>
                <div className="text-sm">
                  <p className="text-primary font-medium">Week 2</p>
                  <p className="text-secondary">Exercise-energy correlation discovered</p>
                </div>
                <div className="text-sm">
                  <p className="text-primary font-medium">Week 3</p>
                  <p className="text-secondary">Weekend Energy Agent spawned</p>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="card-header">Key Insights</h3>
              <div className="space-y-3 text-sm">
                <div className="insight-card insight" style={{background: '#F0FDF4', padding: '0.75rem', borderRadius: '0.5rem'}}>
                  <p className="font-medium" style={{color: '#065F46'}}>Morning Exercise Boost</p>
                  <p style={{color: '#047857'}}>+2.3 energy increase on exercise days</p>
                </div>
                <div className="insight-card pattern" style={{background: '#EBF8FF', padding: '0.75rem', borderRadius: '0.5rem'}}>
                  <p className="font-medium" style={{color: '#1E40AF'}}>Sleep Quality Impact</p>
                  <p style={{color: '#1D4ED8'}}>87% correlation with next-day mood</p>
                </div>
                <div className="insight-card spawned" style={{background: '#FEF3C7', padding: '0.75rem', borderRadius: '0.5rem'}}>
                  <p className="font-medium" style={{color: '#92400E'}}>Weekend Pattern</p>
                  <p style={{color: '#B45309'}}>Specialized agent improving weekend energy</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}