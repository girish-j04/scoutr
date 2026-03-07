"""
ChromaDB Vector Search Service.

Ported from Dev 1's scoutr-backend. Provides player search via ChromaDB
with smart position mapping for StatsBomb dataset labels.
"""

import chromadb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data_pipeline/data/db/chroma_db')


class ChromaService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(name="players")

    def search_players(self, query: dict):
        """Search players using ChromaDB with smart position mapping."""
        filters = []

        if query.get("position"):
            pos = query["position"].lower().replace("-", " ")
            if "back" in pos:
                if "right" in pos:
                    filters.append({"position": {"$in": ["right back", "right wing back", "right center back", "right-back"]}})
                elif "left" in pos:
                    filters.append({"position": {"$in": ["left back", "left wing back", "left center back", "left-back"]}})
                elif "center" in pos or "centre" in pos:
                    filters.append({"position": {"$in": ["center back", "centre back", "right center back", "left center back"]}})
                else:
                    filters.append({"position": query["position"]})
            elif "mid" in pos:
                if "defensive" in pos or "dm" in pos:
                    filters.append({"position": {"$in": ["center defensive midfield", "left defensive midfield", "right defensive midfield"]}})
                elif "attacking" in pos or "am" in pos:
                    filters.append({"position": {"$in": ["center attacking midfield", "left attacking midfield", "right attacking midfield"]}})
                elif "right" in pos:
                    filters.append({"position": {"$in": ["right midfield", "right center midfield", "right defensive midfield", "right attacking midfield"]}})
                elif "left" in pos:
                    filters.append({"position": {"$in": ["left midfield", "left center midfield", "left defensive midfield", "left attacking midfield"]}})
                elif "center" in pos:
                    filters.append({"position": {"$in": ["center midfield", "right center midfield", "left center midfield", "center defensive midfield", "center attacking midfield"]}})
                else:
                    filters.append({"position": {"$in": ["center midfield", "left center midfield", "right center midfield"]}})
            elif "forward" in pos or "striker" in pos:
                filters.append({"position": {"$in": ["center forward", "right center forward", "left center forward", "striker", "secondary striker"]}})
            elif "wing" in pos:
                if "right" in pos:
                    filters.append({"position": {"$in": ["right wing", "right winger"]}})
                elif "left" in pos:
                    filters.append({"position": {"$in": ["left wing", "left winger"]}})
                else:
                    filters.append({"position": {"$in": ["right wing", "left wing", "right winger", "left winger"]}})
            elif "goal" in pos or "gk" in pos:
                filters.append({"position": "goalkeeper"})
            else:
                filters.append({"position": query["position"]})

        if query.get("max_age"):
            filters.append({"age": {"$lte": query["max_age"]}})
        if query.get("min_press_score"):
            filters.append({"pressure_success_rate": {"$gte": query["min_press_score"]}})

        where_clause = None
        if len(filters) == 1:
            where_clause = filters[0]
        elif len(filters) > 1:
            where_clause = {"$and": filters}

        results = self.collection.get(
            where=where_clause
        )
        return results


chroma_service = ChromaService()
