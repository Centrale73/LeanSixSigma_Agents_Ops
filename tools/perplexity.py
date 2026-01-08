import httpx
from agno.tools import Toolkit
from settings import settings

class PerplexitySearchTool(Toolkit):
    def __init__(self):
        super().__init__(name="perplexity_search")
        self.register(self.search_perplexity)

    def search_perplexity(self, query: str) -> str:
        """
        Conducts deep research using the Perplexity API. 
        Use this for the 'Analyze' phase of DMAIC.
        """
        headers = {
            "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": query}
            ]
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(f"{settings.PERPLEXITY_BASE_URL}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error connecting to Perplexity Cognitive Layer: {str(e)}"