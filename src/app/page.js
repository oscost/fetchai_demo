'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/dashboard');
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="content-wrapper text-center">
          <div className="text-2xl">Loading your wellness insights...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <div className="page-header">
          <h1 className="page-title">Good morning! How are you feeling today?</h1>
          <p className="page-subtitle">Your AI agents have been analyzing your patterns</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Energy Trend</div>
            <div className="stat-value positive">{dashboardData?.energy_trend || '↗ +15%'}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Active Agents</div>
            <div className="stat-value primary">{dashboardData?.active_agents || 4}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Patterns Found</div>
            <div className="stat-value accent">{dashboardData?.patterns_found || 5}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Daily Entries</div>
            <div className="stat-value warning">{dashboardData?.streak_days || 30}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="card">
            <h2 className="card-header flex items-center">
              <span className="w-3 h-3 bg-blue-500 rounded-full mr-3"></span>
              Recent AI Insights
            </h2>
            <div className="space-y-4">
              {dashboardData?.recent_insights?.map((insight, index) => (
                <div key={index} className={`insight-card ${insight.type}`}>
                  <p className="text-muted text-sm">{insight.agent}</p>
                  <p className="text-primary font-medium">{insight.text}</p>
                  {insight.confidence && (
                    <p className="text-xs text-secondary">Confidence: {(insight.confidence * 100).toFixed(0)}%</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h2 className="card-header">Today's Recommendations</h2>
            <div className="space-y-3">
              {dashboardData?.todays_recommendations?.map((rec, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    rec.priority === 'high' ? 'bg-green-500' : 
                    rec.priority === 'medium' ? 'bg-blue-500' : 'bg-gray-400'
                  }`}></div>
                  <div>
                    <p className="text-primary font-medium">{rec.text}</p>
                    <p className="text-secondary text-sm">{rec.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <Link href="/daily_entry" className="btn btn-primary">
            Log Today's Entry
          </Link>
        </div>
      </div>
    </div>
  );
}