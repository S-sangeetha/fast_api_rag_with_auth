from src.llm_config import llm_embedding

class Router:

    async def classify_question(self, question: str) -> str:

        question_lower = question.lower()

        audio_keywords = [
            "recording",
            "audio",
            "voice",
            "said",
            "says",
            "sound",
            "heard"
        ]

        image_keywords = [
            "image",
            "picture",
            "photo",
            "chart",
            "diagram",
            "shown",
            "visible"
        ]

        if any(word in question_lower for word in audio_keywords):
            return "audio"

        if any(word in question_lower for word in image_keywords):
            return "image"

        return "text"
    # async def classify_question(self, question: str):

    #     prompt = f"""
    #     Determine which source types are needed to answer this question.

    #     Available source types:
    #     - text
    #     - image
    #     - audio
    #     - multi

    #     Question:
    #     {question}

    #     Return only one:
    #     text
    #     image
    #     audio
    #     multi
    #     """

    #     response = await llm_embedding.llm.ainvoke(prompt)
    #     source_type = "".join(
    #         block["text"]
    #         for block in response.content
    #         if isinstance(block, dict)
    #         and block.get("type") == "text"
    #     ).strip().lower()

    #     allowed_types = {
    #         "text",
    #         "image",
    #         "audio",
    #         "multi"
    #     }

    #     if source_type not in allowed_types:
    #         source_type = "multi"
        
    #     return source_type

rag_router = Router()