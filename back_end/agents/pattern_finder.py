from uagents import Agent, Context, Model
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict
import re
from typing import List, Tuple, Dict, Any
import pickle
import os
import asyncio

#structure that we are going to use to comminicate between uAgents
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

class PatternAnalysisMessage(Model):
    patterns: List[Dict[str, Any]]
    user_id: str
    total_patterns: int
    high_confidence_patterns: int
    is_baseline: bool = False

# Initialize pattern finder agent
pattern_finder_agent = Agent(
    name="pattern_finder_agent",
    seed="pattern_finder_seed",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"]
)

# Global pattern finder instance
pattern_finder = None
PATTERN_CACHE_FILE = "pattern_finder_cache.pkl"
baseline_initialized = False

class SemanticPatternFinder:
    def __init__(self, similarity_threshold=0.85):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.activity_groups = {}
        self.group_effects = {}
        self.activity_to_group = {}
        self.similarity_threshold = similarity_threshold
        self.next_group_id = 0
        
        # Time patterns to filter out
        self.time_patterns = [
            r'\d+(?:am|pm|AM|PM)',  
            r'\d+:\d+',             
            r'(?:morning|afternoon|evening|night|today|tomorrow|yesterday|day|week|weekend)',
            r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)',
            r'\b(?:early|late|immediately|soon|later|before|after|until|since|while|during)\b',
        ]
        
        self.activity_synonyms = {
            'exercise': ['gym', 'workout', 'run', 'running', 'walk', 'walking', 'hike', 'hiking', 'yoga', 'fitness', 'dance', 'dancing', 'sports', 'volleyball', 'weightlifting', 'cardio', 'training', 'bike', 'biking', 'swimming'],
            'social_media': ['scrolling', 'instagram', 'tiktok', 'facebook', 'feeds', 'social', 'browsing', 'checking', 'phone', 'apps', 'posting', 'liking'],
            'cooking': ['cook', 'cooking', 'meal', 'prep', 'recipe', 'recipes', 'baking', 'kitchen', 'ingredients', 'preparing', 'prepared'],
            'social': ['friends', 'family', 'party', 'dinner', 'brunch', 'hanging', 'video', 'call', 'chat', 'meeting', 'conversation', 'gatherings', 'socializing'],
            'sleep': ['sleep', 'sleeping', 'bed', 'bedtime', 'nap', 'rest', 'tired', 'exhausted', 'late']
        }
    
    def _calculate_overall_averages(self):
        all_moods = []
        all_energies = []
        
        for effect_data in self.group_effects.values():
            if effect_data['mood_outcomes']:
                all_moods.extend(effect_data['mood_outcomes'].values())
            if effect_data['energy_outcomes']:
                all_energies.extend(effect_data['energy_outcomes'].values())
        
        if all_moods and all_energies:
            return np.median(all_moods), np.median(all_energies)
        return 5.0, 5.0
    
    def _is_valid_activity(self, activity):
        activity_lower = activity.lower().strip()
        
        # Filter unneeded stuff
        for pattern in self.time_patterns:
            if re.search(pattern, activity_lower):
                return False
        
        if len(activity_lower) <= 3:
            return False
            
        feeling_words = {'stressed', 'tired', 'happy', 'sad', 'anxious', 'excited', 'bored', 'grateful', 'accomplished', 'energized', 'motivated', 'overwhelmed', 'satisfied', 'content', 'frustrated', 'felt', 'feeling', 'spent', 'had', 'was', 'were', 'been', 'have', 'has'}
        if activity_lower in feeling_words:
            return False
            
        non_activities = {'time', 'life', 'people', 'things', 'way', 'nothing', 'everything', 'something', 'perfect', 'amazing', 'wonderful', 'terrible', 'good', 'bad'}
        if activity_lower in non_activities:
            return False
            
        return True
    
    def _get_canonical_activity(self, activity):
        activity_lower = activity.lower().strip()
        
        for canonical, synonyms in self.activity_synonyms.items():
            if activity_lower in synonyms or any(synonym in activity_lower for synonym in synonyms):
                return canonical
                
        return activity_lower
    
    def _find_or_create_group(self, activity):
        if not self._is_valid_activity(activity):
            return None
            
        canonical_activity = self._get_canonical_activity(activity)
        
        if canonical_activity in self.activity_to_group:
            group_id = self.activity_to_group[canonical_activity]
            self.activity_groups[group_id]['activities'].add(activity)
            self.activity_to_group[activity] = group_id
            return group_id
            
        activity_embedding = self.model.encode([canonical_activity])[0]
        
        best_group = None
        best_similarity = 0
        
        for group_id, group_data in self.activity_groups.items(): #find the group that best matches current item
            similarity = cosine_similarity([activity_embedding], [group_data['embedding']])[0][0]
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_group = group_id
        
        if best_group is not None: #if we have something at our threshold
            self.activity_groups[best_group]['activities'].add(activity)
            self.activity_groups[best_group]['activities'].add(canonical_activity)
            
            self.activity_to_group[activity] = best_group
            self.activity_to_group[canonical_activity] = best_group
            return best_group
        else: #means we didnt find a group that matches us
            group_id = self.next_group_id
            self.next_group_id += 1
            
            self.activity_groups[group_id] = {
                'activities': {activity, canonical_activity},
                'embedding': activity_embedding,
                'label': canonical_activity
            }
            
            self.group_effects[group_id] = {
                'mood_outcomes': defaultdict(float),
                'energy_outcomes': defaultdict(float),
                'confidence': 0.0,
                'observation_count': 0
            }
            
            self.activity_to_group[activity] = group_id
            self.activity_to_group[canonical_activity] = group_id
            return group_id
    
    def add_observation(self, daily_keywords, daily_emotion, mood_rating=None, energy_rating=None):
        for activity, weight in daily_keywords:
            group_id = self._find_or_create_group(activity)
            
            if group_id is not None and mood_rating is not None and energy_rating is not None:
                effect_data = self.group_effects[group_id]
                
                old_count = effect_data['observation_count']
                new_count = old_count + weight
                
                # Update mood outcomes
                current_mood_avg = effect_data['mood_outcomes'].get(daily_emotion[0], 0.0)
                new_mood_avg = ((current_mood_avg * old_count) + (mood_rating * weight)) / new_count
                effect_data['mood_outcomes'][daily_emotion[0]] = new_mood_avg
                
                # Update energy outcomes
                current_energy_avg = effect_data['energy_outcomes'].get(daily_emotion[0], 0.0)
                new_energy_avg = ((current_energy_avg * old_count) + (energy_rating * weight)) / new_count
                effect_data['energy_outcomes'][daily_emotion[0]] = new_energy_avg
                
                effect_data['confidence'] = min(1.0, new_count / 5.0)  
                effect_data['observation_count'] = new_count
    
    def batch_add_observations(self, extracted_data_list):
        #used for testing to give an example user with 30 days of logs
        for extracted_data in extracted_data_list:
            self.add_observation(
                extracted_data.keywords,
                extracted_data.emotions,
                extracted_data.mood_rating,
                extracted_data.energy_rating
            )
    
    def get_patterns(self, min_confidence=0.2):
        patterns = []
        overall_avg_mood, overall_avg_energy = self._calculate_overall_averages()
        
        for group_id, group_data in self.activity_groups.items():
            effect_data = self.group_effects[group_id]
            
            if effect_data['confidence'] >= min_confidence and effect_data['observation_count'] >= 1.5:
                if effect_data['mood_outcomes'] and effect_data['energy_outcomes']:
                    dominant_mood = max(effect_data['mood_outcomes'].items(), key=lambda x: abs(x[1]))
                    dominant_energy = max(effect_data['energy_outcomes'].items(), key=lambda x: abs(x[1]))
                    
                    patterns.append({
                        'group_label': group_data['label'],
                        'activities': list(group_data['activities']),
                        'effect_on_mood': dominant_mood[1],
                        'effect_on_energy': dominant_energy[1],
                        'mood_change_from_avg': dominant_mood[1] - overall_avg_mood,
                        'energy_change_from_avg': dominant_energy[1] - overall_avg_energy,
                        'primary_emotion': dominant_mood[0],
                        'confidence': effect_data['confidence'],
                        'observation_count': effect_data['observation_count']
                    })
        
        return sorted(patterns, key=lambda x: x['confidence'], reverse=True)
    
    def save_state(self, filename):
        #used to cahce
        state = {
            'activity_groups': self.activity_groups,
            'group_effects': self.group_effects,
            'activity_to_group': self.activity_to_group,
            'next_group_id': self.next_group_id
        }
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
    
    def load_state(self, filename):
        #load out cahce
        try:
            with open(filename, 'rb') as f:
                state = pickle.load(f)
            self.activity_groups = state['activity_groups']
            self.group_effects = state['group_effects']
            self.activity_to_group = state['activity_to_group']
            self.next_group_id = state['next_group_id']
            return True
        except FileNotFoundError:
            return False

