#!/usr/bin/env python3
"""
Test script to verify the SSL fix for LightPanda API
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import scraper

def test_lightpanda_fallback():
    """Test that the LightPanda API fallback works correctly"""
    print("🧪 Testing LightPanda API fallback mechanism...")
    
    # Test with a simple URL
    test_url = "https://httpbin.org/html"
    
    print(f"📡 Testing scraping with URL: {test_url}")
    
    try:
        # This should trigger the SSL error and fall back to direct scraping
        result = scraper.scrape_with_service(test_url)
        
        if result and len(result) > 100:
            print("✅ SUCCESS: Fallback mechanism working correctly!")
            print(f"📊 Retrieved {len(result)} characters of content")
            return True
        else:
            print("❌ FAILED: No content retrieved")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_connection_diagnostics():
    """Test the connection diagnostics"""
    print("\n🔍 Running connection diagnostics...")
    
    try:
        scraper.diagnose_network_issues()
        print("✅ Diagnostics completed")
        return True
    except Exception as e:
        print(f"❌ Diagnostics failed: {e}")
        return False

if __name__ == "__main__":
    print("🌍 AI Voyage Assistant - SSL Fix Test")
    print("=" * 50)
    
    # Test 1: Fallback mechanism
    test1_passed = test_lightpanda_fallback()
    
    # Test 2: Connection diagnostics
    test2_passed = test_connection_diagnostics()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"   Fallback Mechanism: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Connection Diagnostics: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The SSL fix is working correctly.")
        print("💡 The application should now handle LightPanda API failures gracefully.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
