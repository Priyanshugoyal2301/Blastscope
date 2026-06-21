import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    transcript_path = r"C:\Users\Priyanshu Goyal\.gemini\antigravity-ide\brain\2987a6cb-9fc3-486d-96c6-ba7dc0b1fd7c\.system_generated\logs\transcript.jsonl"
    with open(transcript_path, "r", encoding="utf-8") as f:
        steps = [json.loads(line) for line in f]
    
    user_inputs = [s for s in steps if s.get("type") == "USER_INPUT"]
    print("=== Last 3 User Inputs ===")
    user_msgs = user_inputs[-3:]
    for m in user_msgs:
        print(f"Step {m.get('step_index')}:")
        print(m.get("content"))
        print("-" * 50)
        
    model_responses = [s for s in steps if s.get("type") == "PLANNER_RESPONSE"]
    print("=== Last 2 Model Responses ===")
    for m in model_responses[-2:]:
        print(f"Step {m.get('step_index')}:")
        print(m.get("content")[:2000] if m.get("content") else "")
        print("-" * 50)

if __name__ == "__main__":
    main()
