from fastapi import APIRouter,UploadFile,File,HTTPException, Depends
from src.service.extraxctor_service import extractor 
from src.dependencies import get_current_user


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
        ".jpeg"
    }

    filename = file.filename or ""

    extension = filename.lower().rsplit(".", 1)[-1]
    print(extension)
    if f".{extension}" not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    try:
        content = await file.read()

        text = extractor.extract_text(
            file_content=content,
            filename=filename
        )
        chunks = extractor.create_chunks(text)

        embeddings = await extractor.create_embeddings(chunks)

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