import sys
sys.path.append('.')
try:
    import app.services.genai_risk_analyzer_service
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
