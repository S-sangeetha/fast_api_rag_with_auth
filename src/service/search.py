from src.database import Database
from src.service.extraxctor_service import extractor
from src.llm_config import llm_embedding
from src.hf_llm import hf_llm
import asyncio
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
    #all sources are in one context.
    
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
        candidate_limit = 10
        vector_results = await db.vector_search(query_embedding = query_embedding ,limit=candidate_limit,source_types=source_types)
        keyword_results = await db.keyword_search( question=question, limit=candidate_limit,source_types=source_types)
        results = self.rank_fusion(vector_results , keyword_results)
        results = await self.rerank_results(question,results,top_k=limit)
        
        return results

    def merge_results( self,vector_results, keyword_results):

        merged = {}

        for result in vector_results:

            document_id = result["document_id"]

            merged[document_id] = result

        for result in keyword_results:

            document_id = result["document_id"]

            if document_id in merged:

                merged[document_id]["keyword_score"] = (
                    result.get("keyword_score", 0)
                )

            else:

                merged[document_id] = result

        return list(merged.values())

    
    async def rerank_results(
    self,
    question: str,
    results: list[dict],
    top_k: int = 3
):
        if not results:
            return []

        candidates = "\n\n".join(
            f"""
    Document {index + 1}:
    {result.get("text", "")}
    """
            for index, result in enumerate(results)
        )

        prompt = f"""
    You are a RAG reranking system.

    User question:
    {question}

    Candidate documents:
    {candidates}

    Rank the candidate documents based on how relevant
    they are to answering the user's question.

    Return ONLY the document numbers in order of relevance.

    Example:
    2,1,3

    Do not explain anything.
    """

        response = await hf_llm.generate(prompt)

        try:
            rankings = [
                int(x.strip())
                for x in response.split(",")
                if x.strip().isdigit()
            ]
        except Exception:
            return results[:top_k]

        reranked = []

        for index in rankings:

            if 1 <= index <= len(results):
                reranked.append(results[index - 1])

        return reranked

    async def retrieve_all(self, sub_questions):

        tasks = [
            self.search_documents(
                question=item["question"],
                source_types=[item["source_type"]]
            )
            for item in sub_questions
        ]

        results = await asyncio.gather(*tasks)

        all_results = [
            result
            for result_group in results
            for result in result_group
        ]
        all_results = rag_router.deduplicate_results(all_results)
        return all_results
    #rrf
    def rank_fusion(self,vector_results : list[dict],keyword_results : list[dict],k:int =60 ):
        scores ={}
        documents = {}

        for rank , result in enumerate(vector_results , start =1):
            document_id = result["document_id"]
            documents[document_id] = result
            scores[document_id] = (scores.get(document_id,0)+1 / (k +rank))

        for rank , result in enumerate (keyword_results , start=1):
            document_id = result["document_id"]
            documents[document_id]= result
            scores[document_id] = (scores.get(document_id , 0) +1/(k+rank))


        ranked_documents = sorted(documents.items(),key = lambda item : scores[item[0]],reverse= True)
        results = []
        for document_id, result in ranked_documents:
            result = result.copy()
            result["rrf_score"] = scores[document_id]
            results.append(result)
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

        response = await hf_llm.generate(prompt)

        return response

    async def search_with_fallback(
        self,
        question: str,
        limit: int,
        preferred_source: str
    ):
        # Get all available source types
        available_sources = await db.get_source_types()

        # First search the source selected by classifier
        results = await self.search_documents(
            question,
            limit,
            source_types=[preferred_source]
        )

        # Check whether retrieved results are actually relevant
        is_relevant = await rag_router.validate_relevance(
            question,
            results
        )

        if is_relevant:
            return results

        print(
            f"No relevant result in {preferred_source}. "
            f"Trying other sources..."
        )

        # Search remaining sources
        other_sources = [
            source
            for source in available_sources
            if source != preferred_source
        ]

        for source in other_sources:

            results = await self.search_documents(
                question,
                limit,
                source_types=[source]
            )

            is_relevant = await rag_router.validate_relevance(
                question,
                results
            )

            if is_relevant:
                print(f"Relevant result found in: {source}")
                return results

        return []
    async def generate_rag_answer(self,question: str,limit: int = 5):
        source_type = await rag_router.classify_question(question)
        
        if source_type != "multi":
                
            results = await self.search_with_fallback(
                question=question,
                limit=limit,
                preferred_source=source_type
            )
        else: 
            sub_questions = await rag_router.decompose_question(question)
    
            results = await self.retrieve_all(sub_questions)
        if not results:
            return {
                "question": question,
                "answer": "Could not find the answer in the provided sources.",
                "sources": []
            }

        context =await self.build_context(results)

        answer = await self.generate_answer(
            question=question,
            context=context
        )
        sources = []
        for result in results:
            metadata = result.get("metadata", {})
            start_time = metadata.get("start_time")
            end_time = metadata.get("end_time")
            timestamp = None

            if start_time is not None and end_time is not None:
                result["timestamp"] = {
                    "start_time": start_time,
                    "end_time": end_time
                }
          
            sources.append({
            "document_id": result.get("document_id"),
            "file_name": result.get("file_name"),
            "chunk_index": result.get("chunk_index"),
            "text": result.get("text"),
            "source_type": result.get("source_type"),
            "metadata": metadata,
            "vector_score": result.get("score"),
            "keyword_score": result.get("keyword_score"),
            "rrf_score": result.get("rrf_score"),
            "timestamp": timestamp
                 })
        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }   

    

chat_service = Chat()