@pattern_finder_agent.on_event("startup")
async def initialize_pattern_finder(ctx: Context):
    global pattern_finder
    ctx.logger.info("🔧 Initializing Pattern Finder...")
    
    pattern_finder = SemanticPatternFinder(similarity_threshold=0.85)
    ctx.logger.info("Pattern Finder initialized, waiting for baseline data...")

@pattern_finder_agent.on_message(model=BaselineInitMessage)
async def handle_baseline_init(ctx: Context, sender: str, msg: BaselineInitMessage):
    global baseline_initialized
    ctx.logger.info(f"RECEIVED BASELINE: {msg.total_entries} entries from {sender}")
    
    if pattern_finder is None:
        ctx.logger.error("Pattern finder not initialized yet!")
        return
    
    try:
        ctx.logger.info(f"Processing {len(msg.baseline_data)} baseline entries in batch...")
        
        pattern_finder.batch_add_observations(msg.baseline_data)
        ctx.logger.info(f"Completed batch processing of {len(msg.baseline_data)} baseline entries")
        
        pattern_finder.save_state(PATTERN_CACHE_FILE)
        baseline_initialized = True
        
        #find patterns in our exiting test user
        patterns = pattern_finder.get_patterns(min_confidence=0.1)
        
        ctx.logger.info(f"BASELINE COMPLETE! Generated {len(patterns)} patterns")
        
        # Create baseline analysis message
        analysis_msg = PatternAnalysisMessage(
            patterns=patterns,
            user_id=msg.user_id,
            total_patterns=len(patterns),
            high_confidence_patterns=len([p for p in patterns if p['confidence'] > 0.7]),
            is_baseline=True
        )
        
        # Small delay then send to planner
        await asyncio.sleep(1)
        await ctx.send("agent1qwvypts2ft35u3w4uhg8da0cj5edkmp0k7slvjqtekas26t4evxj7xk7a4g", analysis_msg)
        ctx.logger.info("SENT BASELINE ANALYSIS TO PLANNER")
        
    except Exception as e:
        ctx.logger.error(f"Error processing baseline data: {str(e)}")

