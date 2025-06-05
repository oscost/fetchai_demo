'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function DailyEntry() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    energy_rating: 5,
    mood_rating: 5,
    entry_text: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch('http://localhost:5000/api/daily_entry', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();
      
      if (result.success) {
        setSubmitted(true);
        setTimeout(() => {
          router.push('/');
        }, 2000);
      } else {
        alert('Error submitting entry: ' + result.error);
      }
    } catch (error) {
      console.error('Error submitting entry:', error);
      alert('Error submitting entry. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="page-container">
        <div className="content-wrapper-narrow text-center">
          <div className="card">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold text-primary mb-2">Entry Submitted!</h2>
            <p className="text-secondary mb-4">Your AI agents are now processing your daily data...</p>
            <div className="flex justify-center space-x-2">
              <span className="agent-status analyzing">Extractor Agent</span>
              <span className="agent-status learning">Pattern Finder</span>
              <span className="agent-status active">Curator</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
              Energy Level: {formData.energy_rating}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.energy_rating}
              onChange={(e) => setFormData({...formData, energy_rating: parseInt(e.target.value)})}
              className="slider"
            />
            <div className="flex justify-between text-sm text-muted mt-2">
              <span>Very Low</span>
              <span>High</span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              Overall Mood: {formData.mood_rating}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.mood_rating}
              onChange={(e) => setFormData({...formData, mood_rating: parseInt(e.target.value)})}
              className="slider"
            />
            <div className="flex justify-between text-sm text-muted mt-2">
              <span>Low</span>
              <span>Great</span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">What happened today?</label>
            <textarea
              value={formData.entry_text}
              onChange={(e) => setFormData({...formData, entry_text: e.target.value})}
              placeholder="Describe your day... What activities did you do? How did you feel? Any highlights or challenges?"
              className="form-textarea"
              rows="6"
              required
            />
            <p className="text-sm text-muted mt-2">
              Be specific about activities, meals, exercise, social interactions, work, etc. 
              This helps your AI agents find meaningful patterns.
            </p>
          </div>

          <div className="card" style={{background: '#EBF8FF', padding: '1rem'}}>
            <h3 className="text-primary font-medium mb-2">Agents processing this entry:</h3>
            <div className="flex flex-wrap gap-2">
              <span className="agent-status analyzing">Extractor Agent</span>
              <span className="agent-status learning">Pattern Finder</span>
              <span className="agent-status active">Curator Agent</span>
              <span className="agent-status specialized">Planner Agent</span>
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary w-full"
            disabled={submitting || !formData.entry_text.trim()}
          >
            {submitting ? 'Submitting...' : 'Submit Daily Entry'}
          </button>
        </form>
      </div>
    </div>
  );
}