from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from PIL import Image
import pytesseract
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4
from src.database import Database
from src.llm_config import  llm_embedding

db =Database() 
class Extractor:
    def extract_text(self, file_content: bytes, filename: str) -> str:

        extension = Path(filename).suffix.lower()

        if extension == ".txt":
            return file_content.decode("utf-8")

        if extension == ".pdf":
            pdf = PdfReader(BytesIO(file_content))

            text = ""

            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            return text

        if extension in [".png", ".jpg", ".jpeg"]:
            image = Image.open(BytesIO(file_content))

            text = pytesseract.image_to_string(image)

            return text

        raise ValueError("Unsupported file type")


    def create_chunks(self, text:str):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap = 50
        )
        chunks = splitter.split_text(text)
        return chunks
    
    async def create_embeddings(self,chunks:list[str]):
        embeddings = await llm_embedding.embeddings.aembed_documents(chunks)
        return embeddings
    
    async def create_query_embeddings(self , question:str):
        embedding = await  llm_embedding.embeddings.aembed_query(question )
        return embedding



    async def save_document(self,filename:str,chunks:list[str], embeddings: list[list[float]] ):
        existing_document = await db.get_document_by_filename(filename)
        if existing_document:
            document_id = existing_document["document_id"]
            await db.delete_chunks(document_id)
        else:
           document_id = str(uuid4())
        documents =[]
        for index , chunk in enumerate(chunks):
            documents.append({
                "document_id":document_id,
                "file_name":filename,
                "chunk_index":index,
                "text":chunk,
                "embedding":embeddings[index]
            })
        if documents:
            await db.save_chunks(documents)
        return document_id

    


extractor = Extractor()