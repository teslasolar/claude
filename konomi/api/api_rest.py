"""
📡 KONOMI REST API
FastAPI server for BlockArray operations
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Tuple
import uvicorn
from base_template import KonomiSystem
import asyncio

# Initialize FastAPI app
app = FastAPI(
    title="KONOMI REST API",
    description="BlockArray operations - 1000³ computational grid",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global KONOMI System instance
konomi = KonomiSystem()


# Request/Response Models
class TemplateCreateRequest(BaseModel):
    template_id: str
    dimensions: Tuple[int, int, int] = (10, 10, 10)
    description: Optional[str] = None


class InstanceCreateRequest(BaseModel):
    template_id: Optional[str] = None
    instance_name: str
    dimensions: Tuple[int, int, int] = (10, 10, 10)


class ValueSetRequest(BaseModel):
    array_name: str
    x: int
    y: int
    z: int
    value: float


class LLMProcessRequest(BaseModel):
    array_name: str
    x: int
    y: int
    z: int
    text: str


class InterlockRequest(BaseModel):
    array_name: str
    face: str  # 'top', 'bottom', 'north', 'south', 'east', 'west'
    operation: str = "activate"  # 'activate', 'clear', 'process'


# API Endpoints

@app.get("/")
async def root():
    """API root - system info"""
    return {
        "system": "KONOMI REST API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "templates": "/template/create",
            "instances": "/instance/create",
            "values": "/value",
            "llm": "/llm/process",
            "interlock": "/llm/interlock",
            "stats": "/stats",
            "health": "/health"
        }
    }


@app.post("/template/create")
async def create_template(request: TemplateCreateRequest):
    """
    Create BlockArray template

    Example:
        POST /template/create
        {
            "template_id": "t1",
            "dimensions": [100, 100, 100],
            "description": "100³ grid"
        }
    """
    config = {
        "dimensions": request.dimensions,
        "description": request.description
    }

    template = konomi.create_template(request.template_id, config)

    return {
        "success": True,
        "template_id": request.template_id,
        "template": template
    }


@app.post("/instance/create")
async def create_instance(request: InstanceCreateRequest):
    """
    Create BlockArray instance

    Example:
        POST /instance/create
        {
            "instance_name": "array1",
            "dimensions": [10, 10, 10]
        }
    """
    if request.template_id:
        # Create from template
        ba = konomi.instantiate_template(request.template_id, request.instance_name)
        if not ba:
            raise HTTPException(status_code=404, detail="Template not found")
    else:
        # Create directly
        ba = konomi.create_block_array(request.instance_name, request.dimensions)

    return {
        "success": True,
        "instance_name": request.instance_name,
        "dimensions": ba.dimensions,
        "stats": ba.stats()
    }


@app.get("/instance/{name}")
async def get_instance(name: str):
    """Get BlockArray instance info"""
    ba = konomi.get_block_array(name)
    if not ba:
        raise HTTPException(status_code=404, detail="Instance not found")

    return {
        "name": name,
        "stats": ba.stats()
    }


@app.get("/instances")
async def list_instances():
    """List all BlockArray instances"""
    return {
        "instances": list(konomi.block_arrays.keys()),
        "count": len(konomi.block_arrays)
    }


@app.get("/value")
async def get_value(array_name: str, x: int, y: int, z: int):
    """
    Get cube value at coordinate

    Example:
        GET /value?array_name=array1&x=5&y=5&z=5
    """
    ba = konomi.get_block_array(array_name)
    if not ba:
        raise HTTPException(status_code=404, detail="Array not found")

    value = ba.get(x, y, z)
    if value is None:
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    return {
        "array_name": array_name,
        "x": x,
        "y": y,
        "z": z,
        "value": value
    }


@app.post("/value")
async def set_value(request: ValueSetRequest):
    """
    Set cube value at coordinate

    Example:
        POST /value
        {
            "array_name": "array1",
            "x": 5,
            "y": 5,
            "z": 5,
            "value": 2.5
        }
    """
    ba = konomi.get_block_array(request.array_name)
    if not ba:
        raise HTTPException(status_code=404, detail="Array not found")

    success = ba.set(request.x, request.y, request.z, request.value)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    return {
        "success": True,
        "array_name": request.array_name,
        "coordinates": [request.x, request.y, request.z],
        "value": request.value
    }


@app.post("/llm/process")
async def llm_process(request: LLMProcessRequest):
    """
    Process text with LLM at coordinate

    Example:
        POST /llm/process
        {
            "array_name": "array1",
            "x": 0,
            "y": 0,
            "z": 0,
            "text": "Hello Konomi"
        }
    """
    ba = konomi.get_block_array(request.array_name)
    if not ba:
        raise HTTPException(status_code=404, detail="Array not found")

    result = await ba.process_at(request.x, request.y, request.z, request.text)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    return {
        "success": True,
        "array_name": request.array_name,
        "coordinates": [request.x, request.y, request.z],
        "input": request.text,
        "output": result
    }


@app.post("/llm/interlock")
async def llm_interlock(request: InterlockRequest):
    """
    Face interlock operation - process 1M cubes at once

    Example:
        POST /llm/interlock
        {
            "array_name": "array1",
            "face": "top",
            "operation": "activate"
        }
    """
    ba = konomi.get_block_array(request.array_name)
    if not ba:
        raise HTTPException(status_code=404, detail="Array not found")

    valid_faces = ['top', 'bottom', 'north', 'south', 'east', 'west']
    if request.face not in valid_faces:
        raise HTTPException(status_code=400, detail=f"Invalid face. Must be one of: {valid_faces}")

    valid_ops = ['activate', 'clear', 'process']
    if request.operation not in valid_ops:
        raise HTTPException(status_code=400, detail=f"Invalid operation. Must be one of: {valid_ops}")

    count = await konomi.interlock_operation(request.array_name, request.face, request.operation)

    return {
        "success": True,
        "array_name": request.array_name,
        "face": request.face,
        "operation": request.operation,
        "cubes_affected": count
    }


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return konomi.get_system_stats()


@app.get("/health")
async def health_check():
    """System health check"""
    health = await konomi.health_check()
    return health


@app.post("/optimize")
async def optimize():
    """Run memory optimization"""
    konomi.optimize_memory()
    return {
        "success": True,
        "message": "Memory optimization complete"
    }


@app.delete("/instance/{name}")
async def delete_instance(name: str):
    """Delete BlockArray instance"""
    if name not in konomi.block_arrays:
        raise HTTPException(status_code=404, detail="Instance not found")

    del konomi.block_arrays[name]
    return {
        "success": True,
        "message": f"Instance '{name}' deleted"
    }


def run_server(host: str = "0.0.0.0", port: int = 3001):
    """Run the REST API server"""
    print(f"""
    🧬 KONOMI REST API Server
    ═══════════════════════════════════════
    📡 Listening on: http://{host}:{port}
    📚 API Docs: http://{host}:{port}/docs
    🔍 Health: http://{host}:{port}/health
    ═══════════════════════════════════════
    """)

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_server()
