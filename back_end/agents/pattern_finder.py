from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict
import re

class SemanticPatternFinder:
    def __init__(self, similarity_threshold=0.85):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.activity_groups = {}
        self.group_effects = {}
        self.activity_to_group = {}
        self.similarity_threshold = similarity_threshold
        self.next_group_id = 0
        
        #note these kept appearing even though not very relevant so I am filtering the,
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
        
        #FILTER unneeded stuff
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
        """Map activity to canonical form using synonyms"""
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
        
        for group_id, group_data in self.activity_groups.items():
            similarity = cosine_similarity([activity_embedding], [group_data['embedding']])[0][0]
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_group = group_id
        
        if best_group is not None:
            self.activity_groups[best_group]['activities'].add(activity)
            self.activity_groups[best_group]['activities'].add(canonical_activity)
            
            self.activity_to_group[activity] = best_group
            self.activity_to_group[canonical_activity] = best_group
            return best_group
        else:
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
    
    def map_new_activity(self, activity):
        if not self._is_valid_activity(activity):
            return None
            
        canonical_activity = self._get_canonical_activity(activity)
        
        if canonical_activity in self.activity_to_group:
            group_id = self.activity_to_group[canonical_activity]
            return {
                'group_label': self.activity_groups[group_id]['label'],
                'confidence': self.group_effects[group_id]['confidence'],
                'predicted_mood_effect': self.group_effects[group_id]['mood_outcomes'],
                'predicted_energy_effect': self.group_effects[group_id]['energy_outcomes']
            }
        else:
            activity_embedding = self.model.encode([canonical_activity])[0]
            best_match = None
            best_similarity = 0
            
            for group_id, group_data in self.activity_groups.items():
                similarity = cosine_similarity([activity_embedding], [group_data['embedding']])[0][0]
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = group_id
            
            if best_match and best_similarity > 0.3:
                return {
                    'group_label': self.activity_groups[best_match]['label'],
                    'confidence': self.group_effects[best_match]['confidence'] * best_similarity,
                    'predicted_mood_effect': self.group_effects[best_match]['mood_outcomes'],
                    'predicted_energy_effect': self.group_effects[best_match]['energy_outcomes'],
                    'similarity': best_similarity
                }
            
            return None