from src.database import Database
from src.service.extraxctor_service import extractor
from src.llm_config import llm_embedding

db = Database()
class Chat: 
    async def search_documents(self , question: str, limit: int = 5):
        query_embedding = await extractor.create_query_embeddings(question)
        results = await db.vector_search(query_embedding = query_embedding ,limit=limit)
        print("RESULTS:", results)
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

        # 1. Retrieve relevant documents
        results = await self.search_documents(
            question,
            limit
        )

        # 2. Create context from retrieved chunks
        context = "\n\n".join(
            result["text"]
            for result in results
        )

        # 3. Send context + question to LLM
        answer = await self.generate_answer(
            question=question,
            context=context
        )

        return {
            "question": question,
            "answer": answer,
            "sources": results
        }   

    

chat_service = Chat()
