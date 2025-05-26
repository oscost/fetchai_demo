'use client';
import { useState } from 'react';

export default function Agents() {
  const [activeAgents] = useState([
    { id: 1, name: 'Pattern Agent', status: 'analyzing', color: 'blue', description: 'Finding correlations in your daily data' },
    { id: 2, name: 'Insight Agent', status: 'active', color: 'green', description: 'Generating actionable recommendations' },
    { id: 3, name: 'Personalization Agent', status: 'learning', color: 'purple', description: 'Adapting suggestions to your preferences' },
    { id: 4, name: 'Weekend Energy Agent', status: 'specialized', color: 'orange', description: 'Spawned to optimize your weekend routines' }
  ]);

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <div className="page-header">
          <h1 className="page-title">Your AI Agent Network</h1>
          <p className="page-subtitle">See how your specialized agents work together to understand your patterns</p>
        </div>

        <div className="card mb-8">
          <h2 className="card-header">Agent Collaboration Map</h2>
          <div className="flex items-center justify-center min-h-64 bg-accent rounded-lg">
            <div className="text-center text-muted">
              <div className="text-4xl mb-2">🔗</div>
              <p>Agent network visualization</p>
              <p className="text-sm">(Interactive diagram showing agent connections)</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {activeAgents.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-primary">{agent.name}</h3>
                <span className={`agent-status ${agent.status}`}>
                  {agent.status}
                </span>
              </div>
              <p className="text-secondary mb-4">{agent.description}</p>
              <div className="flex justify-between items-center text-sm text-muted">
                <span>Last active: 2 minutes ago</span>
                <button className="text-blue-600 hover:text-blue-800">View details</button>
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <h2 className="card-header">Recent Agent Activity</h2>
          <div className="space-y-4">
            <div className="activity-feed">
              <div className="activity-avatar pattern">PA</div>
              <div className="flex-1">
                <p className="text-primary font-medium">Pattern Agent discovered new correlation</p>
                <p className="text-secondary text-sm">Sleep quality correlates with next-day energy levels (confidence: 87%)</p>
                <p className="text-muted text-xs">5 minutes ago</p>
              </div>
            </div>
            <div className="activity-feed">
              <div className="activity-avatar spawned">WE</div>
              <div className="flex-1">
                <p className="text-primary font-medium">Weekend Energy Agent spawned</p>
                <p className="text-secondary text-sm">Specialized agent created to analyze weekend vs weekday patterns</p>
                <p className="text-muted text-xs">2 hours ago</p>
              </div>
            </div>
            <div className="activity-feed">
              <div className="activity-avatar insight">IA</div>
              <div className="flex-1">
                <p className="text-primary font-medium">Insight Agent generated new recommendation</p>
                <p className="text-secondary text-sm">Morning exercise routine shows 85% correlation with energy boost</p>
                <p className="text-muted text-xs">1 hour ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}