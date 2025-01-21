from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from graph import run_workflow, graph
from langchain_core.runnables.graph import MermaidDrawMethod
import traceback 
import time
import os

app = FastAPI()

class SourceRequest(BaseModel):
    source: str

@app.post("/process")
async def process_source(request: SourceRequest):
    try:
        start_time = time.time()
        result = run_workflow(request.source)
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        
        return {
            "elapsed_time": elapsed_time,
            "article": result["final_article"],
            "paragraphs": result["paragraphs"],
        }
    except Exception as e:
        print(e)
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "type": str(type(e).__name__)
        }
        print("Error details:", error_details)
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