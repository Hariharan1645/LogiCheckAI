import json
import os

def create_instant_cache():
    video_id = "1p-D_wb3CMo"
    cache_dir = os.path.join(os.path.dirname(__file__), "backend", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{video_id}.json")
    
    # Standard reasoning text previously retrieved
    reasoning_text = """### Medical Fact-Checking Analysis
#### Health Content Status
This video contains no significant healthcare topics. The dialogue appears to be about general mental fatigue or habits regarding screen time, rather than providing healthcare advise direction.

#### Overall Safety & Accuracy Verdict
The video contents do not pose any immediate safety concerns regarding medical information, as they do not offer any substantive statements. 

#### Detected Errors/False Claims
- **Claims Extracted**: No direct medical false assertions or factual direction are detected. 

#### Final Recommendation
- **Critical Viewing**: Verify information through reputable sources before acting upon it.
- **Healthy Habits**: Be mindful of your screen time and ensure you are maintaining a balance that allows for adequate sleep."""

    payload = {
        "claims": [],
        "reasoning": reasoning_text
    }
    
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
    print(f"Instant Cache created for {video_id} at {cache_path}")

if __name__ == "__main__":
    create_instant_cache()
