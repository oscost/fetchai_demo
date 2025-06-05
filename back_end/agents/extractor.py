import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import logging
logging.getLogger("transformers").setLevel(logging.WARNING)

from keybert import KeyBERT
from transformers import pipeline

from uagents import Agent, Context, Model
from typing import List, Tuple
import asyncio

daily_data = [
    # Pattern: Exercise + good mood + high energy
    ("""Woke up early and went for a 5-mile run before work. Felt energized all day. Had a productive morning at the office working on my presentation. Lunch with colleagues was fun - lots of laughing. Afternoon meetings went smoothly. Cooked a healthy dinner with vegetables and chicken. Read a book before bed feeling accomplished.""", 8, 8),
    
    # Pattern: Social media scrolling + low mood + low energy
    ("""Woke up and immediately spent 2 hours scrolling Instagram and TikTok in bed. Felt unmotivated to get up. Work was boring - just answered emails and did busy work. Spent lunch break browsing social media instead of eating properly. Afternoon dragged on forever. Ordered pizza for dinner and continued scrolling feeds until 2am.""", 3, 3),
    
    # Pattern: Social activities + high mood + moderate energy
    ("""Had brunch with my best friend Sarah - we laughed so much my cheeks hurt. Spent the afternoon shopping and catching up on life. Evening dinner party with college friends, played games and shared stories. Felt so grateful for these relationships. Went to bed happy and content.""", 9, 6),
    
    # Pattern: Poor sleep + low mood + very low energy
    ("""Stayed up until 3am binge-watching Netflix series. Woke up groggy and exhausted. Could barely focus at work - made several mistakes. Skipped lunch because I felt too tired to eat. Afternoon was a struggle to stay awward. Grabbed fast food on the way home and crashed on the couch.""", 3, 2),
    
    # Pattern: Cooking/meal prep + good mood + moderate energy
    ("""Spent the morning at the farmers market buying fresh ingredients. Came home and meal prepped for the entire week - made quinoa salads, roasted vegetables, and marinated chicken. Felt so organized and healthy. Cooked a elaborate dinner trying a new recipe. Kitchen smelled amazing.""", 7, 6),
    
    # Mixed day - exercise pattern
    ("""Started with yoga class at 7am which felt wonderful. Work was stressful with tight deadlines but I handled it well. Hit the gym after work for strength training. Cooked a simple but healthy dinner. Feeling strong and accomplished despite work stress.""", 8, 8),
    
    # Social media pattern
    ("""Lazy Sunday morning scrolling through social media for hours. Saw everyone's perfect vacation photos and felt inadequate. Spent most of the day on my phone checking various apps. Ordered takeout instead of cooking. Evening was just more screen time until very late.""", 4, 4),
    
    # Social pattern  
    ("""Video call with family for my nephew's birthday - he's so cute! Afternoon hanging out with roommates playing board games. Evening went to a friend's house warming party, met some new interesting people. Lots of good conversations and connections made.""", 8, 6),
    
    # Poor sleep pattern
    ("""Another late night gaming session until 4am. Overslept and was late for work. Boss wasn't happy about missing the morning meeting. Felt foggy and irritable all day. Made poor food choices - just snacks and coffee. Couldn't concentrate on anything.""", 2, 2),
    
    # Cooking pattern
    ("""Woke up inspired to try new recipes. Spent the morning making homemade bread and soup from scratch. The process was so meditative and rewarding. Shared the meal with neighbors who loved it. Evening planning next week's menu and organizing kitchen.""", 7, 6),
    
    # Exercise pattern
    ("""Joined a new fitness class - dance cardio was so fun! Made some new acquaintances in class. Work felt easier after that endorphin boost. Packed a healthy lunch I prepared yesterday. Evening walk with podcasts, feeling grateful for my body.""", 8, 9),
    
    # Regular day with some social media
    ("""Normal work day with meetings and project work. Lunch at desk while scrolling news and social feeds. Afternoon was productive. Quick grocery run after work. Simple dinner at home. Checked social media before bed and felt a bit envious of others' posts.""", 5, 5),
    
    # Social pattern
    ("""Surprise visit from old college friend who was in town! Spent the whole day reminiscing and exploring the city together. Went to our old favorite restaurant and laughed until we cried. Felt so connected and nostalgic in the best way.""", 9, 7),
    
    # Poor sleep + social media combination
    ("""Up late scrolling TikTok and Instagram, lost track of time until 2:30am. Woke up exhausted and late. Rushed through morning routine. Work was terrible - couldn't focus and felt behind all day. Lunch was more phone scrolling. Vicious cycle continued into evening.""", 3, 1),
    
    # Cooking pattern
    ("""Saturday dedicated to cooking! Made fresh pasta from scratch, prepared sauces, and baked cookies. Kitchen was my happy place today. Invited friends over to share the feast. Everyone complimented the food and I felt so proud of my skills.""", 8, 7),
    
    # Exercise pattern
    ("""Morning hike in the mountains with spectacular views. Fresh air and physical challenge felt amazing. Work seemed trivial after experiencing nature's beauty. Packed a nutritious lunch feeling energized. Evening gentle stretching and gratitude practice.""", 9, 9),
    
    # Regular day
    ("""Standard Tuesday routine - work, emails, meetings. Lunch at the office cafeteria. Afternoon project work was engaging. Commute home listening to music. Cooked a simple stir-fry dinner. Watched one episode of a show before reasonable bedtime.""", 6, 4),
    
    # Social media + low productivity
    ("""Woke up late and started day checking all social media platforms. Felt overwhelmed by everyone's achievements and travel posts. Work was unfocused - kept getting distracted by phone notifications. Lunch was fast food while browsing feeds. Unproductive afternoon.""", 4, 6),
    
    # Social pattern
    ("""Family dinner at my parents' house with siblings and their kids. Chaos but so much love and laughter. Played with nieces and nephews in the backyard. Felt grateful for family bonds. Drive home reflecting on how lucky I am.""", 8, 6),
    
    # Poor sleep pattern  
    ("""Binged an entire season of a show until 5am. Called in sick to work because I literally couldn't function. Spent the day in bed feeling guilty and exhausted. Ordered junk food delivery. Another wasted day due to poor sleep choices.""", 2, 1),
    
    # Cooking + social combination
    ("""Hosted dinner party for six friends - spent all day preparing multiple courses. Everyone brought wine and we had such a wonderful evening. Food turned out perfectly and friends were impressed. Felt like a successful adult who can actually cook!""", 8, 7),
    
    # Exercise pattern
    ("""New personal record at the gym today! Felt incredibly strong during weightlifting session. Work productivity was through the roof afterward. Healthy lunch felt like fuel rather than just food. Evening was calm and satisfied, early bedtime.""", 9, 9),
    
    # Social media pattern
    ("""Spent way too much time comparing myself to influencers on Instagram. Work was distracted by constant phone checking. Lunch scrolling made me feel worse about my life choices. Evening was more mindless scrolling instead of doing anything productive.""", 3, 3),
    
    # Social pattern
    ("""Girls' night out with friends - dinner, drinks, and dancing! Laughed until my stomach hurt and danced until my feet were sore. Felt so alive and connected to my friend group. Uber ride home was full of happy chattering about the night.""", 9, 7),
    
    # Poor sleep + cascade effect
    ("""Another 3am bedtime due to anxiety scrolling news and social media. Woke up anxious and tired. Work was overwhelming - everything felt impossible. Skipped gym because too exhausted. Fast food dinner while staring at screens. Cycle repeating.""", 3, 2),
    
    # Cooking pattern
    ("""Sunday meal prep session turned into creative cooking experiment. Tried three new recipes and they all worked! Portioned everything for the week ahead. Kitchen dance party while cooking. Feeling prepared and nourished for the week.""", 7, 6),
    
    # Exercise pattern
    ("""Beach volleyball game with friends combined exercise and social time perfectly. Sun, sand, competition, and laughter. Post-game seafood dinner by the ocean. Drive home with windows down feeling grateful for active lifestyle and good friends.""", 9, 8),
    
    # Mixed day
    ("""Productive work morning followed by lunch meeting that went well. Afternoon grocery shopping and errands. Evening cooking while video chatting with long-distance friend. Moderate day with good moments and necessary tasks completed.""", 6, 6),
    
    # Social media pattern
    ("""Rabbit hole of social media started early and continued all day. Felt increasingly inadequate seeing everyone's highlight reels. Work suffered from constant distraction. Lunch was rushed while scrolling. Evening was more of the same mindless consumption.""", 4, 3),
    
    # Grand finale - multiple positive patterns
    ("""Perfect day combining everything I love! Morning workout class with friends, farmers market shopping, afternoon cooking with roommate, evening dinner party we hosted. Felt energized, social, creative, and accomplished. This is how life should feel!""", 10, 9)
]

