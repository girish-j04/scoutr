import os
import sys
import chromadb
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.chroma_service import DB_PATH

def check_chroma():
    print(f"Checking ChromaDB at {DB_PATH}")
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        collection = client.get_collection(name="players")
        count = collection.count()
        print(f"Collection 'players' has {count} entries.")
        
        # Try to get 1001
        res = collection.get(ids=["1001"])
        print(f"Result for ID '1001': {res}")
        
        if count > 0:
            # Peek at one entry
            peek = collection.peek(limit=1)
            print(f"Peek at first entry: {peek}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_chroma()
