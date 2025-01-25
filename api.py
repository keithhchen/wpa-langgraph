from fastapi import FastAPI, HTTPException
import logging
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
from src import run_workflow, graph  # Import from src package
from langchain_core.runnables.graph import MermaidDrawMethod
import traceback 
import time
import os

app = FastAPI()

from typing import Union

class Metadata(BaseModel):
    title: str | None = None
    source: str | None = None
    link: str | None = None
    description: str | None = None
    author: str | None = None

class SourceRequest(BaseModel):
    source: Union[str, dict]
    metadata: Metadata | None = None

    def get_source(self) -> str:
        if isinstance(self.source, dict):
            return str(self.source)
        return self.source

logger = logging.getLogger("uvicorn")

@app.post("/process")
def process_source(request: SourceRequest, plain: bool = False):
    logger.info("Processing new request")
    if request.metadata:
        logger.info(f"Metadata: {request.source}")
        logger.info(f"Metadata: {request.metadata}")

    try:
        start_time = time.time()
        # Pass both source and metadata to run_workflow
        result = run_workflow(
            input_message=request.get_source(),
            metadata=request.metadata.dict() if request.metadata else None
        )
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        
        if plain:
            return PlainTextResponse(result["final_article"])
            
        return {
            "elapsed_time": elapsed_time,
            "title": result["outline"]["title"],
            "full_text": result["final_article"],
            "paragraphs": result["paragraphs"],
        }
    except Exception as e:
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "type": str(type(e).__name__)
        }
        logger.error(error_details)
        raise HTTPException(status_code=500, detail=error_details)

@app.get("/graph")
async def get_graph():
    try:
        # Create a unique filename using timestamp
        filename = f"graph_{int(time.time())}.png"
        
        # Generate the graph
        graph.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
            output_file_path=filename
        )
        
        # Return the file and clean up afterwards
        return FileResponse(
            filename,
            media_type="image/png",
            filename="workflow_graph.png",
            background=cleanup_file(filename)
        )
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(traceback.format_exc()))

def cleanup_file(filename: str):
    """Background task to remove the temporary file after it's sent"""
    async def cleanup():
        try:
            os.remove(filename)
        except Exception:
            pass
    return cleanup

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="localhost", port=8000, reload=True)