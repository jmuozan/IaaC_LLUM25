import os
import requests
from functools import lru_cache
import re

class AITextSensor:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.moderation_url = "https://api.openai.com/v1/moderations"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Add custom word lists
        self.custom_blacklist = {
            'kill', 'murder', 'dead', 'death', 'die', 'hate',
            'violence', 'violent', 'attack', 'fight', 'hurt',
            'blood', 'bloody', 'weapon', 'gun', 'shoot',
            'fuck', 'shit', 'damn', 'hell',
            'nazi', 'racist', 'hate', 'discrimination',
            'sex', 'porn', 'nude', 'naked'
        }
        
        # Compile regex for custom blacklist
        pattern = r'\b(' + '|'.join(re.escape(word) for word in self.custom_blacklist) + r')\b'
        self.custom_pattern = re.compile(pattern, re.IGNORECASE)

        # Add custom category rules
        self.force_inappropriate_categories = {
            'kill': ['violence'],
            'murder': ['violence'],
            'death': ['violence'],
            'gun': ['violence'],
            'weapon': ['violence'],
            'hate': ['hate'],
            'racist': ['hate'],
            'discrimination': ['hate'],
            'naked': ['sexual'],
            'nude': ['sexual']
        }

    @lru_cache(maxsize=100)  # Cache results to avoid redundant API calls
    def get_content_details(self, text):
        """Get detailed content analysis from OpenAI's moderation API"""
        try:
            response = requests.post(
                self.moderation_url,
                headers=self.headers,
                json={"input": text}
            )
            response.raise_for_status()
            result = response.json()
            
            # Return the categories dictionary
            categories = result.get('results', [{}])[0].get('categories', {})

            # Apply custom rules
            lower_text = text.lower()
            for trigger_word, trigger_categories in self.force_inappropriate_categories.items():
                if trigger_word in lower_text:
                    for category in trigger_categories:
                        categories[category] = True
                        print(f"[INFO] Forced category '{category}' to True due to word '{trigger_word}'")

            return categories

        except Exception as e:
            print(f"[WARNING] Moderation API error: {e}")
            return {}

    def check_content(self, text):
        """Check content using both API and custom blacklist"""
        api_flagged = self._check_api_content(text)
        custom_flagged = bool(self.custom_pattern.search(text))
        return api_flagged or custom_flagged

    @lru_cache(maxsize=100)
    def _check_api_content(self, text):
        """Original API check method"""
        try:
            response = requests.post(
                self.moderation_url,
                headers=self.headers,
                json={"input": text}
            )
            response.raise_for_status()
            result = response.json()
            return any(result.get('results', [{}])[0].get('categories', {}).values())
        except Exception as e:
            print(f"[WARNING] Moderation API error: {e}")
            return False

    def censor_text(self, text):
        """Replace inappropriate content with a rocket emoji"""
        if self.check_content(text):
            # Censor individual words that match the blacklist
            censored = self.custom_pattern.sub('🚀', text)
            # If API also flags it, censor additional words
            if self._check_api_content(text):
                words = censored.split()
                censored = ' '.join(['🚀' if i % 2 == 0 and word != '🚀' 
                                   else word for i, word in enumerate(words)])
            return censored
        return text

    def contains_inappropriate_content(self, text):
        """Check if text contains any inappropriate content"""
        return self.check_content(text)