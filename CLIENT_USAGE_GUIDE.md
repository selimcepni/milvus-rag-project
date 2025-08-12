# 🚀 Milvus RAG Client Kullanım Kılavuzu (Optimize Edilmiş)

Bu kılavuz, **timecode ve season metadata** ile optimize edilmiş Milvus RAG sisteminizi **local embedding** ile nasıl kullanacağınızı açıklar.

## 📋 Sistem Mimarisi

```
[Kendi Bilgisayarınız]          [Ubuntu Sunucu]
┌─────────────────────┐         ┌─────────────────┐
│  Client Script      │   HTTP  │   Flask API     │
│  - Text Processing  │ ──────► │   - Milvus DB   │
│  - Embedding        │         │   - Storage     │
│  - API Requests     │         │   - Search      │
└─────────────────────┘         └─────────────────┘
```

## 🔧 Kurulum

### 1. Kendi Bilgisayarınızda (Windows)
```bash
pip install sentence-transformers nltk requests torch
```

### 2. Ubuntu Sunucuda
```bash
# Sadece Milvus ve Flask gerekli
pip install flask pymilvus
```

## 📝 API Değişiklikleri

### Eski API ❌
```python
# Sunucu embedding yapıyordu
POST /insert_episode
{
  "content": "Ham metin...",
  "project_name": "Dizi",
  ...
}
```

### Yeni API ✅
```python
# Client embedding yapıyor
POST /insert_sentences  
{
  "sentences": ["cümle1", "cümle2", ...],
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...], ...],
  "project_name": "Dizi",
  ...
}
```

## 🎯 Kullanım Örnekleri

### 1. Basit Kullanım
```python
from client_embedding import LocalEmbeddingClient

# Client oluştur
client = LocalEmbeddingClient("http://your-server:5000")

# Dizi bölümü ekle
result = client.insert_episode(
    project_name="Kurtlar Vadisi",
    season=1,
    episode_number=1,
    timecode="00:15:30",
    content="Polat Alemdar yeni bir görev aldı..."
)

print(result)
# {'status': 'success', 'message': 'Inserted 25 sentences', ...}
```

### 2. Cümle Arama
```python
# Benzer cümleleri ara
search_result = client.search_sentences(
    query_sentences=[
        "Polat ne yapıyor?",
        "Yeni görev nedir?"
    ],
    filters={"project_name": "Kurtlar Vadisi"},
    top_k=3  # Her cümle için 3 benzer cümle
)

print(search_result['similar_sentences'])
# ['Polat Alemdar yeni bir görev aldı', 'Görev çok gizliydi', ...]
```

### 3. Toplu İşlem
```python
# Birden fazla bölüm ekle
episodes = [
    {
        "project_name": "Muhteşem Yüzyıl",
        "season": 1,
        "episode_number": 1,
        "timecode": "00:05:00",
        "content": "Süleyman tahta çıktı..."
    },
    {
        "project_name": "Muhteşem Yüzyıl", 
        "season": 1,
        "episode_number": 2,
        "timecode": "00:10:15",
        "content": "Hürrem saraya geldi..."
    }
]

for episode in episodes:
    result = client.insert_episode(**episode)
    print(f"S{episode['season']}E{episode['episode_number']} @ {episode['timecode']}: {result['message']}")
```

## 🔍 Gelişmiş Arama

### Filtreli Arama
```python
# Sadece belirli bölümlerde ara
result = client.search_sentences(
    query_sentences=["Aşk sahnesi"],
    filters={
        "project_name": "Muhteşem Yüzyıl",
        "season": 1,
        "episode_number": 5,  # Sadece S1E5'te
        "timecode_start": "00:20:00",  # 20. dakikadan sonra
        "timecode_end": "00:40:00",   # 40. dakikaya kadar
        # "exclude_episode": 3  # 3. bölümü hariç tut
    },
    top_k=5
)
```

### Çoklu Sorgu
```python
# 30 cümlelik büyük sorgu (orijinal tasarım)
big_query = [f"Cümle {i}" for i in range(30)]

result = client.search_sentences(
    query_sentences=big_query,
    filters={"project_name": "Kurtlar Vadisi"}
)

# 30 benzer cümle döner
print(len(result['similar_sentences']))  # 30
```

## 📊 API Endpoint'leri

### 1. Sağlık Kontrolü
```bash
GET /health
```
**Yanıt:**
```json
{
  "status": "healthy",
  "milvus_stats": {
    "total_sentences": 1250,
    "collection_name": "tv_series_sentences"
  }
}
```

### 2. Cümle Ekleme
```bash
POST /insert_sentences
```
**İstek:**
```json
{
  "sentences": ["cümle1", "cümle2"],
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "project_name": "Dizi Adı",
  "season": 1,
  "episode_number": 1,
  "timecode": "00:15:30"
}
```

### 3. Cümle Arama
```bash
POST /search_sentences
```
**İstek:**
```json
{
  "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "filters": {
    "project_name": "Dizi Adı",
    "season": 1,
    "episode_number": 1,
    "timecode_start": "00:10:00",
    "timecode_end": "00:20:00"
  },
  "top_k": 3
}
```

## ⚡ Performans İpuçları

### 1. Batch İşlem
```python
# Büyük metinleri parçalara böl
def process_large_content(client, content, chunk_size=1000):
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        client.insert_episode(
            project_name="Büyük Dizi",
            episode_number=i+1,
            episode_title=f"Parça {i+1}",
            content=chunk
        )
```

### 2. Embedding Cache
```python
# Aynı cümleleri tekrar embed etmeyin
class CachedClient(LocalEmbeddingClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embedding_cache = {}
    
    def create_single_embedding(self, sentence):
        if sentence in self.embedding_cache:
            return self.embedding_cache[sentence]
        
        embedding = super().create_single_embedding(sentence)
        self.embedding_cache[sentence] = embedding
        return embedding
```

## 🔧 Hata Ayıklama

### Yaygın Hatalar

1. **Sunucu bağlantı hatası**
```python
# Sunucunun çalıştığını kontrol edin
import requests
try:
    response = requests.get("http://your-server:5000/health")
    print(response.json())
except:
    print("Sunucu çalışmıyor!")
```

2. **Embedding boyut hatası**
```python
# Embedding boyutu 768 olmalı
embedding = client.create_single_embedding("test")
print(len(embedding))  # 768 olmalı
```

3. **Cümle-embedding sayı uyumsuzluğu**
```python
sentences = ["cümle1", "cümle2"]
embeddings = client.create_embeddings(sentences)
assert len(sentences) == len(embeddings)
```

## 🎉 Özet

✅ **Artık embedding işlemleri kendi bilgisayarınızda yapılıyor**  
✅ **Sunucu sadece vektör depolama/arama yapıyor**  
✅ **API'ler hazır vektör kabul ediyor**  
✅ **Performans ve güvenlik artmış durumda**

**Kullanmaya başlamak için:**
```bash
# 1. Sunucuyu başlat (Ubuntu)
python app.py

# 2. Client script'ini çalıştır (Windows)
python example_usage.py
```
