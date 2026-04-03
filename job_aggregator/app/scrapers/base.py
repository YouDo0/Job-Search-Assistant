from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import re

class BaseScraper(ABC):
    def __init__(self, preferences: Dict = None):
        self.preferences = preferences or {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    @abstractmethod
    def search(self, keywords: List[str], location: str = None) -> List[Dict]:
        pass

    def extract_salary(self, text: str) -> tuple:
        patterns = [
            r'([\d.,]+)\s*[-–]\s*([\d.,]+)',
            r'Rp\s*([\d.,]+)\s*[-–]\s*Rp\s*([\d.,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    min_s = float(match.group(1).replace('.', '').replace(',', '.'))
                    max_s = float(match.group(2).replace('.', '').replace(',', '.'))
                    return int(min_s), int(max_s)
                except:
                    pass
        return None, None

    def detect_seniority(self, title: str, description: str = '') -> str:
        text = (title + ' ' + description).lower()
        if any(k in text for k in ['senior', 'sr.', 'sr ', 'lead', 'principal', 'head', 'director', 'manager']):
            return 'senior'
        elif any(k in text for k in ['junior', 'jr.', 'jr ', 'associate', 'intern', 'fresh', 'entry', 'trainee', 'graduate']):
            return 'entry'
        return 'mid'
