'use client';
import { useState } from 'react';

export default function DailyEntry() {
  const [formData, setFormData] = useState({
    energy: 5,
    mood: 5,
    journalEntry: '',
    emotionalState: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Submitting:', formData);
  };

  return (
    <div className="page-container">
      <div className="content-wrapper-narrow">
        <div className="page-header text-center">
          <h1 className="page-title">Daily Check-in</h1>
          <p className="page-subtitle">Help your agents understand your day</p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-8">
          <div className="form-group">
            <label className="form-label">
              Energy Level: {formData.energy}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.energy}
              onChange={(e) => setFormData({...formData, energy: e.target.value})}
              className="slider"
            />
            <div className="flex justify-between text-sm text-muted mt-2">
              <span>Very Low</span>
              <span>High</span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              Overall Mood: {formData.mood}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.mood}
              onChange={(e) => setFormData({...formData, mood: e.target.value})}
              className="slider"
            />
            <div className="flex justify-between text-sm text-muted mt-2">
              <span>Low</span>
              <span>Great</span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Daily Summary</label>
            <textarea
              value={formData.journalEntry}
              onChange={(e) => setFormData({...formData, journalEntry: e.target.value})}
              placeholder="What happened today? Any highlights, challenges, or thoughts you'd like to share..."
              className="form-textarea"
              rows="4"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Emotional State Summary</label>
            <textarea
              value={formData.emotionalState}
              onChange={(e) => setFormData({...formData, emotionalState: e.target.value})}
              placeholder="How are you feeling emotionally? Any stress, excitement, anxiety, or contentment you want to note..."
              className="form-textarea"
              rows="3"
            />
          </div>

          <div className="card" style={{background: '#EBF8FF', padding: '1rem'}}>
            <h3 className="text-primary font-medium mb-2">Agents that will process this entry:</h3>
            <div className="flex flex-wrap gap-2">
              <span className="agent-status analyzing">Pattern Agent</span>
              <span className="agent-status active">Insight Agent</span>
              <span className="agent-status learning">Personalization Agent</span>
            </div>
          </div>

          <button type="submit" className="btn btn-primary w-full">
            Submit Daily Entry
          </button>
        </form>
      </div>
    </div>
  );
}