seed_keywords = [
    # Morning routine activities
    "wake up", "snooze alarm", "stretch", "check phone", "use bathroom", "brush teeth", "shower", 
    "wash hair", "shave", "moisturize", "get dressed", "make bed", "make coffee", "drink water", "breakfast",
    
    # Meals and cooking
    "breakfast", "lunch", "dinner", "snack", "cook", "order takeout", "grocery shopping", 
    "wash dishes", "eat leftovers", "drink tea", "meal prep",
    
    # Work activities
    "commute", "check emails", "attend meetings", "make phone calls", "write reports", "use computer", 
    "take notes", "brainstorm", "problem solve", "collaborate", "present", "research",
    
    # Exercise and health
    "gym workout", "run", "walk", "bike ride", "yoga", "stretch", "dance", "sports", "hike", 
    "swimming", "take vitamins", "meditate", "physical therapy",
    
    # Learning and development
    "study", "read books", "take classes", "watch tutorials", "practice skills", "do homework", 
    "attend lectures", "listen to podcasts", "watch documentaries", "learn language",
    
    # Social activities
    "text friends", "video call family", "social media", "meet friends", "date night", "party", 
    "networking", "deep conversations", "comfort others", "receive support",
    
    # Entertainment
    "watch tv", "stream movies", "play video games", "listen to music", "play instruments", 
    "sing", "draw", "paint", "write", "photography",
    
    # Household and personal care
    "clean house", "do laundry", "vacuum", "organize", "declutter", "pay bills", "budget", 
    "online shopping", "browse internet", "scroll feeds",
    
    # Outdoor and errands
    "drive car", "take public transport", "walk outside", "enjoy nature", "sit in park", 
    "run errands", "visit stores", "get haircut", "doctor appointment",
    
    # Family and relationships
    "call parents", "visit family", "babysit", "help neighbors", "volunteer work", "feed pets", 
    "walk dog", "play with pets",
    
    # Self-care and rest
    "take breaks", "power nap", "rest", "sleep", "journal writing", "reflect", "set goals"
]

