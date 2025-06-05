from uagents import Agent, Context, Model
import requests
import json
from typing import List, Dict, Any
import os
import numpy as np

class PatternAnalysisMessage(Model):
    patterns: List[Dict[str, Any]]
    user_id: str
    total_patterns: int
    high_confidence_patterns: int
    is_baseline: bool = False

class PlannerRecommendationsMessage(Model):
    daily_suggestions: str
    weekly_report: str
    habit_change_plans: List[Dict[str, Any]]
    user_id: str
    patterns_analyzed: int

# Initialize planner agent
planner_agent = Agent(
    name="planner_agent",
    seed="planner_seed",
    port=8003,
    endpoint=["http://127.0.0.1:8003/submit"]
)

class WellnessPlanner:
    def __init__(self, asi_api_key: str):
        self.asi_api_key = asi_api_key
        self.asi_base_url = "https://api.asi1.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {asi_api_key}",
            "Content-Type": "application/json"
        }
        self.baseline_established = False
        self.baseline_patterns = []
    
    def _call_asi_mini(self, prompt: str, max_tokens: int = 500) -> str:
        """Make API call to AS1:Mini"""
        if self.asi_api_key == "your-asi-api-key-here":
            return "[AS1 API key not configured - returning mock response]"
            
        payload = {
            "model": "asi1-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.asi_base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling AS1:Mini: {str(e)}"
    
    def analyze_baseline_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive baseline analysis of all 30 entries"""
        if not patterns:
            return {"insights": "No baseline patterns detected. Continue logging daily activities."}
        
        self.baseline_patterns = patterns
        
        # sort into catagories of levels
        highly_positive = [p for p in patterns if p['mood_change_from_avg'] > 2.0]
        moderately_positive = [p for p in patterns if 1.0 < p['mood_change_from_avg'] <= 2.0]
        neutral = [p for p in patterns if -1.0 <= p['mood_change_from_avg'] <= 1.0]
        moderately_negative = [p for p in patterns if -2.0 <= p['mood_change_from_avg'] < -1.0]
        highly_negative = [p for p in patterns if p['mood_change_from_avg'] < -2.0]
        
        # sort by confidence
        highly_positive.sort(key=lambda x: x['confidence'], reverse=True)
        highly_negative.sort(key=lambda x: x['confidence'], reverse=True)
        
        prompt = f"""
        Analyze this user's comprehensive baseline behavioral patterns from 30 days of activity data:

        HIGHLY POSITIVE ACTIVITIES (Major mood/energy boost - {len(highly_positive)} patterns):
        {self._format_patterns_for_prompt(highly_positive[:5])}  

        MODERATELY POSITIVE ACTIVITIES ({len(moderately_positive)} patterns):
        {self._format_patterns_for_prompt(moderately_positive[:3])}

        NEUTRAL ACTIVITIES ({len(neutral)} patterns):
        {self._format_patterns_for_prompt(neutral[:2])}

        MODERATELY NEGATIVE ACTIVITIES ({len(moderately_negative)} patterns):
        {self._format_patterns_for_prompt(moderately_negative[:3])}

        HIGHLY NEGATIVE ACTIVITIES (Major mood/energy drain - {len(highly_negative)} patterns):
        {self._format_patterns_for_prompt(highly_negative[:5])}

        Provide a comprehensive baseline analysis including:
        1. User's strongest positive behavioral patterns and why they're effective
        2. Most concerning negative patterns that need immediate attention  
        3. Key insights about their activity-mood-energy relationships
        4. 3 immediate actionable recommendations based on this 30-day baseline
        5. Warning signs to monitor going forward
        6. Overall behavioral profile summary

        This establishes their complete behavioral baseline from 30 entries - be thorough and insightful.
        """
        
        analysis = self._call_asi_mini(prompt, max_tokens=1000)
        
        return {
            "baseline_analysis": analysis,
            "highly_positive": highly_positive,
            "highly_negative": highly_negative,
            "moderately_positive": moderately_positive,
            "moderately_negative": moderately_negative,
            "neutral": neutral,
            "pattern_count": len(patterns),
            "confidence_score": np.mean([p['confidence'] for p in patterns]) if patterns else 0
        }
    
    def analyze_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not patterns:
            return {"insights": "No significant patterns detected yet. Continue logging daily activities."}
        
        # compare against baseline if available
        baseline_context = ""
        if self.baseline_established and self.baseline_patterns:
            baseline_context = f"\nBaseline context: User had {len(self.baseline_patterns)} established patterns. "
        
        positive_patterns = [p for p in patterns if p['mood_change_from_avg'] > 1.0]
        negative_patterns = [p for p in patterns if p['mood_change_from_avg'] < -1.0]
        
        prompt = f"""
        None of your output should contain emojis.
        Analyze these updated daily activity patterns:{baseline_context}

        POSITIVE PATTERNS (boost mood/energy - {len(positive_patterns)} total):
        {self._format_patterns_for_prompt(positive_patterns[:5])}

        NEGATIVE PATTERNS (drain mood/energy - {len(negative_patterns)} total):
        {self._format_patterns_for_prompt(negative_patterns[:5])}

        Provide:
        1. Key insights about current activity effectiveness vs baseline
        2. Specific, actionable recommendations for today/this week
        3. Any concerning trend changes from baseline
        4. Positive reinforcement for patterns that are working well

        Keep recommendations practical and achievable. Focus on small, sustainable changes.
        """
        
        analysis = self._call_asi_mini(prompt, max_tokens=600)
        
        return {
            "insights": analysis,
            "positive_patterns": positive_patterns,
            "negative_patterns": negative_patterns,
            "pattern_count": len(patterns)
        }

    def generate_daily_suggestions(self, patterns: List[Dict[str, Any]], current_mood: int = None, current_energy: int = None) -> str:
        """generate specific suggestions for today based on patterns"""
        if not patterns:
            return "Start tracking your daily activities to receive personalized suggestions."
        
        high_impact_positive = [p for p in patterns if p['mood_change_from_avg'] > 2.0 and p['confidence'] > 0.5]
        high_impact_negative = [p for p in patterns if p['mood_change_from_avg'] < -2.0 and p['confidence'] > 0.5]
        
        mood_context = f"Current mood: {current_mood}/10, " if current_mood else ""
        energy_context = f"Current energy: {current_energy}/10, " if current_energy else ""
        
        prompt = f"""
        Based on established activity patterns, create today's personalized wellness action plan.

        {mood_context}{energy_context}

        HIGH-IMPACT POSITIVE ACTIVITIES ({len(high_impact_positive)} identified):
        {self._format_patterns_for_prompt(high_impact_positive)}

        HIGH-IMPACT NEGATIVE ACTIVITIES ({len(high_impact_negative)} identified):
        {self._format_patterns_for_prompt(high_impact_negative)}

        Generate today's action plan:
        1. 3 specific activities to prioritize today (from positive patterns)
        2. 2 activities to avoid or limit today (from negative patterns)  
        3. One "mood booster" activity if feeling low
        4. One "energy booster" activity if feeling tired
        5. A simple evening reflection question

        Make suggestions specific, actionable, and realistic for a single day.
        """
        
        return self._call_asi_mini(prompt, max_tokens=400)

    def _format_patterns_for_prompt(self, patterns: List[Dict[str, Any]]) -> str:
        """Format patterns for AI prompt"""
        if not patterns:
            return "None identified"
        
        formatted = []
        for pattern in patterns:
            formatted.append(
                f"- {pattern['group_label']}: "
                f"Mood effect {pattern['effect_on_mood']:.1f}/10 "
                f"({pattern['mood_change_from_avg']:+.1f} from average), "
                f"Energy effect {pattern['effect_on_energy']:.1f}/10 "
                f"({pattern['energy_change_from_avg']:+.1f} from average), "
                f"Confidence: {pattern['confidence']:.2f}"
            )
        return "\n".join(formatted)

# Global planner instance
wellness_planner = None

@planner_agent.on_event("startup")
async def initialize_planner(ctx: Context):
    global wellness_planner

    # Get AS1 API key from environment
    asi_api_key = os.getenv("AS1_API_KEY", "your-asi-api-key-here")

    if asi_api_key == "your-asi-api-key-here":
        ctx.logger.warning("AS1 API key not set! Set AS1_API_KEY environment variable")
        ctx.logger.info("Will use mock responses instead of real AI analysis")

    wellness_planner = WellnessPlanner(asi_api_key)
    ctx.logger.info("Wellness Planner initialized, waiting for baseline analysis...")

@planner_agent.on_message(model=PatternAnalysisMessage)
async def handle_pattern_analysis(ctx: Context, sender: str, msg: PatternAnalysisMessage):
    ctx.logger.info(f"Processing pattern analysis from {sender}")
    ctx.logger.info(f"Received {msg.total_patterns} patterns, {msg.high_confidence_patterns} high confidence")
    ctx.logger.info(f"Is baseline: {msg.is_baseline}")

    if wellness_planner is None:
        ctx.logger.error("Wellness planner not initialized yet!")
        return

    try:
        if msg.is_baseline:
            # Handle comprehensive baseline establishment
            ctx.logger.info("Processing COMPREHENSIVE BASELINE analysis...")
            analysis = wellness_planner.analyze_baseline_patterns(msg.patterns)
            wellness_planner.baseline_established = True
            
            # Comprehensive baseline logging
            ctx.logger.info("=" * 80)
            ctx.logger.info("COMPREHENSIVE BASELINE BEHAVIORAL ANALYSIS COMPLETE")
            ctx.logger.info("=" * 80)
            ctx.logger.info(f"Total patterns identified: {analysis['pattern_count']}")
            ctx.logger.info(f"Highly positive patterns: {len(analysis.get('highly_positive', []))}")
            ctx.logger.info(f"Moderately positive patterns: {len(analysis.get('moderately_positive', []))}")
            ctx.logger.info(f"Neutral patterns: {len(analysis.get('neutral', []))}")
            ctx.logger.info(f"Moderately negative patterns: {len(analysis.get('moderately_negative', []))}")
            ctx.logger.info(f"Highly negative patterns: {len(analysis.get('highly_negative', []))}")
            ctx.logger.info(f"Average confidence: {analysis.get('confidence_score', 0):.2f}")
            ctx.logger.info("-" * 40)
            
            # Show top patterns
            if analysis.get('highly_positive'):
                ctx.logger.info("TOP POSITIVE PATTERNS:")
                for i, pattern in enumerate(analysis['highly_positive'][:3], 1):
                    ctx.logger.info(f"  {i}. {pattern['group_label']} (impact: +{pattern['mood_change_from_avg']:.1f}, confidence: {pattern['confidence']:.2f})")
            
            if analysis.get('highly_negative'):
                ctx.logger.info("TOP CONCERNING PATTERNS:")
                for i, pattern in enumerate(analysis['highly_negative'][:3], 1):
                    ctx.logger.info(f"  {i}. {pattern['group_label']} (impact: {pattern['mood_change_from_avg']:.1f}, confidence: {pattern['confidence']:.2f})")
            
            ctx.logger.info("-" * 40)
            ctx.logger.info(f"AI Analysis:\n{analysis['baseline_analysis']}")
            ctx.logger.info("=" * 80)
            ctx.logger.info("BASELINE ESTABLISHED! Ready for daily entries.")
            ctx.logger.info("=" * 80)
            
        else:
            # Handle regular daily analysis
            ctx.logger.info("Processing DAILY analysis update...")
            analysis = wellness_planner.analyze_patterns(msg.patterns)
            daily_suggestions = wellness_planner.generate_daily_suggestions(msg.patterns)
            
            # Create habit change plans for concerning patterns
            habit_plans = []
            concerning_patterns = [p for p in msg.patterns if p['mood_change_from_avg'] < -2.0 and p['confidence'] > 0.5]
            
            for pattern in concerning_patterns[:2]:  # Limit to top 2 concerning patterns
                habit_plan = {
                    "target_activity": pattern['group_label'],
                    "change_direction": "reduce",
                    "confidence": pattern['confidence'],
                    "impact": pattern['mood_change_from_avg']
                }
                habit_plans.append(habit_plan)
            
            # Log daily recommendations
            ctx.logger.info("=" * 60)
            ctx.logger.info("DAILY WELLNESS ANALYSIS UPDATE")
            ctx.logger.info("=" * 60)
            ctx.logger.info(f"Current patterns: {msg.total_patterns} total, {msg.high_confidence_patterns} high confidence")
            ctx.logger.info(f"Analysis Insights:\n{analysis['insights']}")
            ctx.logger.info("-" * 30)
            ctx.logger.info(f"Daily Suggestions:\n{daily_suggestions}")
            
            if habit_plans:
                ctx.logger.info("-" * 30)
                ctx.logger.info("Habit Change Recommendations:")
                for plan in habit_plans:
                    ctx.logger.info(f"  • Reduce: {plan['target_activity']} (impact: {plan['impact']:.1f}, confidence: {plan['confidence']:.2f})")
            
            ctx.logger.info("=" * 60)
        
    except Exception as e:
        ctx.logger.error(f"Error processing pattern analysis: {str(e)}")

if __name__ == "__main__":
    planner_agent.run()