# Milvus RAG System - Turkish TV Series

Türkçe dizi bölümleri için cümle bazlı RAG (Retrieval-Augmented Generation) sistemi.

## 🚀 Özellikler

- 30 cümle gönder → 30 benzer cümle al
- Türkçe NLP optimizasyonu
- Proje/bölüm bazlı filtreleme
- RESTful API
- Production-ready deployment

## 📋 Gereksinimler

- Python 3.8+
- Milvus 2.3+
- Ubuntu 20.04+ (önerilen)

Sunucu (API) için minimal bağımlılıklar:

```
flask
pymilvus
gunicorn
```

Embedding üretimi tamamen istemci tarafındadır. İstemci için `sentence-transformers`, `torch`, `nltk` vb. paketleri kendi ortamınızda kurun.

## 🔧 Kurulum

### Otomatik Kurulum (Sunucu Minimal)
```bash
./scripts/install.sh