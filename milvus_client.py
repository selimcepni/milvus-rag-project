from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class MilvusClient:
    def __init__(self):
        self.collection = None
        self.connect()
        self.setup_collection()
    
    def connect(self):
        """Milvus'a bağlan"""
        try:
            connections.connect(
                "default", 
                host=Config.MILVUS_HOST, 
                port=Config.MILVUS_PORT
            )
            logger.info("Milvus connection established")
        except Exception as e:
            logger.error(f"Milvus connection failed: {e}")
            raise
    
    def setup_collection(self):
        """Collection oluştur veya bağlan"""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=Config.EMBEDDING_DIM),
            FieldSchema(name="sentence", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="project_name", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="season", dtype=DataType.INT64),
            FieldSchema(name="episode_number", dtype=DataType.INT64),
            FieldSchema(name="timecode", dtype=DataType.VARCHAR, max_length=50),
        ]
        
        schema = CollectionSchema(fields, "Turkish TV Series Sentences")
        
        collection_name = "tv_series_sentences"
        if collection_name in [c.name for c in connections.get_connection().list_collections()]:
            self.collection = Collection(collection_name)
            logger.info(f"Connected to existing collection: {collection_name}")
        else:
            self.collection = Collection(collection_name, schema)
            self.create_index()
            logger.info(f"Created new collection: {collection_name}")
        
        self.collection.load()
    
    def create_index(self):
        """Index oluştur"""
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": Config.INDEX_NLIST}
        }
        
        self.collection.create_index("embedding", index_params)
        logger.info("Index created")
    
    def insert_sentences(self, sentences, project_name, season, episode_number, timecode, embeddings):
        """Cümleleri ekle"""
        try:
            data = [
                embeddings,
                sentences,
                [project_name] * len(sentences),
                [season] * len(sentences),
                [episode_number] * len(sentences),
                [timecode] * len(sentences)
            ]
            
            self.collection.insert(data)
            self.collection.load()
            
            logger.info(f"Inserted {len(sentences)} sentences")
            return True
            
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return False
    
    def search_similar(self, query_embeddings, filters=None, top_k=1):
        """Benzer cümleleri ara"""
        try:
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": Config.SEARCH_NPROBE}
            }
            
            # Filter oluştur
            filter_expr = None
            if filters:
                conditions = []
                if filters.get('project_name'):
                    conditions.append(f'project_name == "{filters["project_name"]}"')
                if filters.get('season'):
                    conditions.append(f'season == {filters["season"]}')
                if filters.get('episode_number'):
                    conditions.append(f'episode_number == {filters["episode_number"]}')
                if filters.get('exclude_episode'):
                    conditions.append(f'episode_number != {filters["exclude_episode"]}')
                if filters.get('timecode_start') and filters.get('timecode_end'):
                    conditions.append(f'timecode >= "{filters["timecode_start"]}" && timecode <= "{filters["timecode_end"]}"')
                
                if conditions:
                    filter_expr = " && ".join(conditions)
            
            results = self.collection.search(
                data=query_embeddings,
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=["sentence"]
            )
            
            # Sadece cümleleri döndür
            similar_sentences = []
            for hits in results:
                if hits and len(hits) > 0:
                    similar_sentences.append(hits[0].entity.get('sentence'))
                else:
                    similar_sentences.append("")
            
            return similar_sentences
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_stats(self):
        """İstatistikler"""
        return {
            'total_sentences': self.collection.num_entities,
            'collection_name': self.collection.name
        }