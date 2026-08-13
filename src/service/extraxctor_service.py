from io import BytesIO
from pathlib import Path
from pypdf import PdfReader
from PIL import Image
import pytesseract
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4
from src.database import Database
from src.llm_config import  llm_embedding
from src.service.audio_transcribe import audio_extract
db =Database() 
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
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
        if extension in [".mp3", ".wav", ".m4a", ".ogg", ".webm"]:
             return audio_extract.extract_audio_text(file_content, filename)
        
        raise ValueError("Unsupported file type")

    def create_audio_chunk(self,audio_segments,document_id,filename):
        chunks = []
        for index ,segment in enumerate(audio_segments):
            chunks.append({
                "document_id":document_id,
                "file_name":filename,
                "chunk_index":index,
                "text":segment["text"],
                "source_type": "audio",
                "metadata": {
                "start_time":segment["start_time"],
                "end_time":segment["end_time"]
                }
            })
        return chunks

    def create_chunks(self, text:str,document_id: str, filename:str , source_type:str):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap = 50
        )
        chunked_text = splitter.split_text(text)
        chunks = []
        for index , chunk_text in enumerate(chunked_text):
            chunks.append({
                "document_id":document_id,
                "file_name":filename,
                "chunk_index":index,
                "text":chunk_text,
                "source_type":source_type,
                "metadata":{}
            })
        return chunks
    
    async def create_embeddings(self,chunks:list[str]):
        print(chunks)
        embeddings = await llm_embedding.embeddings.aembed_documents(chunks)
       
        return embeddings
    
    async def create_query_embeddings(self , question:str):
        embedding = await  llm_embedding.embeddings.aembed_query(question )
        return embedding



    async def save_document(
        self,
        filename: str,
        chunks: list[dict],
        embeddings: list[list[float]]
       
    ):
        existing_document = await db.get_document_by_filename(filename)

        if existing_document:
            document_id = existing_document["document_id"]
            await db.delete_chunks(document_id)
        else:
            document_id = chunks[0]["document_id"]

        documents = []
        for index, chunk in enumerate(chunks):
            if isinstance(chunk, dict):
                text = chunk["text"] 
                source_type = chunk.get("source_type")
                metadata = chunk.get("metadata", {})
            else:
                 text= chunk
                 source_type = "text",
                 metadata ={}   

            document = {
            "document_id": document_id,
            "file_name": filename,
            "chunk_index": index,
            "text":text,
            "source_type":source_type,
            "metadata":metadata,
            "embedding": embeddings[index]
              }
            documents.append(document)

        if documents:
            await db.save_chunks(chunks)

        return document_id

        


extractor = Extractor()