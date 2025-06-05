from uagents import Agent, Context, Model
from typing import List, Dict, Any, Optional

# Message models
class PatternAnalysisMessage(Model):
    patterns: List[Dict[str, Any]]
    user_id: str
    total_patterns: int
    high_confidence_patterns: int
    is_baseline: bool = False

class UserFeedbackMessage(Model):
    pattern_id: str
    feedback_type: str  # "BAD idea", "unsure about idea", "GREAT idea"
    user_comment: str
    user_id: str

class ConfidenceUpdateMessage(Model):
    pattern_id: str
    confidence_adjustment: float
    user_id: str
    reason: str

class PlannerTriggerMessage(Model):
    user_id: str
    reason: str
    patterns_to_focus: List[str]

class ImmediatePlannerUpdateMessage(Model):
    user_id: str
    reason: str
    patterns_to_focus: List[str]
    updated_patterns: List[Dict[str, Any]]

curator_agent = Agent(
    name="curator_agent",
    seed="curator_seed", 
    port=8005,
    endpoint=["http://127.0.0.1:8005/submit"]
)

class PatternCurator:
    def __init__(self, confidence_threshold=0.3, significant_change_threshold=0.2):
        self.confidence_threshold = confidence_threshold
        self.significant_change_threshold = significant_change_threshold
        self.last_sent_patterns = {}
        self.current_patterns = []  # Keep track of current patterns
        self.suppressed_patterns = set()
        self.user_validated_patterns = set()
    
    def should_trigger_planner_update(self, current_patterns: List[Dict[str, Any]], user_id: str) -> tuple[bool, List[str], List[str]]:
        """
        Returns: (should_trigger, reasons, affected_patterns)
        """
        reasons = []
        affected_patterns = []
        
        # Always trigger on baseline
        if not self.last_sent_patterns:
            return True, ["baseline_initialization"], []
        
        # Create current pattern lookup by ID for easier comparison
        current_by_id = {p['group_label']: p for p in current_patterns}
        
        # Check for new high-confidence patterns
        current_high_conf = {p['group_label']: p for p in current_patterns 
                           if p['confidence'] >= self.confidence_threshold}
        last_high_conf = set(self.last_sent_patterns.keys())
        
        new_patterns = set(current_high_conf.keys()) - last_high_conf
        if new_patterns:
            reasons.append(f"new_high_confidence_patterns: {list(new_patterns)}")
            affected_patterns.extend(new_patterns)
        
        # Check for significant confidence changes in ALL patterns
        for pattern_id, last_pattern in self.last_sent_patterns.items():
            if pattern_id in current_by_id:
                current_pattern = current_by_id[pattern_id]
                last_conf = last_pattern['confidence']
                current_conf = current_pattern['confidence']
                conf_change = abs(current_conf - last_conf)
                
                if conf_change >= self.significant_change_threshold:
                    reasons.append(f"confidence_change_{pattern_id}: {last_conf:.2f} -> {current_conf:.2f}")
                    affected_patterns.append(pattern_id)
        
        # Check for patterns dropping below threshold
        dropped_patterns = last_high_conf - set(current_high_conf.keys())
        if dropped_patterns:
            reasons.append(f"patterns_dropped_below_threshold: {list(dropped_patterns)}")
            affected_patterns.extend(dropped_patterns)
        
        return len(reasons) > 0, reasons, affected_patterns
    
    def update_memory(self, patterns: List[Dict[str, Any]]):
        """Update memory of what patterns we've seen"""
        self.current_patterns = patterns.copy()  # Keep current patterns
        self.last_sent_patterns = {}
        for pattern in patterns:
            # Store ALL patterns, not just high confidence ones
            self.last_sent_patterns[pattern['group_label']] = {
                'confidence': pattern['confidence'],
                'effect_on_mood': pattern['effect_on_mood'],
                'effect_on_energy': pattern['effect_on_energy']
            }
    
    def apply_feedback_to_current_patterns(self, pattern_id: str, confidence_adjustment: float) -> List[Dict[str, Any]]:
        """Apply feedback adjustment to current patterns and return updated patterns"""
        updated_patterns = []
        for pattern in self.current_patterns:
            if pattern['group_label'] == pattern_id:
                # Apply the confidence adjustment
                new_confidence = max(0.0, min(1.0, pattern['confidence'] + confidence_adjustment))
                updated_pattern = pattern.copy()
                updated_pattern['confidence'] = new_confidence
                updated_patterns.append(updated_pattern)
            else:
                updated_patterns.append(pattern.copy())
        
        self.current_patterns = updated_patterns  # Update our current state
        return updated_patterns
    
    def process_user_feedback(self, feedback: UserFeedbackMessage) -> tuple[Optional[ConfidenceUpdateMessage], List[Dict[str, Any]]]:
        """Process user feedback and return confidence adjustment + updated patterns"""
        pattern_id = feedback.pattern_id
        
        if feedback.feedback_type == "BAD idea":
            self.suppressed_patterns.add(pattern_id)
            adjustment = -0.6
            updated_patterns = self.apply_feedback_to_current_patterns(pattern_id, adjustment)
            return (ConfidenceUpdateMessage(
                pattern_id=pattern_id,
                confidence_adjustment=adjustment,
                user_id=feedback.user_id,
                reason=f"User feedback: BAD idea - {feedback.user_comment}"
            ), updated_patterns)
        elif feedback.feedback_type == "unsure about idea":
            adjustment = -0.2
            updated_patterns = self.apply_feedback_to_current_patterns(pattern_id, adjustment)
            return (ConfidenceUpdateMessage(
                pattern_id=pattern_id,
                confidence_adjustment=adjustment,
                user_id=feedback.user_id,
                reason=f"User feedback: unsure about idea - {feedback.user_comment}"
            ), updated_patterns)
        elif feedback.feedback_type == "GREAT idea":
            self.user_validated_patterns.add(pattern_id)
            adjustment = 0.3
            updated_patterns = self.apply_feedback_to_current_patterns(pattern_id, adjustment)
            return (ConfidenceUpdateMessage(
                pattern_id=pattern_id,
                confidence_adjustment=adjustment,
                user_id=feedback.user_id,
                reason=f"User feedback: GREAT idea - {feedback.user_comment}"
            ), updated_patterns)
        
        return None, self.current_patterns

