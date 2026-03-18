import traceback
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("Starting manual test client simulation...")
try:
    url = "https://www.youtube.com/watch?v=0kP0SShSHeY"
    response = client.get(f"/analyze_youtube?url={url}")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.text[:2000])
except Exception as e:
    print("Pipeline Crashed with Exception:")
    traceback.print_exc()
