#!/usr/bin/env python3

import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Test the AI insights function directly
from api import get_ai_insights
from database import get_db

# Test with a mock database session
def test_ai_insights():
    try:
        # Get a database session
        db = next(get_db())
        
        # Call the AI insights function
        result = get_ai_insights(1, db)
        
        print("AI Insights Result:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_insights()
