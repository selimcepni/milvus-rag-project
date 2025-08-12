import re
import nltk
import requests
import json
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

# NLTK data download
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class LocalEmbeddingClient:
    def __init__(self, server_url: str = "http://localhost:5000"):
        """
        Local embedding client for Milvus RAG system
        
        Args:
            server_url: Milvus server API URL
        """
        self.server_url = server_url.rstrip('/')
        self.model = SentenceTransformer('emrecan/bert-base-turkish-cased-mean-nli-stsb-tr')
        print(f"✅ Model loaded: {self.model}")
        
    def split_turkish_sentences(self, text: str) -> List[str]:
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
    
    def create_embeddings(self, sentences: List[str]) -> List[List[float]]:
        """Cümleler için embedding oluştur"""
        print(f"🔄 Creating embeddings for {len(sentences)} sentences...")
        embeddings = self.model.encode(sentences).tolist()
        print(f"✅ Embeddings created: {len(embeddings)} x {len(embeddings[0])}")
        return embeddings
    
    def create_single_embedding(self, sentence: str) -> List[float]:
        """Tek cümle için embedding"""
        return self.model.encode(sentence).tolist()
    
    def insert_episode(self, project_name: str, season: int, episode_number: int, 
                      timecode: str, content: str) -> Dict[str, Any]:
        """
        Dizi bölümünü işleyip sunucuya gönder
        
        Args:
            project_name: Dizi adı
            season: Sezon numarası
            episode_number: Bölüm numarası
            timecode: Zaman kodu (örn: "00:15:30")
            content: Bölüm metni
        """
        print(f"📝 Processing episode: {project_name} - S{season}E{episode_number} @ {timecode}")
        
        # Cümlelere ayır
        sentences = self.split_turkish_sentences(content)
        if not sentences:
            return {"error": "No valid sentences found"}
        
        print(f"📄 Found {len(sentences)} sentences")
        
        # Embeddings oluştur
        embeddings = self.create_embeddings(sentences)
        
        # Sunucuya gönder
        payload = {
            "sentences": sentences,
            "embeddings": embeddings,
            "project_name": project_name,
            "season": season,
            "episode_number": episode_number,
            "timecode": timecode
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/insert_sentences",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message', 'Success')}")
                return result
            else:
                error_msg = f"Server error: {response.status_code}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def search_sentences(self, query_sentences: List[str], 
                        filters: Dict[str, Any] = None, 
                        top_k: int = 1) -> Dict[str, Any]:
        """
        Benzer cümleleri ara
        
        Args:
            query_sentences: Arama cümleleri
            filters: Filtreleme seçenekleri
            top_k: Her cümle için kaç benzer cümle döndürülecek
        """
        print(f"🔍 Searching for {len(query_sentences)} sentences...")
        
        # Embeddings oluştur
        query_embeddings = []
        for sentence in query_sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence.split()) >= 3:
                query_embeddings.append(self.create_single_embedding(clean_sentence))
            else:
                # Boş embedding
                query_embeddings.append([0.0] * 768)
        
        # Sunucuya gönder
        payload = {
            "embeddings": query_embeddings,
            "filters": filters or {},
            "top_k": top_k
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/search_sentences",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Found {len(result.get('similar_sentences', []))} results")
                return result
            else:
                error_msg = f"Server error: {response.status_code}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

# Örnek kullanım
if __name__ == "__main__":
    # Client oluştur
    client = LocalEmbeddingClient("http://localhost:5000")
    
    # Örnek bölüm ekleme
    sample_content = """
    Merhaba, ben Ali. Bugün çok güzel bir gün. 
    Hava çok güzel ve ben dışarı çıkmak istiyorum.
    Arkadaşlarımla buluşacağız ve birlikte yürüyüş yapacağız.
    """
    
    result = client.insert_episode(
        project_name="Test Dizisi",
        season=1,
        episode_number=1,
        timecode="00:05:30",
        content=sample_content
    )
    print("Insert result:", result)
    
    # Örnek arama
    query_sentences = [
        "Bugün hava nasıl?",
        "Arkadaşlarla ne yapacaksın?"
    ]
    
    search_result = client.search_sentences(
        query_sentences=query_sentences,
        filters={"project_name": "Test Dizisi"},
        top_k=2
    )
    print("Search result:", search_result)