pattern_curator = None

@curator_agent.on_event("startup")
async def initialize_curator(ctx: Context):
    global pattern_curator
    pattern_curator = PatternCurator()
    ctx.logger.info("Pattern Curator initialized")

@curator_agent.on_message(model=PatternAnalysisMessage)
async def handle_pattern_analysis(ctx: Context, sender: str, msg: PatternAnalysisMessage):
    """Decide whether pattern_finder should update planner"""
    ctx.logger.info(f"Curator evaluating {msg.total_patterns} patterns")
    
    if pattern_curator is None:
        ctx.logger.error("Pattern curator not initialized!")
        return
    
    try:
        should_trigger, reasons, affected_patterns = pattern_curator.should_trigger_planner_update(
            msg.patterns, msg.user_id
        )
        
        if should_trigger or msg.is_baseline:
            ctx.logger.info("CURATOR DECISION: Triggering planner update")
            ctx.logger.info(f"Reasons: {reasons}")
            ctx.logger.info(f"Affected patterns: {affected_patterns}")
            
            # Tell pattern_finder to send to planner
            trigger_msg = PlannerTriggerMessage(
                user_id=msg.user_id,
                reason="; ".join(reasons),
                patterns_to_focus=affected_patterns
            )
            
            # Send trigger back to pattern_finder
            await ctx.send("agent1qggee7fyd8fjtm379ggavw3h0uckmgglwnj35e8gte5a4ev4kry3ss788jf", trigger_msg)
            
            # Update our memory
            pattern_curator.update_memory(msg.patterns)
            
            ctx.logger.info("Sent planner trigger to pattern_finder")
        else:
            ctx.logger.info("CURATOR DECISION: No significant changes, not triggering planner")
            # Still update memory even if not triggering
            pattern_curator.update_memory(msg.patterns)
    
    except Exception as e:
        ctx.logger.error(f"Error in curator: {str(e)}")

@curator_agent.on_message(model=UserFeedbackMessage)
async def handle_user_feedback(ctx: Context, sender: str, msg: UserFeedbackMessage):
    """Handle user feedback and trigger immediate planner update"""
    ctx.logger.info(f"User feedback for '{msg.pattern_id}': {msg.feedback_type}")
    
    if pattern_curator is None:
        return
    
    try:
        confidence_update, updated_patterns = pattern_curator.process_user_feedback(msg)
        
        if confidence_update:
            ctx.logger.info(f"Applying confidence adjustment: {confidence_update.confidence_adjustment:+.2f}")
            
            # Send confidence update to pattern_finder
            await ctx.send("agent1qggee7fyd8fjtm379ggavw3h0uckmgglwnj35e8gte5a4ev4kry3ss788jf", confidence_update)
            
            # IMMEDIATELY trigger planner update with the affected pattern
            ctx.logger.info("IMMEDIATE PLANNER UPDATE: Triggering due to user feedback")
            immediate_update = ImmediatePlannerUpdateMessage(
                user_id=msg.user_id,
                reason=f"immediate_user_feedback: {msg.feedback_type} for {msg.pattern_id}",
                patterns_to_focus=[msg.pattern_id],
                updated_patterns=updated_patterns
            )
            
            # Send immediate update to planner
            await ctx.send("agent1qwvypts2ft35u3w4uhg8da0cj5edkmp0k7slvjqtekas26t4evxj7xk7a4g", immediate_update)
            ctx.logger.info("Sent immediate planner update")
            
    except Exception as e:
        ctx.logger.error(f"Error processing feedback: {str(e)}")

if __name__ == "__main__":
    curator_agent.run()