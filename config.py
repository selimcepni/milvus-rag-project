import os

class Config:
    # Milvus ayarları
    MILVUS_HOST = os.getenv('MILVUS_HOST', 'localhost')
    MILVUS_PORT = os.getenv('MILVUS_PORT', '19530')
    
    # Model ayarları
    MODEL_NAME = 'emrecan/bert-base-turkish-cased-mean-nli-stsb-tr'
    EMBEDDING_DIM = 768
    
    # API ayarları
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG = False
    
    # Milvus v2.6.0 performans ayarları
    BATCH_SIZE = 1000
    SEARCH_NPROBE = 20
    INDEX_NLIST = 2048
    
    # v2.6.0 yeni özellikler
    ENABLE_STORAGE_V2 = True  # Storage Format V2 desteği
    CONNECTION_TIMEOUT = 30   # Bağlantı timeout süresi
    SEARCH_TIMEOUT = 60       # Arama timeout süresi
    
    # Log ayarları
    LOG_LEVEL = 'INFO'
    # Proje kök dizini (env ile override edilebilir)
    PROJECT_ROOT = os.getenv('MILVUS_RAG_ROOT', os.path.dirname(os.path.abspath(__file__)))
    # Log dizini (env ile override edilebilir); varsayılan olarak proje altındaki logs/
    LOG_DIR = os.getenv('MILVUS_RAG_LOG_DIR', os.path.join(PROJECT_ROOT, 'logs'))
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')