import pandas as pd
import numpy as np
from typing import Dict, Any
import spacy
import logging
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from app.utils.status import update_processing_status

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TextProcessor:
    """Class to handle text processing transformations."""
    
    def __init__(self):
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.stemmer = nltk.PorterStemmer()
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        return nltk.word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from list of tokens."""
        return [token for token in tokens if token.lower() not in self.stopwords]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens."""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def stem(self, tokens: List[str]) -> List[str]:
        """Stem tokens."""
        return [self.stemmer.stem(token) for token in tokens]
    
    def get_named_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text."""
        doc = nlp(text)
        return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
    
    def pos_tag(self, tokens: List[str]) -> List[Dict[str, str]]:
        """Get part-of-speech tags for tokens."""
        return [{'token': token, 'pos': tag} 
                for token, tag in nltk.pos_tag(tokens)]
    
    def vectorize_text(self, texts: List[str], method: str = 'tfidf') -> pd.DataFrame:
        """Vectorize text using either TF-IDF or Count vectorization."""
        if method == 'tfidf':
            vectorizer = TfidfVectorizer()
        else:  # method == 'count'
            vectorizer = CountVectorizer()
        
        vectors = vectorizer.fit_transform(texts)
        return pd.DataFrame(
            vectors.toarray(),
            columns=vectorizer.get_feature_names_out()
        )

def process_file(input_path: str, output_path: str, config: Dict[str, Any]) -> None:
    """Process a file with the specified transformations.
    
    Args:
        input_path: Path to input file
        output_path: Path to save processed file
        config: Processing configuration
    """
    try:
        # Extract file_id from input path
        file_id = input_path.split('/')[-1].split('_')[0]
        logger.debug(f"Processing file {file_id} with config: {config}")
        
        # Load data
        logger.debug(f"Loading data from {input_path}")
        update_processing_status(file_id, "processing", "Loading data", 10)
        df = pd.read_csv(input_path)
        logger.debug(f"Loaded DataFrame with shape: {df.shape}")
        
        # Process each transformation
        transformations = config.get("transformations", [])
        total_transforms = len(transformations)
        logger.debug(f"Found {total_transforms} transformations to apply")
        
        for i, transform in enumerate(transformations, 1):
            progress = 10 + (i / total_transforms) * 80  # Reserve 10% for loading, 10% for saving
            
            transform_type = transform["type"]
            params = transform["params"]
            columns = params["columns"]
            
            logger.debug(f"Applying transformation {i}/{total_transforms}: {transform_type}")
            logger.debug(f"Parameters: {params}")
            
            update_processing_status(
                file_id,
                "processing",
                f"Applying {transform_type}",
                progress
            )
            
            if transform_type == "tokenization":
                logger.debug(f"Tokenizing columns: {columns}")
                processor = TextProcessor()
                for col in columns:
                    df[f"{col}_tokens"] = df[col].apply(processor.tokenize)
            
            elif transform_type == "stopword_removal":
                logger.debug(f"Removing stopwords from columns: {columns}")
                processor = TextProcessor()
                for col in columns:
                    df[f"{col}_no_stop"] = df[col].apply(lambda x: " ".join(processor.remove_stopwords(processor.tokenize(x))))
            
            elif transform_type == "lemmatization":
                logger.debug(f"Lemmatizing columns: {columns}")
                processor = TextProcessor()
                for col in columns:
                    df[f"{col}_lemma"] = df[col].apply(lambda x: " ".join(processor.lemmatize(processor.tokenize(x))))
            
            elif transform_type == "text_vectorization":
                logger.debug(f"Vectorizing columns: {columns}")
                method = params.get("method", "tfidf")
                max_features = params.get("max_features", 1000)
                ngram_range = tuple(params.get("ngram_range", (1, 1)))
                
                for col in columns:
                    vectorizer = (
                        TfidfVectorizer(max_features=max_features, ngram_range=ngram_range)
                        if method == "tfidf"
                        else CountVectorizer(max_features=max_features, ngram_range=ngram_range)
                    )
                    
                    features = vectorizer.fit_transform(df[col])
                    feature_names = vectorizer.get_feature_names_out()
                    
                    for i, name in enumerate(feature_names):
                        df[f"{col}_{method}_{name}"] = features[:, i].toarray()
            
            elif transform_type == "named_entity_recognition":
                logger.debug(f"Extracting entities from columns: {columns}")
                nlp = spacy.load("en_core_web_sm")
                entity_types = set(params.get("entity_types", ["PERSON", "ORG", "GPE"]))
                
                for col in columns:
                    df[f"{col}_entities"] = df[col].apply(
                        lambda x: [(ent.text, ent.label_) for ent in nlp(x).ents if ent.label_ in entity_types]
                    )
            
            elif transform_type == "pos_tagging":
                logger.debug(f"POS tagging columns: {columns}")
                nlp = spacy.load("en_core_web_sm")
                for col in columns:
                    df[f"{col}_pos"] = df[col].apply(
                        lambda x: [(token.text, token.pos_) for token in nlp(x)]
                    )
            
            elif transform_type == "stemming":
                logger.debug(f"Stemming columns: {columns}")
                from nltk.stem import PorterStemmer
                stemmer = PorterStemmer()
                for col in columns:
                    df[f"{col}_stem"] = df[col].apply(
                        lambda x: " ".join([stemmer.stem(word) for word in x.split()])
                    )
            
            logger.debug(f"Completed transformation {transform_type}")
        
        # Save processed data
        logger.debug(f"Saving processed data to {output_path}")
        update_processing_status(file_id, "processing", "Saving processed data", 90)
        df.to_csv(output_path, index=False)
        
        # Mark as complete
        logger.debug("Processing complete")
        update_processing_status(file_id, "completed", "Processing complete", 100)
        
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {str(e)}")
        # Update status with error
        update_processing_status(file_id, "error", str(e))
        raise e
