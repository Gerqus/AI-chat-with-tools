from typing import List
from googlesearch import search, SearchResult

def search_google(search_str: str) -> List[SearchResult]:
    return [result for result in search(search_str, num_results=5, lang="en", timeout=10, advanced=True)]