seed_keywords = [
    # Morning routine activities
    "wake up", "snooze alarm", "stretch", "check phone", "use bathroom", "brush teeth", "shower", 
    "wash hair", "shave", "moisturize", "get dressed", "make bed", "make coffee", "drink water", "breakfast",
    
    # Meals and cooking
    "breakfast", "lunch", "dinner", "snack", "cook", "order takeout", "grocery shopping", 
    "wash dishes", "eat leftovers", "drink tea", "meal prep",
    
    # Work activities
    "commute", "check emails", "attend meetings", "make phone calls", "write reports", "use computer", 
    "take notes", "brainstorm", "problem solve", "collaborate", "present", "research",
    
    # Exercise and health
    "gym workout", "run", "walk", "bike ride", "yoga", "stretch", "dance", "sports", "hike", 
    "swimming", "take vitamins", "meditate", "physical therapy",
    
    # Learning and development
    "study", "read books", "take classes", "watch tutorials", "practice skills", "do homework", 
    "attend lectures", "listen to podcasts", "watch documentaries", "learn language",
    
    # Social activities
    "text friends", "video call family", "social media", "meet friends", "date night", "party", 
    "networking", "deep conversations", "comfort others", "receive support",
    
    # Entertainment
    "watch tv", "stream movies", "play video games", "listen to music", "play instruments", 
    "sing", "draw", "paint", "write", "photography",
    
    # Household and personal care
    "clean house", "do laundry", "vacuum", "organize", "declutter", "pay bills", "budget", 
    "online shopping", "browse internet", "scroll feeds",
    
    # Outdoor and errands
    "drive car", "take public transport", "walk outside", "enjoy nature", "sit in park", 
    "run errands", "visit stores", "get haircut", "doctor appointment",
    
    # Family and relationships
    "call parents", "visit family", "babysit", "help neighbors", "volunteer work", "feed pets", 
    "walk dog", "play with pets",
    
    # Self-care and rest
    "take breaks", "power nap", "rest", "sleep", "journal writing", "reflect", "set goals"
]

# uAgent message design
class DailyEntryMessage(Model):
    entry_text: str
    mood_rating: int
    energy_rating: int
    user_id: str = "default_user"

class ExtractedDataMessage(Model):
    keywords: List[Tuple[str, float]]
    emotions: List[Tuple[str, float]]
    mood_rating: int
    energy_rating: int
    user_id: str
    entry_text: str

class BaselineInitMessage(Model):
    baseline_data: List[ExtractedDataMessage]
    total_entries: int
    user_id: str

# Define our agent
extractor_agent = Agent(
    name="extractor_agent",
    seed="extractor_seed",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]
)

# Our global models
kw_model = None
emotion_classifier = None
baseline_processed = False

