"""
WealthWise AI - Vector Store (Mock)
"""

class VectorStore:
    """
    Mock VectorStore for development/fallback.
    """
    def __init__(self):
        pass
        
    def search(self, query: str, n_results: int = 3):
        """Mock search that returns empty or static results."""
        # For now, return empty lists to prevent errors
        return []
