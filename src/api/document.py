from fastapi import APIRouter,UploadFile,File,HTTPException, Depends
from src.service.extraxctor_service import extractor 
from src.dependencies import get_current_user
from uuid import uuid4
from pathlib import Path


router  =APIRouter(
    prefix="/documents",
    tags=["Document"],
    dependencies=[Depends(get_current_user)]
    
)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    allowed_extensions = {
        ".pdf",
        ".txt",
        ".png",
        ".jpg",
        ".jpeg",
        
    }
    audio_extensions = {
        ".mp3", ".wav", ".m4a", ".ogg", ".webm"
    }
    filename = file.filename or ""

    extension = Path(filename).suffix.lower()
    print("Filename:", filename)
    print("Extension:", extension)
    if extension not in allowed_extensions and extension not in audio_extensions:

        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    try:
        content = await file.read()
        if extension in audio_extensions:
            print(extension)

            audio_segments = extractor.extract_text( file_content=content,filename=filename)
            document_id = str(uuid4())

            chunks =  extractor.create_audio_chunk(audio_segments=audio_segments,document_id=document_id,filename=filename )
        else:
            print(extension)
            text = extractor.extract_text(
                file_content=content,
                filename=filename
            )
           
            chunks = extractor.create_chunks(text)
        texts = [
        chunk["text"] if isinstance(chunk, dict) else chunk
        for chunk in chunks
         ]

        embeddings = await extractor.create_embeddings(texts)

        document_id = await extractor.save_document(
            filename= filename,
            chunks = chunks,
            embeddings = embeddings
        )
        return {
            "document_id": document_id,
            "filename": filename,
            "message": "Document processed successfully",
            "chunks_count": len(chunks)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(error)}"
        )