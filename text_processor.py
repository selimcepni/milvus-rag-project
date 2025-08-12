import re
import nltk
from sentence_transformers import SentenceTransformer
from config import Config

# NLTK data download
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextProcessor:
    def __init__(self):
        self.model = SentenceTransformer(Config.MODEL_NAME)
        
    def split_turkish_sentences(self, text):
        """Türkçe metni cümlelere ayır"""
        # Temel temizlik
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Türkçe için sentence splitting
        sentences = nltk.sent_tokenize(text, language='turkish')
        
        processed_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Çok kısa cümleleri atla
            if len(sentence.split()) < 3:
                continue
                
            # Çok uzun cümleleri böl
            if len(sentence) > 500:
                sub_sentences = re.split(r'[.!?]\s+', sentence)
                for sub in sub_sentences:
                    if len(sub.strip().split()) >= 3:
                        processed_sentences.append(sub.strip())
            else:
                processed_sentences.append(sentence)
        
        return processed_sentences
    
    def create_embeddings(self, sentences):
        """Cümleler için embedding oluştur"""
        return self.model.encode(sentences).tolist()
    
    def create_single_embedding(self, sentence):
        """Tek cümle için embedding"""
        return self.model.encode(sentence).tolist()