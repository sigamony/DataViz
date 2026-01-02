"""
User Profile Generator - Creates anonymous user profiles.
Generates fun, memorable usernames and avatars for anonymous users.
"""

import random
from typing import Dict

# Adjectives for username generation
ADJECTIVES = [
    'Clever', 'Curious', 'Brave', 'Swift', 'Wise', 'Bold', 'Bright',
    'Creative', 'Dynamic', 'Eager', 'Friendly', 'Gentle', 'Happy',
    'Jolly', 'Kind', 'Lively', 'Mighty', 'Noble', 'Proud', 'Quick',
    'Radiant', 'Silent', 'Thoughtful', 'Vibrant', 'Witty', 'Zealous',
    'Agile', 'Calm', 'Daring', 'Elegant', 'Fierce', 'Graceful'
]

# Animals for username generation
ANIMALS = [
    'Panda', 'Fox', 'Dolphin', 'Eagle', 'Tiger', 'Wolf', 'Bear',
    'Owl', 'Hawk', 'Lion', 'Leopard', 'Falcon', 'Raven', 'Phoenix',
    'Dragon', 'Penguin', 'Otter', 'Koala', 'Lynx', 'Jaguar',
    'Cheetah', 'Panther', 'Cobra', 'Shark', 'Whale', 'Octopus',
    'Elephant', 'Rhino', 'Gazelle', 'Stallion', 'Falcon', 'Sparrow'
]

# Avatar emojis
AVATAR_EMOJIS = [
    '🐼', '🦊', '🐬', '🦅', '🐯', '🐺', '🐻', '🦉', '🦅', '🦁',
    '🐆', '🦜', '🐧', '🦦', '🐨', '🦌', '🐘', '🦏', '🦒', '🦓',
    '🐙', '🦈', '🐋', '🦑', '🐢', '🦎', '🐍', '🦖', '🦕', '🐉',
    '🦚', '🦩', '🦢', '🦤', '🦭', '🦫', '🦨', '🦡', '🦝', '🐿️'
]

# Gradient colors for avatar backgrounds
AVATAR_GRADIENTS = [
    ['#667eea', '#764ba2'],  # Purple
    ['#f093fb', '#f5576c'],  # Pink
    ['#4facfe', '#00f2fe'],  # Blue
    ['#43e97b', '#38f9d7'],  # Green
    ['#fa709a', '#fee140'],  # Sunset
    ['#30cfd0', '#330867'],  # Ocean
    ['#a8edea', '#fed6e3'],  # Pastel
    ['#ff9a56', '#ff6a88'],  # Coral
    ['#ffecd2', '#fcb69f'],  # Peach
    ['#ff6e7f', '#bfe9ff'],  # Cotton Candy
    ['#e0c3fc', '#8ec5fc'],  # Lavender
    ['#f8b500', '#fceabb'],  # Gold
]


def generate_username() -> str:
    """
    Generate a random anonymous username.
    
    Returns:
        str: Username in format "Adjective Animal"
    """
    adjective = random.choice(ADJECTIVES)
    animal = random.choice(ANIMALS)
    return f"{adjective} {animal}"


def generate_avatar() -> Dict:
    """
    Generate avatar data (emoji and gradient).
    
    Returns:
        Dict with emoji and gradient colors
    """
    emoji = random.choice(AVATAR_EMOJIS)
    gradient = random.choice(AVATAR_GRADIENTS)
    
    return {
        'emoji': emoji,
        'gradient': gradient,
        'type': 'emoji'
    }


def generate_user_profile() -> Dict:
    """
    Generate complete anonymous user profile.
    
    Returns:
        Dict containing username and avatar data
    """
    return {
        'username': generate_username(),
        'avatar': generate_avatar(),
        'is_anonymous': True
    }


def get_avatar_style(avatar: Dict) -> str:
    """
    Generate CSS style string for avatar gradient background.
    
    Args:
        avatar: Avatar dictionary with gradient colors
        
    Returns:
        str: CSS background style
    """
    gradient = avatar.get('gradient', ['#667eea', '#764ba2'])
    return f"linear-gradient(135deg, {gradient[0]} 0%, {gradient[1]} 100%)"