@extractor_agent.on_event("startup")
async def initialize_models(ctx: Context):
    global kw_model, emotion_classifier, baseline_processed
    ctx.logger.info("Initializing KeyBERT and emotion classification models...")
    
    # Init keyword model
    kw_model = KeyBERT()
    
    # Init sentiment analysis model
    emotion_classifier = pipeline(
        "text-classification", 
        model="j-hartmann/emotion-english-distilroberta-base"
    )
    
    ctx.logger.info("Models initialized successfully!")
    
    # Process baseline data after model initialization
    ctx.logger.info("Starting baseline data processing...")
    await process_baseline_data(ctx)

async def process_baseline_data(ctx: Context):
    global baseline_processed
    
    ctx.logger.info(f"Processing {len(daily_data)} baseline entries...")
    baseline_extractions = []
    
    # Process all baseline entries first
    for i, (entry_text, mood_rating, energy_rating) in enumerate(daily_data):
        ctx.logger.info(f"Processing baseline entry {i+1}/{len(daily_data)}")
        
        try:
            # Extract keywords and emotions
            keywords = get_daily_keywords(entry_text)
            emotions = get_top_emotions(entry_text)
            
            # Create extracted data message
            extracted_data = ExtractedDataMessage(
                keywords=keywords,
                emotions=emotions,
                mood_rating=mood_rating,
                energy_rating=energy_rating,
                user_id="baseline_user",
                entry_text=entry_text
            )
            
            baseline_extractions.append(extracted_data)
            
            # Small delay to prevent overloading
            await asyncio.sleep(0.05)
            
        except Exception as e:
            ctx.logger.error(f"Error processing baseline entry {i+1}: {str(e)}")
    
    ctx.logger.info(f"Completed processing all {len(baseline_extractions)} baseline entries")
    
    # Now send all baseline data at once to pattern finder
    baseline_message = BaselineInitMessage(
        baseline_data=baseline_extractions,
        total_entries=len(baseline_extractions),
        user_id="baseline_user"
    )
    
    try:
        # Wait a moment to ensure pattern finder is ready
        await asyncio.sleep(2)
        
        await ctx.send("agent1qggee7fyd8fjtm379ggavw3h0uckmgglwnj35e8gte5a4ev4kry3ss788jf", baseline_message)
        ctx.logger.info(f"SENT ALL {len(baseline_extractions)} BASELINE ENTRIES TO PATTERN FINDER")
        baseline_processed = True
    except Exception as e:
        ctx.logger.error(f"Error sending baseline data: {str(e)}")

def get_daily_keywords(doc, seed_keywords_list=None):
    if seed_keywords_list is None:
        seed_keywords_list = seed_keywords
    return kw_model.extract_keywords(doc, keyphrase_ngram_range=(1,1), stop_words='english',
                                use_maxsum=True, nr_candidates=20, top_n=10, seed_keywords=seed_keywords_list)

def get_top_emotions(text, top_n=1):
    results = emotion_classifier(text, top_k=None)
    top_emotions = sorted(results, key=lambda x: x['score'], reverse=True)[:top_n]
    return [(emotion['label'], emotion['score']) for emotion in top_emotions]

@extractor_agent.on_message(model=DailyEntryMessage)
async def handle_daily_entry(ctx: Context, sender: str, msg: DailyEntryMessage):
    ctx.logger.info(f"Processing NEW daily entry from {sender}")
    
    if kw_model is None or emotion_classifier is None:
        ctx.logger.error("Models not initialized yet!")
        return
        
    if not baseline_processed:
        ctx.logger.warning("Baseline not processed yet, but processing new entry anyway...")
    
    try:
        # Extract keywords and emotions
        keywords = get_daily_keywords(msg.entry_text)
        emotions = get_top_emotions(msg.entry_text)
        
        ctx.logger.info(f"Extracted {len(keywords)} keywords and {len(emotions)} emotions for new entry")
        
        # Create response message
        extracted_data = ExtractedDataMessage(
            keywords=keywords,
            emotions=emotions,
            mood_rating=msg.mood_rating,
            energy_rating=msg.energy_rating,
            user_id=msg.user_id,
            entry_text=msg.entry_text
        )
        
        # Send to pattern finder agent
        await ctx.send("agent1qggee7fyd8fjtm379ggavw3h0uckmgglwnj35e8gte5a4ev4kry3ss788jf", extracted_data)
        ctx.logger.info("Sent NEW entry extracted data to pattern finder")
        
    except Exception as e:
        ctx.logger.error(f"Error processing daily entry: {str(e)}")

if __name__ == "__main__":
    extractor_agent.run()