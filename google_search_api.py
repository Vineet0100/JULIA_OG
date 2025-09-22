from googleapiclient.discovery import build
from config import GOOGLE_API_KEY, CSE_ID

def google_search_api(query):
    """
    Perform a Google search and return the top snippet without the URL.
    """
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=CSE_ID, num=1).execute()
        if "items" in res:
            item = res["items"][0]
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            # Clean snippet: remove extra whitespace and newlines
            snippet_clean = " ".join(snippet.split())
            return f"{title}: {snippet_clean}"
        else:
            return "I couldn't find any results for that."
    except Exception as e:
        return f"Sorry, I couldn't perform the search. Error: {e}"
