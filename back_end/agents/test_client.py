'''
WAIT FOR ALL 4 AGENTS TO FINISH SETTING UP BEFORE RUNNING THIS FILE
(extractor, pattern_finder, curator, planner)
'''

from uagents import Agent, Context, Model
import asyncio
from typing import List, Tuple

#copy of what extractor expects (somehow doesnt work on import)
class DailyEntryMessage(Model):
    entry_text: str
    mood_rating: int
    energy_rating: int
    user_id: str = "default_user"

# Copy of what curator expects for user feedback
class UserFeedbackMessage(Model):
    pattern_id: str
    feedback_type: str  # "BAD idea", "unsure about idea", "GREAT idea" HORRIBLE FORMAT LOL TOO LAZY
    user_comment: str
    user_id: str

test_agent = Agent(
    name="test_agent",
    seed="test_agent_seed",
    port=8004
)

@test_agent.on_event("startup")
async def run_complete_test(ctx: Context):
    
    #Send daily entries to test the pipeline
    ctx.logger.info("=== STEP 1: Testing daily entry pipeline ===")
    
    ctx.logger.info("Sending first new daily entry...")
    
    new_entry = DailyEntryMessage(
        entry_text="""Had an amazing morning yoga session followed by a healthy smoothie. 
        Work was challenging but I felt focused and productive. Lunch with a colleague turned into 
        great brainstorming. Afternoon I got caught up scrolling social media for too long and 
        felt my energy drop. Recovered by going for a walk and cooking a nice dinner. 
        Video called my sister before bed which always makes me happy.""",
        mood_rating=7,
        energy_rating=6,
        user_id="daily_user"
    )
    
    # Send to extractor
    await ctx.send("agent1qwcrrpsgl49tqn50gmsyesq48g3v7mchzmhr6074tn94fw8dqzepxxds4vm", new_entry)
    ctx.logger.info("Sent first daily entry to extractor")
    
    # try a second one
    ctx.logger.info("Waiting 30 seconds before sending second entry...")
    await asyncio.sleep(30)
    
    # Second daily entry
    ctx.logger.info("Sending second new daily entry...")
    
    another_entry = DailyEntryMessage(
        entry_text="""Woke up late and felt rushed all morning. Skipped breakfast and just grabbed coffee. 
        Spent most of my work breaks scrolling Instagram which made me feel worse about myself. 
        Had a stressful meeting that didn't go well. Evening was better - cooked a simple meal 
        and watched a funny movie that lifted my spirits.""",
        mood_rating=4,
        energy_rating=3,
        user_id="daily_user"
    )
    
    await ctx.send("agent1qwcrrpsgl49tqn50gmsyesq48g3v7mchzmhr6074tn94fw8dqzepxxds4vm", another_entry)
    ctx.logger.info("Sent second daily entry to extractor")
    
    # Wait for processing
    ctx.logger.info("Waiting 40 seconds for pattern analysis...")
    await asyncio.sleep(40)
    
    # Third daily entry to trigger more patterns
    ctx.logger.info("Sending third daily entry...")
    
    third_entry = DailyEntryMessage(
        entry_text="""Started day with intense gym workout - felt incredible afterward. 
        Had productive meetings all morning. Lunch was meal prep from yesterday which saved time. 
        Afternoon was focused coding session. Evening spent cooking elaborate dinner while 
        listening to podcasts. Went to bed early feeling accomplished.""",
        mood_rating=8,
        energy_rating=9,
        user_id="daily_user"
    )
    
    await ctx.send("agent1qwcrrpsgl49tqn50gmsyesq48g3v7mchzmhr6074tn94fw8dqzepxxds4vm", third_entry)
    ctx.logger.info("Sent third daily entry to extractor")
    
    # Step 2: Test user feedback system (only one feedback)
    ctx.logger.info("=== STEP 2: Testing user feedback system ===")
    ctx.logger.info("Waiting 30 seconds before testing feedback...")
    await asyncio.sleep(30)
    
    # Test "BAD idea" feedback - this will suppress the pattern and significantly reduce confidence
    ctx.logger.info("Sending negative feedback for social media pattern...")
    negative_feedback = UserFeedbackMessage(
        pattern_id="social_media",
        feedback_type="BAD idea", 
        user_comment="I can't control my social media usage, this advice isn't realistic for me.",
        user_id="daily_user"
    )
    
    await ctx.send("agent1qdr8zekrarc5hhyhxju7suyr8nfxe6j8q9kgxa9007v8wmdvraw9z0uw37v", negative_feedback)
    ctx.logger.info("Sent negative feedback to curator")
    
    # Step 3: Send another daily entry to see how feedback affected the system
    ctx.logger.info("=== STEP 3: Testing feedback impact ===")
    ctx.logger.info("Waiting 25 seconds before final entry...")
    await asyncio.sleep(25)
    
    ctx.logger.info("Sending final daily entry to test feedback impact...")
    final_entry = DailyEntryMessage(
        entry_text="""Morning started with gym session again - becoming a habit! 
        Work was smooth with good energy levels. Tried to limit social media but still 
        spent too much time scrolling during lunch. Cooked dinner but wasn't feeling 
        creative about it. Read a book before bed instead of screen time.""",
        mood_rating=7,
        energy_rating=7,
        user_id="daily_user"
    )
    
    await ctx.send("agent1qwcrrpsgl49tqn50gmsyesq48g3v7mchzmhr6074tn94fw8dqzepxxds4vm", final_entry)
    ctx.logger.info("Sent final daily entry to extractor")
    
    ctx.logger.info("=== ALL TESTS COMPLETED ===")
    ctx.logger.info("Check the logs to see how the 'BAD idea' feedback suppressed social media recommendations!")

if __name__ == "__main__":
    test_agent.run()