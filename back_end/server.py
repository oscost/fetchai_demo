from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# REST Gateway endpoints - NEW ARCHITECTURE
GATEWAY_ENDPOINTS = {
    'daily_entry': 'http://127.0.0.1:8006/daily_entry',
    'feedback': 'http://127.0.0.1:8006/feedback',
    'status': 'http://127.0.0.1:8006/status',
    'test': 'http://127.0.0.1:8006/test'
}

# ALL 30 BASELINE ENTRIES (from extractor.py)
BASELINE_ENTRIES = [
    {
        "date": "2024-04-01",
        "entry_text": "Woke up early and went for a 5-mile run before work. Felt energized all day. Had a productive morning at the office working on my presentation. Lunch with colleagues was fun - lots of laughing. Afternoon meetings went smoothly. Cooked a healthy dinner with vegetables and chicken. Read a book before bed feeling accomplished.",
        "mood_rating": 8,
        "energy_rating": 8
    },
    {
        "date": "2024-04-02",
        "entry_text": "Woke up and immediately spent 2 hours scrolling Instagram and TikTok in bed. Felt unmotivated to get up. Work was boring - just answered emails and did busy work. Spent lunch break browsing social media instead of eating properly. Afternoon dragged on forever. Ordered pizza for dinner and continued scrolling feeds until 2am.",
        "mood_rating": 3,
        "energy_rating": 3
    },
    {
        "date": "2024-04-03",
        "entry_text": "Had brunch with my best friend Sarah - we laughed so much my cheeks hurt. Spent the afternoon shopping and catching up on life. Evening dinner party with college friends, played games and shared stories. Felt so grateful for these relationships. Went to bed happy and content.",
        "mood_rating": 9,
        "energy_rating": 6
    },
    {
        "date": "2024-04-04",
        "entry_text": "Stayed up until 3am binge-watching Netflix series. Woke up groggy and exhausted. Could barely focus at work - made several mistakes. Skipped lunch because I felt too tired to eat. Afternoon was a struggle to stay awake. Grabbed fast food on the way home and crashed on the couch.",
        "mood_rating": 3,
        "energy_rating": 2
    },
    {
        "date": "2024-04-05",
        "entry_text": "Spent the morning at the farmers market buying fresh ingredients. Came home and meal prepped for the entire week - made quinoa salads, roasted vegetables, and marinated chicken. Felt so organized and healthy. Cooked a elaborate dinner trying a new recipe. Kitchen smelled amazing.",
        "mood_rating": 7,
        "energy_rating": 6
    },
    {
        "date": "2024-04-06",
        "entry_text": "Started with yoga class at 7am which felt wonderful. Work was stressful with tight deadlines but I handled it well. Hit the gym after work for strength training. Cooked a simple but healthy dinner. Feeling strong and accomplished despite work stress.",
        "mood_rating": 8,
        "energy_rating": 8
    },
    {
        "date": "2024-04-07",
        "entry_text": "Lazy Sunday morning scrolling through social media for hours. Saw everyone's perfect vacation photos and felt inadequate. Spent most of the day on my phone checking various apps. Ordered takeout instead of cooking. Evening was just more screen time until very late.",
        "mood_rating": 4,
        "energy_rating": 4
    },
    {
        "date": "2024-04-08",
        "entry_text": "Video call with family for my nephew's birthday - he's so cute! Afternoon hanging out with roommates playing board games. Evening went to a friend's house warming party, met some new interesting people. Lots of good conversations and connections made.",
        "mood_rating": 8,
        "energy_rating": 6
    },
    {
        "date": "2024-04-09",
        "entry_text": "Another late night gaming session until 4am. Overslept and was late for work. Boss wasn't happy about missing the morning meeting. Felt foggy and irritable all day. Made poor food choices - just snacks and coffee. Couldn't concentrate on anything.",
        "mood_rating": 2,
        "energy_rating": 2
    },
    {
        "date": "2024-04-10",
        "entry_text": "Woke up inspired to try new recipes. Spent the morning making homemade bread and soup from scratch. The process was so meditative and rewarding. Shared the meal with neighbors who loved it. Evening planning next week's menu and organizing kitchen.",
        "mood_rating": 7,
        "energy_rating": 6
    },
    {
        "date": "2024-04-11",
        "entry_text": "Joined a new fitness class - dance cardio was so fun! Made some new acquaintances in class. Work felt easier after that endorphin boost. Packed a healthy lunch I prepared yesterday. Evening walk with podcasts, feeling grateful for my body.",
        "mood_rating": 8,
        "energy_rating": 9
    },
    {
        "date": "2024-04-12",
        "entry_text": "Normal work day with meetings and project work. Lunch at desk while scrolling news and social feeds. Afternoon was productive. Quick grocery run after work. Simple dinner at home. Checked social media before bed and felt a bit envious of others' posts.",
        "mood_rating": 5,
        "energy_rating": 5
    },
    {
        "date": "2024-04-13",
        "entry_text": "Surprise visit from old college friend who was in town! Spent the whole day reminiscing and exploring the city together. Went to our old favorite restaurant and laughed until we cried. Felt so connected and nostalgic in the best way.",
        "mood_rating": 9,
        "energy_rating": 7
    },
    {
        "date": "2024-04-14",
        "entry_text": "Up late scrolling TikTok and Instagram, lost track of time until 2:30am. Woke up exhausted and late. Rushed through morning routine. Work was terrible - couldn't focus and felt behind all day. Lunch was more phone scrolling. Vicious cycle continued into evening.",
        "mood_rating": 3,
        "energy_rating": 1
    },
    {
        "date": "2024-04-15",
        "entry_text": "Saturday dedicated to cooking! Made fresh pasta from scratch, prepared sauces, and baked cookies. Kitchen was my happy place today. Invited friends over to share the feast. Everyone complimented the food and I felt so proud of my skills.",
        "mood_rating": 8,
        "energy_rating": 7
    },
    {
        "date": "2024-04-16",
        "entry_text": "Morning hike in the mountains with spectacular views. Fresh air and physical challenge felt amazing. Work seemed trivial after experiencing nature's beauty. Packed a nutritious lunch feeling energized. Evening gentle stretching and gratitude practice.",
        "mood_rating": 9,
        "energy_rating": 9
    },
    {
        "date": "2024-04-17",
        "entry_text": "Standard Tuesday routine - work, emails, meetings. Lunch at the office cafeteria. Afternoon project work was engaging. Commute home listening to music. Cooked a simple stir-fry dinner. Watched one episode of a show before reasonable bedtime.",
        "mood_rating": 6,
        "energy_rating": 4
    },
    {
        "date": "2024-04-18",
        "entry_text": "Woke up late and started day checking all social media platforms. Felt overwhelmed by everyone's achievements and travel posts. Work was unfocused - kept getting distracted by phone notifications. Lunch was fast food while browsing feeds. Unproductive afternoon.",
        "mood_rating": 4,
        "energy_rating": 6
    },
    {
        "date": "2024-04-19",
        "entry_text": "Family dinner at my parents' house with siblings and their kids. Chaos but so much love and laughter. Played with nieces and nephews in the backyard. Felt grateful for family bonds. Drive home reflecting on how lucky I am.",
        "mood_rating": 8,
        "energy_rating": 6
    },
    {
        "date": "2024-04-20",
        "entry_text": "Binged an entire season of a show until 5am. Called in sick to work because I literally couldn't function. Spent the day in bed feeling guilty and exhausted. Ordered junk food delivery. Another wasted day due to poor sleep choices.",
        "mood_rating": 2,
        "energy_rating": 1
    },
    {
        "date": "2024-04-21",
        "entry_text": "Hosted dinner party for six friends - spent all day preparing multiple courses. Everyone brought wine and we had such a wonderful evening. Food turned out perfectly and friends were impressed. Felt like a successful adult who can actually cook!",
        "mood_rating": 8,
        "energy_rating": 7
    },
    {
        "date": "2024-04-22",
        "entry_text": "New personal record at the gym today! Felt incredibly strong during weightlifting session. Work productivity was through the roof afterward. Healthy lunch felt like fuel rather than just food. Evening was calm and satisfied, early bedtime.",
        "mood_rating": 9,
        "energy_rating": 9
    },
    {
        "date": "2024-04-23",
        "entry_text": "Spent way too much time comparing myself to influencers on Instagram. Work was distracted by constant phone checking. Lunch scrolling made me feel worse about my life choices. Evening was more mindless scrolling instead of doing anything productive.",
        "mood_rating": 3,
        "energy_rating": 3
    },
    {
        "date": "2024-04-24",
        "entry_text": "Girls' night out with friends - dinner, drinks, and dancing! Laughed until my stomach hurt and danced until my feet were sore. Felt so alive and connected to my friend group. Uber ride home was full of happy chattering about the night.",
        "mood_rating": 9,
        "energy_rating": 7
    },
    {
        "date": "2024-04-25",
        "entry_text": "Another 3am bedtime due to anxiety scrolling news and social media. Woke up anxious and tired. Work was overwhelming - everything felt impossible. Skipped gym because too exhausted. Fast food dinner while staring at screens. Cycle repeating.",
        "mood_rating": 3,
        "energy_rating": 2
    },
    {
        "date": "2024-04-26",
        "entry_text": "Sunday meal prep session turned into creative cooking experiment. Tried three new recipes and they all worked! Portioned everything for the week ahead. Kitchen dance party while cooking. Feeling prepared and nourished for the week.",
        "mood_rating": 7,
        "energy_rating": 6
    },
    {
        "date": "2024-04-27",
        "entry_text": "Beach volleyball game with friends combined exercise and social time perfectly. Sun, sand, competition, and laughter. Post-game seafood dinner by the ocean. Drive home with windows down feeling grateful for active lifestyle and good friends.",
        "mood_rating": 9,
        "energy_rating": 8
    },
    {
        "date": "2024-04-28",
        "entry_text": "Productive work morning followed by lunch meeting that went well. Afternoon grocery shopping and errands. Evening cooking while video chatting with long-distance friend. Moderate day with good moments and necessary tasks completed.",
        "mood_rating": 6,
        "energy_rating": 6
    },
    {
        "date": "2024-04-29",
        "entry_text": "Rabbit hole of social media started early and continued all day. Felt increasingly inadequate seeing everyone's highlight reels. Work suffered from constant distraction. Lunch was rushed while scrolling. Evening was more of the same mindless consumption.",
        "mood_rating": 4,
        "energy_rating": 3
    },
    {
        "date": "2024-04-30",
        "entry_text": "Perfect day combining everything I love! Morning workout class with friends, farmers market shopping, afternoon cooking with roommate, evening dinner party we hosted. Felt energized, social, creative, and accomplished. This is how life should feel!",
        "mood_rating": 10,
        "energy_rating": 9
    }
]