@pattern_finder_agent.on_message(model=ExtractedDataMessage) #processing dynamic messages
async def handle_extracted_data(ctx: Context, sender: str, msg: ExtractedDataMessage):
    ctx.logger.info(f"Processing NEW daily entry from {sender}")
    
    if pattern_finder is None:
        ctx.logger.error("Pattern finder not initialized yet!")
        return
        
    if not baseline_initialized:
        ctx.logger.warning("Baseline not initialized yet, processing new entry anyway...")
    
    try:
        # Add single observation to pattern finder
        pattern_finder.add_observation(
            msg.keywords,
            msg.emotions,
            msg.mood_rating,
            msg.energy_rating
        )
        
        pattern_finder.save_state(PATTERN_CACHE_FILE)
        
        # Get current patterns
        patterns = pattern_finder.get_patterns(min_confidence=0.2)
        ctx.logger.info(f"Found {len(patterns)} patterns with confidence >= 0.2")
        
        # Create response message
        analysis_msg = PatternAnalysisMessage(
            patterns=patterns,
            user_id=msg.user_id,
            total_patterns=len(patterns),
            high_confidence_patterns=len([p for p in patterns if p['confidence'] > 0.7]),
            is_baseline=False
        )
        
        # Send to planner agent
        await ctx.send("agent1qwvypts2ft35u3w4uhg8da0cj5edkmp0k7slvjqtekas26t4evxj7xk7a4g", analysis_msg)
        ctx.logger.info("Sent pattern analysis to planner")
        
    except Exception as e:
        ctx.logger.error(f"Error processing extracted data: {str(e)}")

if __name__ == "__main__":
    pattern_finder_agent.run()