'''
WAIT FOR ALL 3 OTHER AGENTS TO FINISHING SETTING UP BEFORE RUNNING THIS FILE
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

test_new_entry = Agent(
    name="test_new_entry",
    seed="test_new_entry_seed",
    port=8004
)

@test_new_entry.on_event("startup")
async def send_new_entry(ctx: Context):
    
    ctx.logger.info("Sending first new daily entry...")
    
    # First example test
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
    
    # sneding
    await ctx.send("agent1qwcrrpsgl49tqn50gmsyesq48g3v7mchzmhr6074tn94fw8dqzepxxds4vm", new_entry)
    ctx.logger.info("Sent first daily entry to extractor for processing")
    
    # try a second one
    ctx.logger.info("Waiting 30 seconds before sending second entry...")
    await asyncio.sleep(30)
    
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
    
    ctx.logger.info("All test entries sent successfully!")

if __name__ == "__main__":
    test_new_entry.run()