# DYNAMIC DATA CLASS (updated by agents)
class DynamicData:
    def __init__(self):
        self.current_patterns = []
        self.current_recommendations = {}
        self.agent_insights = []
        self.last_pattern_update = None
        self.last_recommendation_update = None
        self.system_status = {
            "agents_active": 4,
            "last_analysis": None,
            "baseline_complete": True
        }
    
    def update_patterns(self, patterns):
        self.current_patterns = patterns
        self.last_pattern_update = datetime.now()
        self.system_status["last_analysis"] = datetime.now()
        print(f"UPDATED PATTERNS: {len(patterns)} patterns from AI agents")
        
    def update_recommendations(self, pattern_id, recommendation):
        self.current_recommendations[pattern_id] = recommendation
        self.last_recommendation_update = datetime.now()
        print(f"UPDATED RECOMMENDATION for {pattern_id}")
        
    def add_insight(self, insight):
        self.agent_insights.append({
            **insight,
            'timestamp': datetime.now().isoformat()
        })
        # Keep only last 10 insights
        if len(self.agent_insights) > 10:
            self.agent_insights = self.agent_insights[-10:]

# Global dynamic data
dynamic_data = DynamicData()

# FALLBACK PATTERNS (used if agents haven't sent data yet)
FALLBACK_PATTERNS = [
    {
        "id": "exercise",
        "name": "Exercise",
        "confidence": 1.00,
        "mood_effect": 9.0,
        "energy_effect": 6.0,
        "mood_change_from_avg": 4.9,
        "energy_change_from_avg": 2.0,
        "status": "Strongly helping",
        "description": "Physical activity including gym, running, yoga, dance, hiking, and sports",
        "activities": ["run", "gym", "workout", "yoga", "exercise", "fitness", "hike", "dance", "volleyball", "weightlifting", "cardio"]
    },
    {
        "id": "social_media",
        "name": "Social Media",
        "confidence": 0.89,
        "mood_effect": 3.0,
        "energy_effect": 3.0,
        "mood_change_from_avg": -1.1,
        "energy_change_from_avg": -1.0,
        "status": "Mildly hurting",
        "description": "Scrolling social platforms, checking feeds, comparing to others",
        "activities": ["scrolling", "instagram", "tiktok", "social media", "browsing", "feeds", "checking phone", "news"]
    },
    {
        "id": "cooking",
        "name": "Cooking",
        "confidence": 0.79,
        "mood_effect": 7.0,
        "energy_effect": 6.0,
        "mood_change_from_avg": 2.9,
        "energy_change_from_avg": 2.0,
        "status": "Helping",
        "description": "Meal preparation, trying new recipes, kitchen activities, meal prep",
        "activities": ["cook", "cooking", "meal prep", "recipe", "kitchen", "baking", "farmers market", "preparing food"]
    },
    {
        "id": "lunch",
        "name": "Lunch",
        "confidence": 0.49,
        "mood_effect": 8.0,
        "energy_effect": 8.0,
        "mood_change_from_avg": 3.9,
        "energy_change_from_avg": 4.0,
        "status": "Potentially helping",
        "description": "Midday meals and lunch activities, social lunch meetings",
        "activities": ["lunch", "midday meal", "lunch break", "lunch meeting", "eating with colleagues"]
    },
    {
        "id": "social",
        "name": "Social Activities",
        "confidence": 0.40,
        "mood_effect": 8.0,
        "energy_effect": 8.0,
        "mood_change_from_avg": 3.9,
        "energy_change_from_avg": 4.0,
        "status": "Potentially helping",
        "description": "Time with friends, family, social gatherings, parties, conversations",
        "activities": ["friends", "family", "social", "party", "gathering", "call", "dinner party", "video call", "hanging out"]
    }
]

