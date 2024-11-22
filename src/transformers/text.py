from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import spacy
from src.core.pipeline import BaseTransformer

# Download required NLTK data
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

class TokenizationTransformer(BaseTransformer):
    """Transformer for tokenizing text data."""
    
    def __init__(self, columns: List[str]):
        """
        Initialize the transformer.
        
        Args:
            columns: List of column names to tokenize
        """
        super().__init__()
        self.columns = columns
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Tokenize text in specified columns.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with tokenized text
        """
        result = data.copy()
        
        for col in self.columns:
            result[f"{col}_tokens"] = result[col].apply(
                lambda x: word_tokenize(str(x)) if pd.notna(x) else []
            )
        
        return result

class StopwordRemovalTransformer(BaseTransformer):
    """Transformer for removing stopwords from text data."""
    
    def __init__(self, columns: List[str], language: str = 'english'):
        """
        Initialize the transformer.
        
        Args:
            columns: List of column names to process
            language: Language for stopwords (default: 'english')
        """
        super().__init__()
        self.columns = columns
        self.stop_words = set(stopwords.words(language))
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Remove stopwords from tokenized text.
        
        Args:
            data: Input DataFrame with tokenized text columns
            
        Returns:
            DataFrame with stopwords removed
        """
        result = data.copy()
        
        for col in self.columns:
            token_col = f"{col}_tokens"
            if token_col not in result.columns:
                raise ValueError(f"Column {token_col} not found. Please tokenize text first.")
            
            result[f"{col}_filtered"] = result[token_col].apply(
                lambda tokens: [word for word in tokens if word.lower() not in self.stop_words]
            )
        
        return result

class LemmatizationTransformer(BaseTransformer):
    """Transformer for lemmatizing text data."""
    
    def __init__(self, columns: List[str]):
        """
        Initialize the transformer.
        
        Args:
            columns: List of column names to lemmatize
        """
        super().__init__()
        self.columns = columns
        self.lemmatizer = WordNetLemmatizer()
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Lemmatize tokenized text.
        
        Args:
            data: Input DataFrame with filtered text columns
            
        Returns:
            DataFrame with lemmatized text
        """
        result = data.copy()
        
        for col in self.columns:
            filtered_col = f"{col}_filtered"
            if filtered_col not in result.columns:
                raise ValueError(f"Column {filtered_col} not found. Please remove stopwords first.")
            
            result[f"{col}_lemmatized"] = result[filtered_col].apply(
                lambda tokens: [self.lemmatizer.lemmatize(word) for word in tokens]
            )
        
        return result

class TextVectorizationTransformer(BaseTransformer):
    """Transformer for converting text to numerical features."""
    
    def __init__(
        self,
        columns: List[str],
        method: str = 'tfidf',
        max_features: Optional[int] = None,
        ngram_range: tuple = (1, 1)
    ):
        """
        Initialize the transformer.
        
        Args:
            columns: List of column names to vectorize
            method: Vectorization method ('tfidf' or 'count')
            max_features: Maximum number of features to create
            ngram_range: Range of n-grams to consider
        """
        super().__init__()
        self.columns = columns
        self.method = method
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizers = {}
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert text to numerical features.
        
        Args:
            data: Input DataFrame with processed text columns
            
        Returns:
            DataFrame with vectorized text features
        """
        result = data.copy()
        
        for col in self.columns:
            lemmatized_col = f"{col}_lemmatized"
            if lemmatized_col not in result.columns:
                raise ValueError(f"Column {lemmatized_col} not found. Please lemmatize text first.")
            
            # Join tokens back into text
            text_data = result[lemmatized_col].apply(' '.join)
            
            # Create and fit vectorizer
            if self.method == 'tfidf':
                vectorizer = TfidfVectorizer(
                    max_features=self.max_features,
                    ngram_range=self.ngram_range
                )
            else:  # count vectorization
                vectorizer = CountVectorizer(
                    max_features=self.max_features,
                    ngram_range=self.ngram_range
                )
            
            # Transform text to features
            features = vectorizer.fit_transform(text_data)
            feature_names = vectorizer.get_feature_names_out()
            
            # Convert to DataFrame
            vectorized_df = pd.DataFrame(
                features.toarray(),
                columns=[f"{col}_feature_{name}" for name in feature_names]
            )
            
            # Add features to result
            result = pd.concat([result, vectorized_df], axis=1)
            
            # Store vectorizer for future use
            self.vectorizers[col] = vectorizer
        
        return result

class NamedEntityTransformer(BaseTransformer):
    """Transformer for extracting named entities from text."""
    
    def __init__(self, columns: List[str], entity_types: Optional[List[str]] = None):
        """
        Initialize the transformer.
        
        Args:
            columns: List of column names to process
            entity_types: List of entity types to extract (e.g., ['PERSON', 'ORG'])
        """
        super().__init__()
        self.columns = columns
        self.entity_types = entity_types
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract named entities from text.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with extracted entities
        """
        result = data.copy()
        
        for col in self.columns:
            # Process text with spaCy
            docs = list(nlp.pipe(result[col].astype(str)))
            
            # Extract entities
            if self.entity_types:
                entities = [
                    [ent.text for ent in doc.ents if ent.label_ in self.entity_types]
                    for doc in docs
                ]
            else:
                entities = [[ent.text for ent in doc.ents] for doc in docs]
            
            # Add entities to result
            result[f"{col}_entities"] = entities
            
            # Add entity types if requested
            if self.entity_types:
                for entity_type in self.entity_types:
                    result[f"{col}_entities_{entity_type}"] = [
                        [ent.text for ent in doc.ents if ent.label_ == entity_type]
                        for doc in docs
                    ]
        
        return result
