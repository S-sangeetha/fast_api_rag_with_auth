from src.database import Database
from src.service.extraxctor_service import extractor
from src.llm_config import llm_embedding
from src.service.rag_router import rag_router
db = Database()
class Chat: 

    def format_timestamp(
        self,
        start_time: float | None,
        end_time: float | None
    ) -> str | None:

        if start_time is None or end_time is None:
            return None

        def format_seconds(value: float) -> str:
            minutes = int(value // 60)
            seconds = int(value % 60)

            return f"{minutes:02d}:{seconds:02d}"

        return (
            f"{format_seconds(start_time)} - "
            f"{format_seconds(end_time)}"
        )

    
    async def build_context(self, results):
        context_parts = []
        for result in results:
            source_type = result.get("source_type", "document")
            filename = result.get("file_name", "unknown")
            text = result.get("text", "")
            metadata = result.get("metadata", {})

            part = f"[{source_type.upper()} SOURCE]\n"
            part += f"File: {filename}\n" 

            if source_type == "audio":
                start_time = metadata.get("start_time")
                end_time = metadata.get("end_time")

                if start_time is not None and end_time is not None:
                     timestamp = (
                        f"{self.format_timestamp(start_time)} - "
                        f"{self.format_timestamp(end_time)}"
                    )
                     part += f"Timestamp: {timestamp}\n"
            part += f"Content:\n{text}"
            context_parts.append(part)
        return "\n\n---\n\n".join(context_parts)

    async def search_documents(self , question: str, limit: int = 5, source_types: list[str] | None = None):
        query_embedding = await extractor.create_query_embeddings(question)
        results = await db.vector_search(query_embedding = query_embedding ,limit=limit,source_types=source_types)
        RELEVANCE_THRESHOLD = 0.80
        results = [result for result in results if result["score"] >= RELEVANCE_THRESHOLD]
        
        return results


    async def generate_answer(self, question : str , context :str):
        prompt = f"""
        You are a helpful RAG assistant.
        Answer the user's question using ONLY the information
        provided in the context below.
        The context can contain information from different source types:
        - DOCUMENT
        - IMAGE
        - AUDIO
        Rules:
        1. Do not invent information.
        2. Do not use outside knowledge.
        3. If the answer is not present in the context, say that you
        could not find the answer in the provided sources.
        4. For AUDIO sources, use the timestamp information when it
        helps answer the question.
        5. Keep the answer concise and accurate.

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
        source_type = await rag_router.classify_question(question)
        if source_type == "text":
            source_types = ["text"]

        elif source_type == "audio":
            source_types = ["audio"]

        elif source_type == "image":
            source_types = ["image"]

        elif source_type == "multi":
            source_types = ["text", "audio", "image"]

        else:
            source_types = None

        results = await self.search_documents(
            question,
            limit,
            source_types=source_types
        )
        

        context =await self.build_context(results)

        answer = await self.generate_answer(
            question=question,
            context=context
        )
        for result in results:
            metadata = result.get("metadata", {})
            start_time = metadata.get("start_time")
            end_time = metadata.get("end_time")
            
            result["timestamp"] =(
            start_time,
            end_time
            )
           
        print(result)
        return {
            "question": question,
            "answer": answer,
            "sources": results
        }   

    

chat_service = Chat()