# FALLBACK RECOMMENDATIONS
FALLBACK_RECOMMENDATIONS = {
    "exercise": {
        "title": "Maximize Your Exercise Benefits",
        "analysis": "Exercise is your most reliable mood booster with perfect consistency (1.00 confidence) and exceptional mood elevation (9.0/10). It's been exceptionally effective in elevating your mood (+4.9 above average) and moderately improving energy (+2.0 above average). Your perfect confidence score indicates it always delivers positive results for you.",
        "strategies": [
            "Schedule consistency: Block dedicated workout slots (e.g., morning routines) to ensure no misses",
            "Variety for sustainability: Rotate between cardio, strength, and flexibility training to prevent burnout",
            "Micro-boosts: Add short walks or stretching breaks during slumps for quick mood lifts",
            "Treat workouts as non-negotiable appointments—defend this time fiercely against interruptions",
            "Try morning workouts before 10 AM when you have peak energy for maximum benefit",
            "Combine social and exercise: volleyball, dance classes, hiking with friends amplify the positive effects",
            "Use exercise as a reset button: when feeling low energy or mood, prioritize movement first"
        ]
    },
    "social_media": {
        "title": "Address Social Media Drain",
        "analysis": "Highly consistent drain on mood (-1.1 below average) and energy (-1.0 below average), with 89% confidence. This is a habitual trap likely leading to comparison fatigue, passive scrolling without fulfillment, and disrupted sleep patterns. The high confidence means this negative effect is very reliable and predictable.",
        "strategies": [
            "Strict limits: Use app timers or block distracting apps during key hours (especially mornings and bedtime)",
            "Alternative delivery: Switch to curated newsletters (e.g., niche interests) to reduce doomscrolling",
            "Replacement habit: When you feel the urge to scroll, do a 5-minute workout or cooking prep instead",
            "Audit feeds: Unfollow accounts that trigger negativity or comparison—curate for inspiration only",
            "Time boundaries: No social media after 9 PM or before completing morning routine",
            "Physical barriers: Charge phone outside bedroom, use app blockers during work hours",
            "Conscious consumption: When you do use social media, set specific intentions (connect with friends, not browse)"
        ]
    },
    "cooking": {
        "title": "Amplify Cooking Benefits",
        "analysis": "Cooking reliably enhances mood (+2.9 above average) and energy (+2.0 above average), with high confidence (0.79). Likely due to creativity, sensory engagement, accomplishment feeling, and nutritional benefits. This pattern includes meal prep, trying new recipes, and kitchen creativity.",
        "strategies": [
            "Theme nights: Experiment with new cuisines or techniques to keep it engaging (Italian Monday, Asian Tuesday)",
            "Batch prep: Cook larger portions to extend positive effects (leftovers provide convenience + satisfaction)",
            "Social cooking: Invite others to participate—dinner parties and collaborative cooking amplify mood benefits",
            "Keep kitchen stocked with favorite ingredients to reduce friction on low-motivation days",
            "Try advanced techniques: bread making, fermentation, or elaborate dishes for deeper engagement",
            "Farmers market visits: Make ingredient shopping part of the positive ritual",
            "Document successes: Take photos of meals, keep a recipe journal to build confidence"
        ]
    },
    "social": {
        "title": "Optimize Social Connections",
        "analysis": "Social activities provide massive boosts (+3.9 mood, +4.0 energy above average) but with low confidence (0.40), indicating high variability. When social interactions work, they're incredibly powerful for your wellbeing. The inconsistency suggests some social contexts work better than others.",
        "strategies": [
            "Quality over quantity: Focus on deep connections rather than large groups or surface interactions",
            "Activity-based socializing: Combine with other positive patterns like cooking (dinner parties) or exercise",
            "Schedule regular touchpoints: Weekly video calls with family, monthly friend gatherings",
            "Energy matching: Plan social activities when you have good energy, not when depleted",
            "Intimate settings: Small gatherings, one-on-one time, and familiar environments work best",
            "Be intentional: Choose social activities that align with your values and interests",
            "Recovery time: Plan downtime after big social events to recharge"
        ]
    },
    "lunch": {
        "title": "Stabilize Lunch Benefits",
        "analysis": "Lunch shows strong positive effects (+3.9 mood, +4.0 energy above average) but with low confidence (0.49), suggesting high variability. Sometimes it's amazing, sometimes not. This inconsistency likely depends on context: rushed vs. mindful eating, social vs. solo, quality of food.",
        "strategies": [
            "Ritualize it: Eat away from screens, focus on flavors and textures to enhance mood impact",
            "Social component: Lunch with colleagues or friends consistently shows higher satisfaction",
            "Protein-forward meals: Ensure sustained energy with balanced nutrition, avoid just carbs",
            "Prep quality options: Use your cooking skills to prepare satisfying lunches in advance",
            "Time protection: Block calendar during lunch, don't rush or multitask while eating",
            "Environment matters: Find pleasant spaces to eat, not just at your desk",
            "Track patterns: Notice which types of lunches give you the biggest boost"
        ]
    }
}

