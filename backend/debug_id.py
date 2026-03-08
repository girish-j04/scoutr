import os
import sys
from app.services.chroma_service import chroma_service

def check_id(pid):
    results = chroma_service.collection.get(ids=[str(pid)])
    if results["ids"]:
        print(f"Player {pid} FOUND in ChromaDB: {results['metadatas'][0]['name']}")
    else:
        print(f"Player {pid} NOT FOUND in ChromaDB.")

if __name__ == "__main__":
    check_id(sys.argv[1])
