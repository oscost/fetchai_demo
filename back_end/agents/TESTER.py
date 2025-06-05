import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import logging
logging.getLogger("transformers").setLevel(logging.WARNING)

from extractor import get_daily_keywords, get_top_emotions, seed_keywords
from pattern_finder import SemanticPatternFinder
import pickle

#note used LLM to generate example entries
daily_data = [
    # Pattern: Exercise + good mood + high energy
    ("""Woke up early and went for a 5-mile run before work. Felt energized all day. Had a productive morning at the office working on my presentation. Lunch with colleagues was fun - lots of laughing. Afternoon meetings went smoothly. Cooked a healthy dinner with vegetables and chicken. Read a book before bed feeling accomplished.""", 8, 8),
    
    # Pattern: Social media scrolling + low mood + low energy
    ("""Woke up and immediately spent 2 hours scrolling Instagram and TikTok in bed. Felt unmotivated to get up. Work was boring - just answered emails and did busy work. Spent lunch break browsing social media instead of eating properly. Afternoon dragged on forever. Ordered pizza for dinner and continued scrolling feeds until 2am.""", 3, 3),
    
    # Pattern: Social activities + high mood + moderate energy
    ("""Had brunch with my best friend Sarah - we laughed so much my cheeks hurt. Spent the afternoon shopping and catching up on life. Evening dinner party with college friends, played games and shared stories. Felt so grateful for these relationships. Went to bed happy and content.""", 9, 6),
    
    # Pattern: Poor sleep + low mood + very low energy
    ("""Stayed up until 3am binge-watching Netflix series. Woke up groggy and exhausted. Could barely focus at work - made several mistakes. Skipped lunch because I felt too tired to eat. Afternoon was a struggle to stay awake. Grabbed fast food on the way home and crashed on the couch.""", 3, 2),
    
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

#creatinf cache file
CACHE_FILE = "extracted_data_cache.pkl"

def extract_all_data(daily_data):
    print("Running extractor on all entries...")
    extracted_data = []
    
    for day_num, (entry, mood_rating, energy_rating) in enumerate(daily_data, 1):
        print(f"Extracting day {day_num}/30...")
        keywords = get_daily_keywords(entry, seed_keywords)
        emotions = get_top_emotions(entry)
        extracted_data.append((keywords, emotions, mood_rating, energy_rating))
    
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(extracted_data, f)
    
    print("Extraction complete and cached!")
    return extracted_data

def load_cached_data():
    try:
        with open(CACHE_FILE, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

print("Checking for cached extraction data...")
extracted_data = load_cached_data()

if extracted_data is None:
    print("No cache found. Running extraction...")
    extracted_data = extract_all_data(daily_data)
else:
    print("Using cached extraction data!")

print("\nInitializing Pattern Finder...")
pattern_finder = SemanticPatternFinder(similarity_threshold=0.85)

print("Processing cached extraction results...")
print("=" * 50)

for day_num, (keywords, emotions, mood_rating, energy_rating) in enumerate(extracted_data, 1):
    print(f"\nDay {day_num}: Processing cached data...")
    
    print(f"Keywords: {keywords[:5]}...")  #Note we only PRINT the first 5 keywords of the 10 for clarity
    print(f"Emotion: {emotions[0]}")
    print(f"Day mood rating: {mood_rating}/10")
    print(f"Day energy rating: {energy_rating}/10")
    
    pattern_finder.add_observation(keywords, emotions, mood_rating, energy_rating)
    
    #only used to display our progress each 10 days to see how to evolves
    if day_num % 10 == 0:
        current_patterns = pattern_finder.get_patterns(min_confidence=0.2)
        print(f"\nPatterns detected after {day_num} days: {len(current_patterns)}")

print("\n" + "=" * 50)
print("FINAL PATTERN ANALYSIS")
print("=" * 50)

#PRINT OUR FINAL RESULTS!
final_patterns = pattern_finder.get_patterns(min_confidence=0.2)

print(f"\nFound {len(final_patterns)} patterns with confidence >= 0.2:")

for i, pattern in enumerate(final_patterns, 1):
    mood_change = pattern['mood_change_from_avg']
    energy_change = pattern['energy_change_from_avg']
    
    mood_sign = "+" if mood_change >= 0 else ""
    energy_sign = "+" if energy_change >= 0 else ""
    
    print(f"\n{i}. Activity Group: '{pattern['group_label']}'")
    print(f"   Similar activities: {pattern['activities']}")
    print(f"   Effect on mood: {pattern['effect_on_mood']:.2f}/10 ({mood_sign}{mood_change:.2f})")
    print(f"   Effect on energy: {pattern['effect_on_energy']:.2f}/10 ({energy_sign}{energy_change:.2f})")
    print(f"   Primary emotion context: {pattern['primary_emotion']}")
    print(f"   Confidence: {pattern['confidence']:.2f}")
    print(f"   Based on {pattern['observation_count']:.1f} weighted observations")

print(f"\nTotal activity groups created: {len(pattern_finder.activity_groups)}")

print("\n" + "=" * 30)
print("Testing pattern recognition:")
test_activities = ["scrolling social media", "weight training", "family dinner", "staying up late", "baking"]
for activity in test_activities:
    mapping = pattern_finder.map_new_activity(activity)
    if mapping:
        print(f"'{activity}' -> '{mapping['group_label']}' (confidence: {mapping['confidence']:.2f})")
        if 'predicted_mood_effect' in mapping and mapping['predicted_mood_effect']:
            mood_effects = list(mapping['predicted_mood_effect'].values())
            energy_effects = list(mapping['predicted_energy_effect'].values()) if 'predicted_energy_effect' in mapping else []
            if mood_effects:
                print(f"   Predicted mood effect: {mood_effects[0]:.1f}/10")
            if energy_effects:
                print(f"   Predicted energy effect: {energy_effects[0]:.1f}/10")
    else:
        print(f"'{activity}' -> No strong pattern match found")

# Note because I keep forgetting to delete cahce if needed.
print(f"\nTo re-run extraction, delete: {CACHE_FILE}")