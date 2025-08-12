#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milvus RAG Client Kullanım Örnekleri
====================================

Bu dosya, local embedding client'ını nasıl kullanacağınızı gösterir.
"""

from client_embedding import LocalEmbeddingClient

def example_1_insert_episode():
    """Örnek 1: Dizi bölümü ekleme"""
    print("=" * 50)
    print("ÖRNEK 1: DİZİ BÖLÜMÜ EKLEME")
    print("=" * 50)
    
    # Client oluştur
    client = LocalEmbeddingClient("http://localhost:5000")
    
    # Örnek dizi içeriği
    episode_content = """
    Ahmet sabah erkenden kalktı. Bugün çok önemli bir toplantısı vardı.
    Kahvaltısını hızlıca yaptı ve evden çıktı. Yolda arkadaşı Mehmet'le karşılaştı.
    "Merhaba Ahmet, nereye bu kadar acele?" diye sordu Mehmet.
    "Önemli bir toplantım var, geç kalmamalıyım" dedi Ahmet.
    İkisi birlikte yürümeye başladılar. Hava çok güzeldi.
    """
    
    # Bölümü ekle
    result = client.insert_episode(
        project_name="Günlük Hayat",
        season=1,
        episode_number=1,
        timecode="08:00:00",
        content=episode_content
    )
    
    print(f"Sonuç: {result}")

def example_2_search_sentences():
    """Örnek 2: Cümle arama"""
    print("\n" + "=" * 50)
    print("ÖRNEK 2: CÜMLE ARAMA")
    print("=" * 50)
    
    # Client oluştur
    client = LocalEmbeddingClient("http://localhost:5000")
    
    # Arama cümleleri
    search_queries = [
        "Sabah erken kalkmak",
        "Arkadaşla karşılaşmak",
        "Toplantıya gitmek"
    ]
    
    # Arama yap
    result = client.search_sentences(
        query_sentences=search_queries,
        filters={"project_name": "Günlük Hayat"},
        top_k=2  # Her cümle için 2 benzer cümle
    )
    
    print(f"Arama sonuçları:")
    for i, similar in enumerate(result.get('similar_sentences', [])):
        print(f"  {i+1}. {similar}")

def example_3_multiple_episodes():
    """Örnek 3: Birden fazla bölüm ekleme"""
    print("\n" + "=" * 50)
    print("ÖRNEK 3: ÇOKLU BÖLÜM EKLEME")
    print("=" * 50)
    
    client = LocalEmbeddingClient("http://localhost:5000")
    
    episodes = [
        {
            "project_name": "Aile Hikayesi",
            "season": 1,
            "episode_number": 1,
            "timecode": "00:10:15",
            "content": "Elif yeni eve taşındı. Komşuları çok nazikti. Kapı çaldı ve komşusu Ayşe geldi."
        },
        {
            "project_name": "Aile Hikayesi", 
            "season": 1,
            "episode_number": 2,
            "timecode": "00:05:30",
            "content": "Elif ve Ayşe çok iyi arkadaş oldular. Birlikte alışverişe gittiler ve çay içtiler."
        }
    ]
    
    for episode in episodes:
        print(f"\n📺 İşleniyor: {episode['project_name']} - S{episode['season']}E{episode['episode_number']} @ {episode['timecode']}")
        result = client.insert_episode(**episode)
        print(f"   Sonuç: {result.get('message', result)}")

def example_4_filtered_search():
    """Örnek 4: Filtreli arama"""
    print("\n" + "=" * 50)
    print("ÖRNEK 4: FİLTRELİ ARAMA")
    print("=" * 50)
    
    client = LocalEmbeddingClient("http://localhost:5000")
    
    # Sadece belirli bir dizide ara
    result = client.search_sentences(
        query_sentences=["Yeni ev", "Komşu"],
        filters={
            "project_name": "Aile Hikayesi",
            "season": 1,
            "episode_number": 1,  # Sadece S1E1'de ara
            "timecode_start": "00:00:00",
            "timecode_end": "00:15:00"  # İlk 15 dakikada ara
        },
        top_k=3
    )
    
    print("Filtreli arama sonuçları:")
    for i, similar in enumerate(result.get('similar_sentences', [])):
        print(f"  {i+1}. {similar}")

def main():
    """Ana fonksiyon - tüm örnekleri çalıştır"""
    print("🚀 Milvus RAG Client Örnekleri Başlıyor...")
    
    try:
        # Örnekleri sırayla çalıştır
        example_1_insert_episode()
        example_2_search_sentences()
        example_3_multiple_episodes()
        example_4_filtered_search()
        
        print("\n✅ Tüm örnekler başarıyla tamamlandı!")
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}")
        print("Sunucunun çalıştığından emin olun: python app.py")

if __name__ == "__main__":
    main()
