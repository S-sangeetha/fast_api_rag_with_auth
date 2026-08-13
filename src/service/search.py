from src.database import Database
from src.service.extraxctor_service import extractor
from src.llm_config import llm_embedding

db = Database()
class Chat: 

    def format_timestamp(
        self,
        start_time: float | None,
        end_time: float | None
    ) -> str | None:

        if start_time is None or end_time is None:
            return None

        start_minutes = int(start_time // 60)
        start_seconds = int(start_time % 60)

        end_minutes = int(end_time // 60)
        end_seconds = int(end_time % 60)

        return (
            f"{start_minutes:02d}:{start_seconds:02d}"
            f" - "
            f"{end_minutes:02d}:{end_seconds:02d}"
        )
    
    async def search_documents(self , question: str, limit: int = 5):
        query_embedding = await extractor.create_query_embeddings(question)
        results = await db.vector_search(query_embedding = query_embedding ,limit=limit)
        RELEVANCE_THRESHOLD = 0.80
        results = [result for result in results if result["score"] >= RELEVANCE_THRESHOLD]
        return results


    async def generate_answer(self, question : str , context :str):
        prompt = f"""
            You are a helpful company knowledge assistant.

        Answer the user's question using ONLY the information
        provided in the context below.

        If the answer cannot be found in the context,
        say: "I couldn't find that information in the documents."

        Do not make up information.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """

        response = await llm_embedding.llm.ainvoke(prompt)

        return "".join(
            block["text"]
            for block in response.content
              if isinstance(block, dict) and block.get("type") == "text")


    async def generate_rag_answer(self,question: str,limit: int = 5):

        results = await self.search_documents(
            question,
            limit
        )

        context = "\n\n".join(
            result["text"]
            for result in results
        )

        answer = await self.generate_answer(
            question=question,
            context=context
        )
        for result in results:
            result["timestamp"] = self.format_timestamp(
            result.get("start_time"),
            result.get("end_time")
            )
        print(result)
        return {
            "question": question,
            "answer": answer,
            "sources": results
        }   

    

chat_service = Chat()
