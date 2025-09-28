#!/usr/bin/env python3
"""
Test Google Custom Search API with provided credentials
"""

import os
from googleapiclient.discovery import build

def test_google_search():
    """Test Google Custom Search API"""
    
    # Get API key from environment variables
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    print(f"🔑 Testing Google Search API")
    
    if not api_key:
        print("❌ GOOGLE_SEARCH_API_KEY not found in environment variables")
        print("💡 Please set GOOGLE_SEARCH_API_KEY in your .env file")
        return
    
    if not search_engine_id:
        print("❌ GOOGLE_SEARCH_ENGINE_ID not found in environment variables")
        print("💡 Please set GOOGLE_SEARCH_ENGINE_ID in your .env file")
        return
    
    print(f"📋 API Key: {api_key[:20]}...")
    print(f"🔍 Search Engine ID: {search_engine_id}")
    
    try:
        # Build the Custom Search service
        service = build("customsearch", "v1", developerKey=api_key)
        print("✅ Google API service built successfully")
        
        # Test search query
        query = "Rome Colosseum photography"
        print(f"🔍 Testing search query: '{query}'")
        
        # Execute the search
        result = service.cse().list(
            q=query,
            cx=search_engine_id,
            searchType='image',
            num=2,
            imgSize='LARGE',
            imgType='photo',
            safe='active'
        ).execute()
        
        print(f"📊 Search executed successfully")
        
        # Check results
        if 'items' in result:
            print(f"✅ Found {len(result['items'])} images:")
            for i, item in enumerate(result['items'][:2]):
                print(f"  {i+1}. {item.get('title', 'No title')}")
                print(f"     URL: {item['link'][:60]}...")
                print(f"     Thumbnail: {item.get('image', {}).get('thumbnailLink', 'No thumbnail')[:60]}...")
        else:
            print("⚠️ No images found in results")
            print(f"📋 Response keys: {list(result.keys())}")
            
    except Exception as e:
        print(f"❌ Google Search API error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_google_search()
    if success:
        print("\n✅ Google Search API test completed successfully!")
    else:
        print("\n❌ Google Search API test failed!")
