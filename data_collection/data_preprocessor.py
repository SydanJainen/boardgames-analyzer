import re
import logging
from typing import List, Dict, Any
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class DataPreprocessor:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Download necessary NLTK resources
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            self.logger.warning(f"NLTK resource download failed: {e}")

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize and remove stopwords
        """
        try:
            tokens = word_tokenize(text)
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words]
            return tokens
        except Exception as e:
            self.logger.error(f"Tokenization error: {e}")
            return []

    def preprocess_dataset(self, dataset: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Preprocess entire dataset
        """
        preprocessed_dataset = {}
        
        for game, comments in dataset.items():
            preprocessed_comments = []
            
            for comment in comments:
                preprocessed_comment = comment.copy()
                preprocessed_comment['clean_text'] = self.clean_text(comment['value'])
                preprocessed_comment['tokens'] = self.tokenize(preprocessed_comment['clean_text'])
                
                preprocessed_comments.append(preprocessed_comment)
            
            preprocessed_dataset[game] = preprocessed_comments
        
        return preprocessed_dataset