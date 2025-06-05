#REMEMBER TO SET ENVIRONMENT VARIABLE FOR API KEY BEFORE RUNNING!!!!
from uagents import Agent, Context, Model
import requests
import json
from typing import List, Dict, Any
import os
import numpy as np
import threading

class PatternAnalysisMessage(Model):
    patterns: List[Dict[str, Any]]
    user_id: str
    total_patterns: int
    high_confidence_patterns: int
    is_baseline: bool = False

class PatternAnalysisForPlannerMessage(Model):
    patterns: List[Dict[str, Any]]
    user_id: str
    total_patterns: int
    high_confidence_patterns: int
    focus_patterns: List[str] = []  # Which patterns to focus on
    trigger_reason: str = ""
    is_baseline: bool = False

class ImmediatePlannerUpdateMessage(Model):
    user_id: str
    reason: str
    patterns_to_focus: List[str]
    updated_patterns: List[Dict[str, Any]]

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

def send_to_flask_server(endpoint, data):
    """Send updates back to Flask server"""
    try:
        # Use 127.0.0.1 instead of localhost to match Flask's binding
        flask_endpoint = endpoint
        url = f"http://127.0.0.1:5000{flask_endpoint}"  # Changed from localhost
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers, timeout=10)  # Increased timeout
        
        print(f"Sent to Flask {flask_endpoint}: {response.status_code}")
        
        if response.status_code == 200:
            print("Flask update successful!")
            return response.json()
        else:
            print(f"Flask error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to Flask server - is it running on 127.0.0.1:5000?")
        return None
    except Exception as e:
        print(f"Error sending to Flask: {e}")
        return None

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
    
    def filter_patterns_by_focus(self, patterns: List[Dict[str, Any]], focus_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """Filter patterns to only include focus targets, or return all if no focus specified"""
        if not focus_patterns:
            return patterns  # No focus specified, return all patterns
        
        # Filter to only the patterns we want to focus on
        focused = [p for p in patterns if p['group_label'] in focus_patterns]
        return focused
    
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
        
        # sort into categories of levels
        highly_positive = [p for p in patterns if p['mood_change_from_avg'] > 2.0]
        moderately_positive = [p for p in patterns if 1.0 < p['mood_change_from_avg'] <= 2.0]
        neutral = [p for p in patterns if -1.0 <= p['mood_change_from_avg'] <= 1.0]
        moderately_negative = [p for p in patterns if -2.0 <= p['mood_change_from_avg'] < -1.0]
        highly_negative = [p for p in patterns if p['mood_change_from_avg'] < -2.0]
        
        # sort by confidence
        highly_positive.sort(key=lambda x: x['confidence'], reverse=True)
        highly_negative.sort(key=lambda x: x['confidence'], reverse=True)
        
        prompt = f"""
        BEHAVIORAL PATTERN ANALYSIS REPORT
        Analyze this user's 30-day behavioral baseline data:

        HIGHLY POSITIVE PATTERNS ({len(highly_positive)} detected):
        {self._format_patterns_for_prompt(highly_positive[:5])}  

        MODERATELY POSITIVE PATTERNS ({len(moderately_positive)} detected):
        {self._format_patterns_for_prompt(moderately_positive[:3])}

        NEUTRAL PATTERNS ({len(neutral)} detected):
        {self._format_patterns_for_prompt(neutral[:2])}

        MODERATELY NEGATIVE PATTERNS ({len(moderately_negative)} detected):
        {self._format_patterns_for_prompt(moderately_negative[:3])}

        HIGHLY NEGATIVE PATTERNS ({len(highly_negative)} detected):
        {self._format_patterns_for_prompt(highly_negative[:5])}

        Provide a BEHAVIORAL PATTERN ANALYSIS (not wellness advice):

        **STRONGEST POSITIVE PATTERNS:**
        For each high-confidence positive pattern, state: "[Pattern name]: [Confidence score] reliability, [mood impact] mood effect - [why this pattern works for them]"

        **MOST HARMFUL PATTERNS:**
        For each high-confidence negative pattern, state: "[Pattern name]: [Confidence score] reliability, [mood impact] mood drain - [why this pattern hurts them]"

        **PATTERN RELIABILITY INSIGHTS:**
        Which patterns have highest confidence scores and what that means for the user.

        **BEHAVIORAL PROFILE:**
        What type of behavioral profile this data reveals about the user.

        Focus on ANALYZING their actual detected patterns, not giving advice.
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
    
    def analyze_patterns(self, patterns: List[Dict[str, Any]], focus_context: str = "") -> Dict[str, Any]:
        if not patterns:
            return {"insights": "No significant patterns detected yet. Continue logging daily activities."}
        
        # compare against baseline if available
        baseline_context = ""
        if self.baseline_established and self.baseline_patterns:
            baseline_context = f"\nBaseline context: User has {len(self.baseline_patterns)} established baseline patterns for comparison. "
        
        positive_patterns = [p for p in patterns if p['mood_change_from_avg'] > 1.0]
        negative_patterns = [p for p in patterns if p['mood_change_from_avg'] < -1.0]
        all_patterns = patterns  # Include ALL patterns for comprehensive analysis
        
        prompt = f"""
        BEHAVIORAL PATTERN ANALYSIS UPDATE
        
        Analyze these SPECIFIC DETECTED PATTERNS from the user's actual behavior data:{baseline_context}{focus_context}

        ALL DETECTED PATTERNS ({len(all_patterns)} total):
        {self._format_patterns_for_prompt(all_patterns)}

        Provide a PATTERN ANALYSIS REPORT (not generic advice):

        **PATTERN STATUS ANALYSIS:**
        For EACH pattern above, provide analysis in this format:
        - [Pattern Name]: [Confidence score] confidence, [mood impact] mood effect, [energy impact] energy effect
          Status: [Is this pattern helping, hurting, or neutral? Based on the actual numbers]
          Reliability: [What does the confidence score tell us about this pattern's consistency?]

        **PATTERN OPTIMIZATION INSIGHTS:**
        - Strongest reliable positive patterns: [List patterns with confidence >0.7 AND positive mood impact]
        - Patterns needing attention: [List patterns with negative mood impact]
        - Inconsistent patterns: [List patterns with confidence <0.5]

        **BEHAVIORAL TRENDS:**
        Based on confidence scores and impact data, what trends do you see in their actual behavior?

        CRITICAL: Analyze the ACTUAL PATTERNS and their SPECIFIC NUMBERS. Do not say "no patterns found" when patterns are clearly listed above.
        """
        
        analysis = self._call_asi_mini(prompt, max_tokens=800)
        
        return {
            "insights": analysis,
            "positive_patterns": positive_patterns,
            "negative_patterns": negative_patterns,
            "all_patterns": all_patterns,
            "pattern_count": len(patterns)
        }

    def generate_pattern_optimizations(self, patterns: List[Dict[str, Any]], focus_context: str = "", current_mood: int = None, current_energy: int = None) -> str:
        """Generate pattern-specific optimization strategies"""
        if not patterns:
            return "No patterns available for optimization analysis."
        
        high_confidence_positive = [p for p in patterns if p['confidence'] > 0.7 and p['mood_change_from_avg'] > 1.0]
        high_confidence_negative = [p for p in patterns if p['confidence'] > 0.7 and p['mood_change_from_avg'] < -1.0]
        low_confidence_patterns = [p for p in patterns if p['confidence'] < 0.5]
        
        mood_context = f"Current mood: {current_mood}/10, " if current_mood else ""
        energy_context = f"Current energy: {current_energy}/10, " if current_energy else ""
        
        prompt = f"""
        PATTERN OPTIMIZATION STRATEGIES

        Based on the user's ACTUAL BEHAVIORAL PATTERNS, provide specific optimization strategies:{focus_context}

        {mood_context}{energy_context}

        HIGH-CONFIDENCE POSITIVE PATTERNS (Reliable Mood Boosters):
        {self._format_patterns_for_prompt(high_confidence_positive)}

        HIGH-CONFIDENCE NEGATIVE PATTERNS (Reliable Mood Drains):
        {self._format_patterns_for_prompt(high_confidence_negative)}

        LOW-CONFIDENCE PATTERNS (Inconsistent Results):
        {self._format_patterns_for_prompt(low_confidence_patterns)}

        Provide PATTERN-SPECIFIC OPTIMIZATION STRATEGIES:

        **MAXIMIZE RELIABLE POSITIVE PATTERNS:**
        For each high-confidence positive pattern, explain:
        - Why this pattern works so well for them (based on confidence and impact scores)
        - Specific ways to get more benefit from this existing habit
        - How to protect/prioritize this pattern

        **MODIFY HARMFUL PATTERNS:**
        For each high-confidence negative pattern, explain:
        - Why this pattern consistently hurts them (based on the data)
        - Specific strategies to reduce or modify this pattern
        - Replacement activities that might work better

        **STABILIZE INCONSISTENT PATTERNS:**
        For low-confidence patterns, explain:
        - Why results vary (based on confidence scores)
        - How to make these patterns more consistently beneficial

        Focus on THEIR SPECIFIC PATTERNS and ACTUAL DATA, not generic wellness tips.
        """
        
        return self._call_asi_mini(prompt, max_tokens=600)

    def _format_patterns_for_prompt(self, patterns: List[Dict[str, Any]]) -> str:
        """Format patterns for AI prompt"""
        if not patterns:
            return "None detected"
        
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
    """Handle original pattern analysis messages (for backwards compatibility)"""
    # Convert to new format
    new_msg = PatternAnalysisForPlannerMessage(
        patterns=msg.patterns,
        user_id=msg.user_id,
        total_patterns=msg.total_patterns,
        high_confidence_patterns=msg.high_confidence_patterns,
        focus_patterns=[],  # No focus for original messages
        trigger_reason="",
        is_baseline=msg.is_baseline
    )
    await handle_focused_pattern_analysis(ctx, sender, new_msg)

@planner_agent.on_message(model=PatternAnalysisForPlannerMessage)
async def handle_focused_pattern_analysis(ctx: Context, sender: str, msg: PatternAnalysisForPlannerMessage):
    ctx.logger.info(f"Processing pattern analysis from {sender}")
    ctx.logger.info(f"Received {msg.total_patterns} patterns, {msg.high_confidence_patterns} high confidence")
    ctx.logger.info(f"Is baseline: {msg.is_baseline}")
    
    if msg.focus_patterns:
        ctx.logger.info(f"FOCUSING ON: {msg.focus_patterns}")
        ctx.logger.info(f"Trigger reason: {msg.trigger_reason}")

    if wellness_planner is None:
        ctx.logger.error("Wellness planner not initialized yet!")
        return

    try:
        # Filter patterns based on focus
        patterns_to_analyze = wellness_planner.filter_patterns_by_focus(msg.patterns, msg.focus_patterns)
        
        if msg.focus_patterns:
            ctx.logger.info(f"Filtered to {len(patterns_to_analyze)} focused patterns from {len(msg.patterns)} total")
        
        # Send patterns to Flask server
        def send_patterns_to_flask():
            try:
                send_to_flask_server("/api/agent_update/patterns", {
                    "patterns": msg.patterns,
                    "focus_patterns": msg.focus_patterns,
                    "trigger_reason": msg.trigger_reason,
                    "is_baseline": msg.is_baseline
                })
            except Exception as e:
                ctx.logger.error(f"Error sending patterns to Flask: {e}")
        
        # Send in background thread
        threading.Thread(target=send_patterns_to_flask).start()
        
        # Create focus context for AI
        focus_context = ""
        if msg.focus_patterns:
            focus_context = f"\n\nSPECIAL FOCUS: This analysis is specifically focusing on the '{', '.join(msg.focus_patterns)}' pattern(s) due to: {msg.trigger_reason}"
        
        if msg.is_baseline:
            # Handle comprehensive baseline establishment (use all patterns)
            ctx.logger.info("Processing COMPREHENSIVE BASELINE analysis...")
            analysis = wellness_planner.analyze_baseline_patterns(msg.patterns)  # Use all patterns for baseline
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
            ctx.logger.info(f"BASELINE PATTERN ANALYSIS:\n{analysis['baseline_analysis']}")
            ctx.logger.info("=" * 80)
            ctx.logger.info("BASELINE ESTABLISHED! Ready for daily entries.")
            ctx.logger.info("=" * 80)
            
        else:
            # Handle regular daily analysis with focus
            ctx.logger.info("Processing PATTERN ANALYSIS update...")
            analysis = wellness_planner.analyze_patterns(patterns_to_analyze, focus_context)
            optimizations = wellness_planner.generate_pattern_optimizations(patterns_to_analyze, focus_context)
            
            # Send recommendations to Flask for each pattern
            def send_recommendations_to_flask():
                try:
                    for pattern in patterns_to_analyze:
                        pattern_id = pattern.get('group_label', 'unknown')
                        
                        # Parse the optimization strategies into a list
                        strategies_list = []
                        if optimizations:
                            # Split by sections and extract bullet points
                            lines = optimizations.split('\n')
                            current_strategies = []
                            for line in lines:
                                line = line.strip()
                                if line.startswith('-') or line.startswith('•'):
                                    current_strategies.append(line[1:].strip())
                                elif line and not line.startswith('**') and current_strategies:
                                    strategies_list.extend(current_strategies)
                                    current_strategies = []
                            if current_strategies:
                                strategies_list.extend(current_strategies)
                        
                        # If no strategies parsed, use the full text
                        if not strategies_list:
                            strategies_list = [optimizations] if optimizations else ["Generating strategies..."]
                        
                        recommendation_data = {
                            "pattern_id": pattern_id,
                            "recommendation": {
                                "title": f"AI Insights for {pattern_id.title()}",
                                "analysis": analysis.get('insights', 'Analysis in progress...'),
                                "strategies": strategies_list[:7],  # Limit to 7 strategies
                                "last_update": "now",
                                "source": "ai_agents"
                            }
                        }
                        send_to_flask_server("/api/agent_update/recommendations", recommendation_data)
                except Exception as e:
                    ctx.logger.error(f"Error sending recommendations to Flask: {e}")
            
            # Send recommendations in background
            threading.Thread(target=send_recommendations_to_flask).start()
            
            # Create habit change plans for concerning patterns (from focused set)
            habit_plans = []
            concerning_patterns = [p for p in patterns_to_analyze if p['mood_change_from_avg'] < -2.0 and p['confidence'] > 0.5]
            
            for pattern in concerning_patterns[:2]:  # Limit to top 2 concerning patterns
                habit_plan = {
                    "target_activity": pattern['group_label'],
                    "change_direction": "reduce",
                    "confidence": pattern['confidence'],
                    "impact": pattern['mood_change_from_avg']
                }
                habit_plans.append(habit_plan)
            
            # Log pattern analysis results
            ctx.logger.info("=" * 60)
            if msg.focus_patterns:
                ctx.logger.info(f"FOCUSED PATTERN ANALYSIS: {', '.join(msg.focus_patterns)}")
                ctx.logger.info(f"Reason: {msg.trigger_reason}")
            else:
                ctx.logger.info("BEHAVIORAL PATTERN ANALYSIS UPDATE")
            ctx.logger.info("=" * 60)
            
            if msg.focus_patterns:
                ctx.logger.info(f"Analyzing {len(patterns_to_analyze)} focused patterns (from {msg.total_patterns} total)")
            else:
                ctx.logger.info(f"Current patterns: {msg.total_patterns} total, {msg.high_confidence_patterns} high confidence")
            
            ctx.logger.info(f"PATTERN ANALYSIS:\n{analysis['insights']}")
            ctx.logger.info("-" * 30)
            ctx.logger.info(f"OPTIMIZATION STRATEGIES:\n{optimizations}")
            
            if habit_plans:
                ctx.logger.info("-" * 30)
                ctx.logger.info("HIGH-PRIORITY PATTERN MODIFICATIONS:")
                for plan in habit_plans:
                    ctx.logger.info(f"  • Reduce: {plan['target_activity']} (impact: {plan['impact']:.1f}, confidence: {plan['confidence']:.2f})")
            
            ctx.logger.info("=" * 60)
        
    except Exception as e:
        ctx.logger.error(f"Error processing pattern analysis: {str(e)}")

@planner_agent.on_message(model=ImmediatePlannerUpdateMessage)
async def handle_immediate_update(ctx: Context, sender: str, msg: ImmediatePlannerUpdateMessage):
    """Handle immediate planner updates (like user feedback)"""
    ctx.logger.info(f"IMMEDIATE PATTERN UPDATE from {sender}")
    ctx.logger.info(f"Reason: {msg.reason}")
    ctx.logger.info(f"Focus patterns: {msg.patterns_to_focus}")
    
    if wellness_planner is None:
        ctx.logger.error("Wellness planner not initialized!")
        return
    
    try:
        # Filter to only the focus patterns
        patterns_to_analyze = wellness_planner.filter_patterns_by_focus(msg.updated_patterns, msg.patterns_to_focus)
        
        # Send updated patterns to Flask
        def send_immediate_patterns_to_flask():
            try:
                send_to_flask_server("/api/agent_update/patterns", {
                    "patterns": msg.updated_patterns,
                    "focus_patterns": msg.patterns_to_focus,
                    "trigger_reason": msg.reason,
                    "is_baseline": False
                })
            except Exception as e:
                ctx.logger.error(f"Error sending immediate patterns to Flask: {e}")
        
        threading.Thread(target=send_immediate_patterns_to_flask).start()
        
        ctx.logger.info("=" * 60)
        ctx.logger.info("IMMEDIATE PATTERN ANALYSIS UPDATE")
        ctx.logger.info("=" * 60)
        ctx.logger.info(f"Trigger: {msg.reason}")
        ctx.logger.info(f"Affected patterns: {', '.join(msg.patterns_to_focus)}")
        ctx.logger.info(f"Analyzing {len(patterns_to_analyze)} targeted patterns")
        
        focus_context = f"\n\nIMMEDIATE FOCUS: This analysis is specifically responding to user feedback about '{', '.join(msg.patterns_to_focus)}'. Reason: {msg.reason}"
        
        analysis = wellness_planner.analyze_patterns(patterns_to_analyze, focus_context)
        optimizations = wellness_planner.generate_pattern_optimizations(patterns_to_analyze, focus_context)
        
        # Send immediate recommendations update
        def send_immediate_recommendations_to_flask():
            try:
                for pattern in patterns_to_analyze:
                    pattern_id = pattern.get('group_label', 'unknown')
                    
                    # Parse strategies
                    strategies_list = []
                    if optimizations:
                        lines = optimizations.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('-') or line.startswith('•'):
                                strategies_list.append(line[1:].strip())
                    
                    if not strategies_list:
                        strategies_list = [optimizations] if optimizations else ["Updated strategies based on your feedback..."]
                    
                    recommendation_data = {
                        "pattern_id": pattern_id,
                        "recommendation": {
                            "title": f"Updated AI Insights for {pattern_id.title()}",
                            "analysis": f"UPDATED BASED ON YOUR FEEDBACK: {analysis.get('insights', 'Analysis updated...')}",
                            "strategies": strategies_list[:7],
                            "last_update": "just now",
                            "source": "ai_agents_feedback"
                        }
                    }
                    send_to_flask_server("/api/agent_update/recommendations", recommendation_data)
            except Exception as e:
                ctx.logger.error(f"Error sending immediate recommendations to Flask: {e}")
        
        threading.Thread(target=send_immediate_recommendations_to_flask).start()
        
        ctx.logger.info("UPDATED PATTERN ANALYSIS:")
        ctx.logger.info(analysis['insights'])
        ctx.logger.info("-" * 30)
        ctx.logger.info("REVISED OPTIMIZATION STRATEGIES:")
        ctx.logger.info(optimizations)
        ctx.logger.info("=" * 60)
        
    except Exception as e:
        ctx.logger.error(f"Error in immediate pattern update: {str(e)}")

if __name__ == "__main__":
    planner_agent.run()