from flask import Flask, request, jsonify
import logging
import time
import os
import threading

from milvus_client import MilvusClient
from config import Config

# Logging setup
os.makedirs('/opt/milvus-rag/logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Global objects
milvus_client = None
processing_lock = threading.Lock()

def initialize_services():
    """Servisleri başlat"""
    global milvus_client
    
    try:
        logger.info("Initializing services...")
        milvus_client = MilvusClient()
        logger.info("Services initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        return False

# Try to initialize on startup so the service is ready immediately
try:
    if not initialize_services():
        logger.warning("Milvus not ready at startup. Health endpoint will be unhealthy until Milvus is reachable.")
except Exception as e:
    logger.error(f"Startup initialization error: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Sistem durumu"""
    try:
        global milvus_client
        if milvus_client is None:
            initialize_services()
        stats = milvus_client.get_stats() if milvus_client else None
        if not stats:
            return jsonify({'status': 'unhealthy', 'error': 'Milvus not initialized'}), 503
        return jsonify({
            'status': 'healthy',
            'milvus_stats': stats
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/insert_sentences', methods=['POST'])
def insert_sentences():
    """Hazır embedding'lerle cümle ekleme"""
    try:
        data = request.json
        
        # Validation
        required_fields = ['sentences', 'embeddings', 'project_name', 'season', 'episode_number', 'timecode']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        sentences = data['sentences']
        embeddings = data['embeddings']
        
        # Validation
        if len(sentences) != len(embeddings):
            return jsonify({'error': 'Sentences and embeddings count mismatch'}), 400
        
        if not sentences:
            return jsonify({'error': 'No sentences provided'}), 400
        
        # Embedding dimension check
        if embeddings and len(embeddings[0]) != Config.EMBEDDING_DIM:
            return jsonify({'error': f'Embedding dimension must be {Config.EMBEDDING_DIM}'}), 400
        
        # Insert to Milvus
        success = milvus_client.insert_sentences(
            sentences=sentences,
            project_name=data['project_name'],
            season=data['season'],
            episode_number=data['episode_number'],
            timecode=data['timecode'],
            embeddings=embeddings
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Inserted {len(sentences)} sentences',
                'episode': f"{data['project_name']} - S{data['season']}E{data['episode_number']} @ {data['timecode']}"
            })
        else:
            return jsonify({'error': 'Insert failed'}), 500
            
    except Exception as e:
        logger.error(f"Insert error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/search_sentences', methods=['POST'])
def search_sentences():
    """Hazır embedding'lerle arama"""
    try:
        data = request.json
        query_embeddings = data.get('embeddings', [])
        filters = data.get('filters', {})
        top_k = data.get('top_k', 1)
        
        if not query_embeddings:
            return jsonify({'error': 'Embeddings required'}), 400
        
        # Embedding dimension check
        if query_embeddings and len(query_embeddings[0]) != Config.EMBEDDING_DIM:
            return jsonify({'error': f'Embedding dimension must be {Config.EMBEDDING_DIM}'}), 400
        
        start_time = time.time()
        
        with processing_lock:
            # Search
            similar_sentences = milvus_client.search_similar(query_embeddings, filters, top_k=top_k)
        
        processing_time = time.time() - start_time
        
        return jsonify({
            'status': 'success',
            'similar_sentences': similar_sentences,
            'processing_time': processing_time
        })
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Flask uygulamasını doğrudan çalıştırmak için
if __name__ == '__main__':
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)