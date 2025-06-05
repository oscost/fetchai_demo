'use client';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function Recommendations() {
  const searchParams = useSearchParams();
  const selectedPattern = searchParams.get('pattern');
  
  const [patterns, setPatterns] = useState([]);
  const [activePattern, setActivePattern] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPatterns();
  }, []);

  useEffect(() => {
    if (selectedPattern && patterns.length > 0) {
      const pattern = patterns.find(p => p.id === selectedPattern);
      if (pattern) {
        setActivePattern(pattern);
        fetchRecommendation(selectedPattern);
      }
    }
  }, [selectedPattern, patterns]);

  const fetchPatterns = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/patterns');
      const data = await response.json();
      setPatterns(data.patterns || []);
      
      // If no specific pattern selected, show the first high-confidence one
      if (!selectedPattern && data.patterns?.length > 0) {
        const highConfPattern = data.patterns.find(p => p.confidence >= 0.7) || data.patterns[0];
        setActivePattern(highConfPattern);
        fetchRecommendation(highConfPattern.id);
      }
    } catch (error) {
      console.error('Error fetching patterns:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendation = async (patternId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/patterns/${patternId}/recommendations`);
      const data = await response.json();
      setRecommendation(data);
    } catch (error) {
      console.error('Error fetching recommendation:', error);
    }
  };

  const handlePatternSelect = (pattern) => {
    setActivePattern(pattern);
    fetchRecommendation(pattern.id);
    // Update URL without page refresh
    window.history.pushState({}, '', `/recommendations?pattern=${pattern.id}`);
  };

  const handleFeedback = async (feedbackType) => {
    try {
      const response = await fetch('http://localhost:5000/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pattern_id: activePattern.id,
          feedback_type: feedbackType,
          comment: ''
        }),
      });

      const result = await response.json();
      if (result.success) {
        alert('Feedback submitted! Your agents will adjust their recommendations.');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Error submitting feedback. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="content-wrapper text-center">
          <div className="text-2xl">Loading AI recommendations...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="content-wrapper">
        <div className="page-header">
          <h1 className="page-title">AI Recommendations</h1>
          <p className="page-subtitle">
            Personalized insights and strategies based on your patterns
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Pattern Selection Sidebar */}
          <div className="lg:col-span-1">
            <div className="card">
              <h3 className="font-semibold mb-4">Select Pattern</h3>
              <div className="space-y-2">
                {patterns.map((pattern) => (
                  <button
                    key={pattern.id}
                    onClick={() => handlePatternSelect(pattern)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      activePattern?.id === pattern.id 
                        ? 'bg-blue-100 border-2 border-blue-500' 
                        : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                    }`}
                  >
                    <div className="font-medium text-sm">{pattern.name}</div>
                    <div className="text-xs text-muted">
                      {(pattern.confidence * 100).toFixed(0)}% confidence
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Recommendation Content */}
          <div className="lg:col-span-3">
            {activePattern && recommendation ? (
              <div className="space-y-6">
                {/* Pattern Summary */}
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-primary">{activePattern.name}</h2>
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="text-sm text-muted">Mood</div>
                        <div className="font-bold text-blue-600">
                          {activePattern.mood_effect.toFixed(1)}/10
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-muted">Energy</div>
                        <div className="font-bold text-green-600">
                          {activePattern.energy_effect.toFixed(1)}/10
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-muted">Confidence</div>
                        <div className="font-bold text-purple-600">
                          {(activePattern.confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI Analysis */}
                <div className="card">
                  <h3 className="card-header">{recommendation.title}</h3>
                  <p className="text-secondary mb-4 leading-relaxed">
                    {recommendation.analysis}
                  </p>
                </div>

                {/* Strategies */}
                <div className="card">
                  <h3 className="card-header">Recommended Strategies</h3>
                  <div className="space-y-3">
                    {recommendation.strategies?.map((strategy, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                          {index + 1}
                        </div>
                        <p className="text-secondary">{strategy}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Feedback Section */}
                <div className="card bg-gradient-to-r from-blue-50 to-purple-50">
                  <h3 className="font-semibold mb-4">How helpful is this recommendation?</h3>
                  <p className="text-secondary text-sm mb-4">
                    Your feedback helps your AI agents learn and improve their suggestions.
                  </p>
                  <div className="flex space-x-4">
                    <button 
                      onClick={() => handleFeedback('love_it')}
                      className="btn bg-green-500 text-white hover:bg-green-600"
                    >
                      👍 Love it!
                    </button>
                    <button 
                      onClick={() => handleFeedback('not_sure')}
                      className="btn bg-yellow-500 text-white hover:bg-yellow-600"
                    >
                      🤔 Not sure
                    </button>
                    <button 
                      onClick={() => handleFeedback('dislike')}
                      className="btn bg-red-500 text-white hover:bg-red-600"
                    >
                      👎 Not helpful
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card text-center">
                <div className="text-4xl mb-4">🤖</div>
                <h3 className="text-xl font-semibold mb-2">Select a pattern to see recommendations</h3>
                <p className="text-secondary">
                  Choose a behavioral pattern from the sidebar to get personalized AI insights.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}