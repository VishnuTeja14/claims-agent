import sys
import json
import os
from src.agent import ClaimsAgent

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <fnol_pdf>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    agent = ClaimsAgent()
    # Note: For this assessment, we assume the agent handles the multimodal extraction
    result = agent.process_claim(file_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
