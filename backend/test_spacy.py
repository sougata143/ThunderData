import spacy

def test_spacy():
    try:
        # Load the English language model
        nlp = spacy.load("en_core_web_sm")
        
        # Test text
        text = "This is a test sentence to verify spaCy installation."
        
        # Process the text
        doc = nlp(text)
        
        # Print tokens and their part-of-speech tags
        print("Tokens and their POS tags:")
        for token in doc:
            print(f"{token.text}: {token.pos_}")
            
        print("\nSpaCy is working correctly!")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_spacy()
