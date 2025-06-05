import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import logging
logging.getLogger("transformers").setLevel(logging.WARNING)

from keybert import KeyBERT
from transformers import pipeline

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
#init keyword model
kw_model = KeyBERT()

#initing sentiment analysis model
emotion_classifier = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base"
)

def get_daily_keywords(doc, seed_keywords_list=None):
    if seed_keywords_list is None:
        seed_keywords_list = seed_keywords
    return kw_model.extract_keywords(doc, keyphrase_ngram_range=(1,1), stop_words='english',
                                use_maxsum=True, nr_candidates=20, top_n=10, seed_keywords=seed_keywords_list)

def get_top_emotions(text, top_n=1):
    results = emotion_classifier(text, top_k=None)
    top_emotions = sorted(results, key=lambda x: x['score'], reverse=True)[:top_n]
    return [(emotion['label'], emotion['score']) for emotion in top_emotions]