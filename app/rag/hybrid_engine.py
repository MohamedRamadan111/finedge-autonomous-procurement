from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

class HybridQualityEngine:
    def __init__(self, connection_string: str = None):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.connection = connection_string or settings.database_url
        self.collection_name = "procurement_docs"

    async def get_vector_store(self) -> PGVector:
        conn_str = self.connection.replace("postgresql+psycopg://", "postgresql+psycopg://")
        return PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=conn_str,
            use_jsonb=True,
        )

    async def retrieve(self, query: str, top_k: int = 3):
        store = await self.get_vector_store()
        docs = await store.asimilarity_search(query, k=top_k)
        return [doc.page_content for doc in docs]

hybrid_engine = HybridQualityEngine()