# Global user entries
user_entries = []

def send_to_gateway(endpoint_url, message_data, timeout=10):
    """Send message to REST Gateway"""
    try:
        headers = {'Content-Type': 'application/json'}
        print(f"Sending to REST Gateway: {endpoint_url}")
        print(f"Data: {message_data}")
        
        response = requests.post(
            endpoint_url, 
            json=message_data, 
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        
        print(f"Successfully sent to gateway! Status: {response.status_code}")
        return {"success": True, "response": response.json() if response.content else {}}
        
    except requests.exceptions.Timeout:
        print(f"Timeout connecting to gateway: {endpoint_url}")
        return {"success": False, "error": "Gateway request timed out"}
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to gateway: {endpoint_url}")
        return {"success": False, "error": "Could not connect to gateway - is it running?"}
    except requests.exceptions.RequestException as e:
        print(f"Gateway request failed: {str(e)}")
        return {"success": False, "error": f"Gateway request failed: {str(e)}"}
    except Exception as e:
        print(f"Unexpected gateway error: {str(e)}")
        return {"success": False, "error": f"Unexpected gateway error: {str(e)}"}

def get_status_from_pattern(pattern):
    """Convert pattern data to status string"""
    mood_change = pattern.get('mood_change_from_avg', 0)
    confidence = pattern.get('confidence', 0)
    
    if confidence < 0.3:
        return "Uncertain"
    elif mood_change > 2:
        return "Strongly helping"
    elif mood_change > 0:
        return "Helping" 
    elif mood_change < -2:
        return "Strongly hurting"
    elif mood_change < 0:
        return "Mildly hurting"
    else:
        return "Neutral"

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    # Use dynamic data if available, fallback to static
    patterns = dynamic_data.current_patterns or FALLBACK_PATTERNS
    
    total_patterns = len(patterns)
    high_confidence_patterns = len([p for p in patterns if p.get('confidence', 0) > 0.7])
    total_entries = len(BASELINE_ENTRIES) + len(user_entries)
    
    # Calculate energy trend from last week of entries
    recent_entries = (BASELINE_ENTRIES[-7:] + user_entries[-7:])[-7:]
    if len(recent_entries) >= 2:
        recent_avg = sum(e['energy_rating'] for e in recent_entries[-3:]) / min(3, len(recent_entries))
        older_avg = sum(e['energy_rating'] for e in recent_entries[:3]) / min(3, len(recent_entries))
        energy_trend = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
    else:
        energy_trend = 0
    
    # Get recent insights from dynamic data
    recent_insights = dynamic_data.agent_insights[-3:] if dynamic_data.agent_insights else [
        {
            "type": "pattern",
            "agent": "Pattern Agent",
            "text": "Exercise shows perfect reliability (1.00 confidence) with +4.9 mood boost",
            "confidence": 1.00
        },
        {
            "type": "insight", 
            "agent": "Insight Agent",
            "text": "Social media consistently drains energy (-1.0) - consider strict time limits"
        },
        {
            "type": "recommendation",
            "agent": "Planner Agent", 
            "text": "Cooking provides reliable mood boost (+2.9) - batch prep on weekends"
        }
    ]
    
    return jsonify({
        "energy_trend": f"+{energy_trend:.0f}%" if energy_trend > 0 else f"{energy_trend:.0f}%",
        "active_agents": dynamic_data.system_status["agents_active"],
        "patterns_found": total_patterns,
        "streak_days": total_entries,
        "recent_insights": recent_insights,
        "todays_recommendations": [
            {
                "text": "Try a morning workout before 10 AM",
                "reason": "Based on your perfect exercise pattern (1.00 confidence)",
                "priority": "high"
            },
            {
                "text": "Limit social media to 15 minutes today",
                "reason": "Consistent -1.1 mood drain detected", 
                "priority": "high"
            },
            {
                "text": "Cook or meal prep this evening",
                "reason": "Reliable +2.9 mood boost from cooking activities",
                "priority": "medium"
            }
        ],
        "last_update": dynamic_data.last_pattern_update.isoformat() if dynamic_data.last_pattern_update else None,
        "data_source": "ai_agents" if dynamic_data.current_patterns else "fallback"
    })

@app.route('/api/patterns', methods=['GET'])
def get_patterns():
    """Get discovered patterns from AI agents"""
    patterns = dynamic_data.current_patterns or FALLBACK_PATTERNS
    
    return jsonify({
        "patterns": patterns,
        "total_patterns": len(patterns),
        "high_confidence_patterns": len([p for p in patterns if p.get('confidence', 0) > 0.7]),
        "last_update": dynamic_data.last_pattern_update.isoformat() if dynamic_data.last_pattern_update else None,
        "source": "ai_agents" if dynamic_data.current_patterns else "fallback"
    })

@app.route('/api/patterns/<pattern_id>/recommendations', methods=['GET'])
def get_pattern_recommendations(pattern_id):
    """Get recommendations for a specific pattern"""
    # Check dynamic recommendations first
    if pattern_id in dynamic_data.current_recommendations:
        recommendation = dynamic_data.current_recommendations[pattern_id]
        recommendation["source"] = "ai_agents"
        recommendation["last_update"] = dynamic_data.last_recommendation_update.isoformat()
        return jsonify(recommendation)
    
    # Fallback to static recommendations
    if pattern_id in FALLBACK_RECOMMENDATIONS:
        recommendation = FALLBACK_RECOMMENDATIONS[pattern_id].copy()
        recommendation["source"] = "fallback"
        recommendation["last_update"] = None
        return jsonify(recommendation)
    else:
        return jsonify({"error": "Pattern not found"}), 404

@app.route('/api/history', methods=['GET'])
def get_history():
    # Combine baseline and user entries
    all_entries = []
    
    # Add baseline entries
    for entry in BASELINE_ENTRIES:
        all_entries.append({
            **entry,
            "type": "baseline"
        })
    
    # Add user entries
    for entry in user_entries:
        all_entries.append({
            **entry,
            "type": "user"
        })
    
    # Sort by date for nicer display
    all_entries.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({
        "entries": all_entries,
        "total_entries": len(all_entries),
        "baseline_entries": len(BASELINE_ENTRIES),
        "user_entries": len(user_entries)
    })

@app.route('/api/daily_entry', methods=['POST'])
def submit_daily_entry():
    """Submit a new daily entry via REST Gateway"""
    data = request.json
    
    # Validate input
    if not all(key in data for key in ['entry_text', 'mood_rating', 'energy_rating']):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Create entry
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "entry_text": data['entry_text'],
        "mood_rating": int(data['mood_rating']),
        "energy_rating": int(data['energy_rating'])
    }
    
    # Store locally
    user_entries.append(entry)
    
    # Send to REST Gateway
    def send_to_gateway_async():
        try:
            gateway_message = {
                "entry_text": entry['entry_text'],
                "mood_rating": entry['mood_rating'],
                "energy_rating": entry['energy_rating'],
                "user_id": "web_user"
            }
            
            print(f"SENDING TO REST GATEWAY: {gateway_message}")
            
            # Send to gateway instead of direct agent
            result = send_to_gateway(GATEWAY_ENDPOINTS['daily_entry'], gateway_message)
            
            if result["success"]:
                print("Successfully sent entry via REST Gateway!")
                print("Pipeline triggered: Gateway → Extractor → Pattern Finder → Curator → Planner")
                
                # Add insight about entry processing
                dynamic_data.add_insight({
                    "type": "entry",
                    "agent": "System",
                    "text": f"Processing new daily entry (mood: {entry['mood_rating']}, energy: {entry['energy_rating']})"
                })
            else:
                print(f"Gateway error: {result['error']}")
                
        except Exception as e:
            print(f"Error sending to gateway: {e}")
    
    # Send in background thread
    threading.Thread(target=send_to_gateway_async).start()
    
    return jsonify({
        "success": True,
        "entry": entry,
        "message": "Entry submitted via REST Gateway - AI pipeline triggered!"
})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback via REST Gateway"""
    data = request.json

    if not all(key in data for key in ['pattern_id', 'feedback_type']):
        return jsonify({"error": "Missing required fields"}), 400

    # Map frontend feedback to backend expectations
    feedback_mapping = {
        "love_it": "GREAT idea",
        "not_sure": "unsure about idea", 
        "dislike": "BAD idea"
    }

    feedback_type = feedback_mapping.get(data['feedback_type'])
    if not feedback_type:
        return jsonify({"error": "Invalid feedback type"}), 400

    # Send to REST Gateway
    def send_feedback_to_gateway():
        try:
            feedback_message = {
                "pattern_id": data['pattern_id'],
                "feedback_type": feedback_type,
                "user_comment": data.get('comment', ''),
                "user_id": "web_user"
            }
            
            print(f"SENDING FEEDBACK TO REST GATEWAY: {feedback_message}")
            
            # Send to gateway instead of direct agent
            result = send_to_gateway(GATEWAY_ENDPOINTS['feedback'], feedback_message)
            
            if result["success"]:
                print("Successfully sent feedback via REST Gateway!")
                print("Curator will adjust confidence and update planner")
                
                # Add insight about feedback
                dynamic_data.add_insight({
                    "type": "feedback",
                    "agent": "User",
                    "text": f"Provided {data['feedback_type']} feedback for {data['pattern_id']} pattern"
                })
            else:
                print(f"Gateway error: {result['error']}")
                
        except Exception as e:
            print(f"Error sending feedback to gateway: {e}")

    threading.Thread(target=send_feedback_to_gateway).start()

    return jsonify({
        "success": True,
        "message": f"Feedback '{feedback_type}' sent via REST Gateway for pattern '{data['pattern_id']}'"
    })

@app.route('/api/agents', methods=['GET']) 
def get_agents():
    """Get agent status"""
    return jsonify({
        "agents": [
            {
                "id": "rest_gateway",
                "name": "REST Gateway",
                "status": "active",
                "description": "Converts REST API calls to uAgent messages",
                "last_active": "now",
                "address": "http://127.0.0.1:8006"
            },
            {
                "id": "extractor",
                "name": "Extractor Agent", 
                "status": "active",
                "description": "Extracts keywords and emotions from daily entries using KeyBERT and emotion classification",
                "last_active": "2 minutes ago",
                "address": "agent1qwcrrpsgl49tqn50gmsyesq48g3v7mchzmhr6074tn94fw8dqzepxxds4vm"
            },
            {
                "id": "pattern_finder",
                "name": "Pattern Finder Agent",
                "status": "analyzing", 
                "description": "Discovers behavioral patterns using semantic similarity and confidence scoring",
                "last_active": "1 minute ago",
                "address": "agent1qggee7fyd8fjtm379ggavw3h0uckmgglwnj35e8gte5a4ev4kry3ss788jf"
            },
            {
                "id": "curator",
                "name": "Curator Agent",
                "status": "learning",
                "description": "Evaluates pattern significance and processes user feedback to adjust recommendations", 
                "last_active": "30 seconds ago",
                "address": "agent1qdr8zekrarc5hhyhxju7suyr8nfxe6j8q9kgxa9007v8wmdvraw9z0uw37v"
            },
            {
                "id": "planner",
                "name": "Planner Agent",
                "status": "specialized",
                "description": "Generates personalized wellness recommendations using AS1 AI analysis",
                "last_active": "5 minutes ago",
                "address": "agent1qwvypts2ft35u3w4uhg8da0cj5edkmp0k7slvjqtekas26t4evxj7xk7a4g"
            }
        ]
    })

@app.route('/api/agent_status', methods=['GET'])
def check_system_status():
    # Test gateway connectivity
    try:
        result = send_to_gateway(GATEWAY_ENDPOINTS['status'], {}, timeout=3)
        gateway_online = result["success"]
        gateway_response = result.get("response", {})
    except:
        gateway_online = False
        gateway_response = {}

    return jsonify({
        "gateway_online": gateway_online,
        "gateway_status": gateway_response,
        "gateway_endpoints": GATEWAY_ENDPOINTS,
        "message": "Using REST Gateway architecture",
        "architecture": "Flask → REST Gateway → uAgent Network",
        "dynamic_data_status": {
            "patterns_loaded": len(dynamic_data.current_patterns) > 0,
            "recommendations_loaded": len(dynamic_data.current_recommendations) > 0,
            "last_pattern_update": dynamic_data.last_pattern_update.isoformat() if dynamic_data.last_pattern_update else None,
            "insights_count": len(dynamic_data.agent_insights)
        }
    })

@app.route('/api/test_agents', methods=['POST'])
def test_gateway_communication():
    """Test REST Gateway communication"""
    results = {}

    print("TESTING REST GATEWAY COMMUNICATION...")

    # Test gateway status
    print("Testing gateway status...")
    result = send_to_gateway(GATEWAY_ENDPOINTS['status'], {}, timeout=5)
    results['gateway_status'] = result

    # Test gateway test endpoint
    test_data = {
        "test_message": "Hello from Flask server!",
        "timestamp": datetime.now().isoformat()
    }

    print("Testing gateway test endpoint...")
    result = send_to_gateway(GATEWAY_ENDPOINTS['test'], test_data, timeout=5)
    results['gateway_test'] = result

    # Test daily entry via gateway
    test_entry = {
        "entry_text": "Test entry from Flask - great workout and cooking session!",
        "mood_rating": 8,
        "energy_rating": 7,
        "user_id": "test_user"
    }

    print("Testing daily entry via gateway...")
    result = send_to_gateway(GATEWAY_ENDPOINTS['daily_entry'], test_entry, timeout=5)
    results['daily_entry'] = result

    # Test feedback via gateway
    test_feedback = {
        "pattern_id": "exercise",
        "feedback_type": "GREAT idea",
        "user_comment": "Test feedback from Flask - exercise works great!",
        "user_id": "test_user"
    }

    print("Testing feedback via gateway...")
    result = send_to_gateway(GATEWAY_ENDPOINTS['feedback'], test_feedback, timeout=5)
    results['feedback'] = result

    print("Gateway communication test completed!")

    return jsonify({
        "test_results": results,
        "message": "REST Gateway communication test completed - check console for details",
        "gateway_endpoints": GATEWAY_ENDPOINTS
    })

@app.route('/api/baseline_stats', methods=['GET'])
def get_baseline_stats():
    """Get statistics about the baseline data"""
    mood_avg = sum(entry['mood_rating'] for entry in BASELINE_ENTRIES) / len(BASELINE_ENTRIES)
    energy_avg = sum(entry['energy_rating'] for entry in BASELINE_ENTRIES) / len(BASELINE_ENTRIES)

    mood_range = {
        'min': min(entry['mood_rating'] for entry in BASELINE_ENTRIES),
        'max': max(entry['mood_rating'] for entry in BASELINE_ENTRIES)
    }

    energy_range = {
        'min': min(entry['energy_rating'] for entry in BASELINE_ENTRIES),
        'max': max(entry['energy_rating'] for entry in BASELINE_ENTRIES)
    }

    return jsonify({
        "total_baseline_entries": len(BASELINE_ENTRIES),
        "date_range": {
            "start": BASELINE_ENTRIES[0]['date'],
            "end": BASELINE_ENTRIES[-1]['date']
        },
        "mood_stats": {
            "average": mood_avg,
            "range": mood_range
        },
        "energy_stats": {
            "average": energy_avg,
            "range": energy_range
        },
        "patterns_discovered": len(dynamic_data.current_patterns) if dynamic_data.current_patterns else len(FALLBACK_PATTERNS)
    })

# NEW ENDPOINTS FOR AGENT UPDATES
@app.route('/api/agent_update/patterns', methods=['POST'])
def receive_pattern_update():
    """Receive pattern updates from AI agents"""
    try:
        data = request.json
        patterns = data.get('patterns', [])
        
        print(f"RECEIVED PATTERN UPDATE: {len(patterns)} patterns from AI agents")
        
        # Convert agent pattern format to frontend format
        converted_patterns = []
        for i, pattern in enumerate(patterns):
            pattern_id = pattern.get('group_label', f'pattern_{i}')
            converted_pattern = {
                "id": pattern_id,
                "name": pattern.get('group_label', f'Pattern {i+1}').title(),
                "confidence": pattern.get('confidence', 0.0),
                "mood_effect": pattern.get('effect_on_mood', 5.0),
                "energy_effect": pattern.get('effect_on_energy', 5.0),
                "mood_change_from_avg": pattern.get('mood_change_from_avg', 0.0),
                "energy_change_from_avg": pattern.get('energy_change_from_avg', 0.0),
                "status": get_status_from_pattern(pattern),
                "description": f"Activities related to {pattern.get('group_label', 'unknown')}",
                "activities": pattern.get('activities', [pattern.get('group_label', 'unknown')])
            }
            converted_patterns.append(converted_pattern)
        
        # Update dynamic data
        dynamic_data.update_patterns(converted_patterns)
        
        # Add insight about the update
        dynamic_data.add_insight({
            "type": "pattern",
            "agent": "Pattern Agent", 
            "text": f"Updated {len(patterns)} patterns with latest confidence scores",
            "confidence": sum(p.get('confidence', 0) for p in patterns) / len(patterns) if patterns else 0
        })
        
        print(f"PATTERNS UPDATED: Now showing {len(converted_patterns)} live AI patterns")
        
        return jsonify({
            "success": True, 
            "patterns_updated": len(patterns),
            "message": "Patterns updated successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error receiving pattern update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agent_update/recommendations', methods=['POST']) 
def receive_recommendation_update():
    """Receive recommendation updates from AI agents"""
    try:
        data = request.json
        pattern_id = data.get('pattern_id')
        recommendation = data.get('recommendation')
        
        print(f"RECEIVED RECOMMENDATION UPDATE for pattern: {pattern_id}")
        
        if pattern_id and recommendation:
            # Ensure recommendation has all required fields
            formatted_recommendation = {
                "title": recommendation.get('title', f"AI Insights for {pattern_id}"),
                "analysis": recommendation.get('analysis', 'AI analysis in progress...'),
                "strategies": recommendation.get('strategies', ['Generating personalized strategies...']),
                "last_update": datetime.now().isoformat(),
                "source": "ai_agents"
            }
            
            dynamic_data.update_recommendations(pattern_id, formatted_recommendation)
            
            # Add insight about the recommendation update
            dynamic_data.add_insight({
                "type": "recommendation",
                "agent": "Planner Agent",
                "text": f"Generated new AI recommendations for {pattern_id} pattern"
            })
            
            print(f"RECOMMENDATION UPDATED for {pattern_id}")
            
            return jsonify({
                "success": True,
                "message": f"Recommendation updated for {pattern_id}",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Missing pattern_id or recommendation"}), 400
            
    except Exception as e:
        print(f"Error receiving recommendation update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agent_update/insights', methods=['POST'])
def receive_insight_update():
    """Receive insight updates from AI agents"""
    try:
        data = request.json
        insight = data.get('insight', {})
        
        if insight:
            dynamic_data.add_insight(insight)
            print(f"RECEIVED INSIGHT: {insight.get('text', 'New insight added')}")
            
            return jsonify({
                "success": True,
                "message": "Insight added successfully",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Missing insight data"}), 400
            
    except Exception as e:
        print(f"Error receiving insight update: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Development/Debug endpoints
@app.route('/api/debug/dynamic_data', methods=['GET'])
def get_debug_dynamic_data():
    """Debug endpoint to see current dynamic data state"""
    return jsonify({
        "patterns_count": len(dynamic_data.current_patterns),
        "recommendations_count": len(dynamic_data.current_recommendations),
        "insights_count": len(dynamic_data.agent_insights),
        "last_pattern_update": dynamic_data.last_pattern_update.isoformat() if dynamic_data.last_pattern_update else None,
        "last_recommendation_update": dynamic_data.last_recommendation_update.isoformat() if dynamic_data.last_recommendation_update else None,
        "current_patterns": dynamic_data.current_patterns,
        "current_recommendations": list(dynamic_data.current_recommendations.keys()),
        "recent_insights": dynamic_data.agent_insights[-5:] if dynamic_data.agent_insights else []
    })

@app.route('/api/debug/reset_dynamic_data', methods=['POST'])
def reset_dynamic_data():
    """Debug endpoint to reset dynamic data (useful for testing)"""
    global dynamic_data
    dynamic_data = DynamicData()
    print("RESET: Dynamic data cleared - back to fallback mode")
    return jsonify({
        "success": True,
        "message": "Dynamic data reset - using fallback patterns and recommendations"
    })

if __name__ == '__main__':
    print("Starting WellnessAI Flask Server...")
    print("=" * 80)
    print("ADVANCED DYNAMIC UPDATES ENABLED")
    print("Real-time pattern updates from AI agents")
    print("Live recommendation generation") 
    print("Dynamic insight tracking")
    print("Fallback support for offline agents")
    print("-" * 80)
    print("Gateway Architecture:")
    print("   Flask ↔ REST Gateway ↔ uAgent Network")
    print("-" * 80)
    print("Available Endpoints:")
    print("      User Endpoints:")
    print("      GET  /api/dashboard")
    print("      GET  /api/patterns") 
    print("      GET  /api/patterns/<id>/recommendations")
    print("      POST /api/daily_entry")
    print("      POST /api/feedback")
    print("      Agent Update Endpoints:")
    print("      POST /api/agent_update/patterns")
    print("      POST /api/agent_update/recommendations")
    print("      POST /api/agent_update/insights")
    print("      System Endpoints:")
    print("      GET  /api/agent_status")
    print("      POST /api/test_agents")
    print("      GET  /api/debug/dynamic_data")
    print("-" * 80)
    print("  STARTUP SEQUENCE:")
    print("   1. Start agents: extractor → pattern_finder → curator → planner")
    print("   2. Start REST gateway: python rest_gateway.py")
    print("   3. Start Flask server: python server.py")
    print("   4. Frontend will show live AI data once agents send updates!")
    print("=" * 80)
    print("  Flask server starting on http://localhost:5000")

    app.run(debug=False, port=5000)