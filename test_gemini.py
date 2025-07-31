#!/usr/bin/env python3
"""
Quick test script for optimized Gemini integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gemini_simple import ask_question

def test_gemini():
    print("Testing optimized Gemini integration...")
    
    # Test basic question
    question = "What should I do for a cut on my hand?"
    coords = (15.5007, 32.5599)  # Khartoum coordinates
    
    print(f"Question: {question}")
    print("Generating response...")
    
    try:
        response = ask_question(question, coords)
        print(f"\nResponse: {response[:200]}..." if len(response) > 200 else f"\nResponse: {response}")
        print("\n✅ Test completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_gemini()
