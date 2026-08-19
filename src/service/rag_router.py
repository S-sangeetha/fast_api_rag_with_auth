from src.llm_config import llm_embedding
from src.hf_llm import  hf_llm
from src.database import Database
db = Database()

class Router:

   async def classify_question(self, question: str):

        source_types = await db.get_source_types()

        source_types_text = "\n".join(
            f"- {source_type}"
            for source_type in source_types
        )

        prompt = f"""
You are a RAG source router.

Available source types in the knowledge base:

{source_types_text}

The user question may require information from one
or multiple source types.

Determine which source types are required to answer
the question.

Rules:

1. Select only source types that are actually needed.
2. If only one source type is required, return that source type.
3. If multiple source types are required, return "multi".
4. Return ONLY one of the following:

{chr(10).join(source_types)}
multi

Question:
{question}

Answer:
"""

        response = await hf_llm.generate(prompt)

        result = response.strip().lower()

        print("AVAILABLE SOURCES:", source_types)
        print("CLASSIFIER RESULT:", result)

        if result in source_types:
            return result

        if result == "multi":
            return "multi"

        return "multi"

    
   async def decompose_question(self, question: str) -> list[dict]:

            prompt = f"""
        You are a question routing system for a Multi-RAG application.

        Break the user's question into independent sub-questions.

        For each sub-question, identify the most appropriate source type.

        Allowed source types:
        - text
        - image
        - audio

        If a question requires multiple source types, create separate sub-questions.

        Return ONLY valid JSON in this exact format:

        [
            {{
                "question": "sub-question",
                "source_type": "text"
            }}
        ]

        User question:
        {question}
        """

            content = await hf_llm.generate(prompt)

            import json

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise ValueError(
                    f"Invalid decomposition response from LLM: {content}"
                )
rag_router = Router()