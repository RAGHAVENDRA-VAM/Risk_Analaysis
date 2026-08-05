import sys
import os

sys.path.insert(0, os.path.abspath("."))

from app.services.risk_analysis_service import risk_analysis_service

try:
    files = [{"path": "config.py", "content": "api_key='sk-12345'"}]
    result = risk_analysis_service.analyze_commit("test_commit", "main", files)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
