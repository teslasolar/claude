# 📡 KONOMI API Reference

Complete API documentation for REST and WebSocket endpoints.

## REST API (Port 3001)

Base URL: `http://localhost:3001`

### System Endpoints

#### `GET /`
Root endpoint with system information

**Response:**
```json
{
  "system": "KONOMI REST API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {...}
}
```

#### `GET /health`
System health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1699123456.789,
  "components": {
    "evgpu": "ok",
    "llm": "ok",
    "block_arrays": "5 active",
    "cubes": "10 active"
  }
}
```

#### `GET /stats`
Comprehensive system statistics

**Response:**
```json
{
  "system": "KONOMI",
  "uptime_seconds": 3600.5,
  "operations": 1250,
  "components": {
    "evgpu": {...},
    "block_arrays": 5,
    "cubes": 10,
    "standalone_llms": 2
  },
  "computation": {
    "active_cubes": 1000,
    "active_llms": 50,
    "cube_nodes": 90,
    "messages_processed": 500
  }
}
```

### Template Management

#### `POST /template/create`
Create BlockArray template

**Request:**
```json
{
  "template_id": "t1",
  "dimensions": [100, 100, 100],
  "description": "100³ grid template"
}
```

**Response:**
```json
{
  "success": true,
  "template_id": "t1",
  "template": {
    "id": "t1",
    "config": {...},
    "created_at": 1699123456.789,
    "instances": []
  }
}
```

### Instance Management

#### `POST /instance/create`
Create BlockArray instance

**Request (from template):**
```json
{
  "template_id": "t1",
  "instance_name": "array1"
}
```

**Request (direct):**
```json
{
  "instance_name": "array1",
  "dimensions": [10, 10, 10]
}
```

**Response:**
```json
{
  "success": true,
  "instance_name": "array1",
  "dimensions": [10, 10, 10],
  "stats": {...}
}
```

#### `GET /instance/{name}`
Get instance information

**Response:**
```json
{
  "name": "array1",
  "stats": {
    "dimensions": [10, 10, 10],
    "active_cubes": 50,
    "active_llms": 5,
    "memory_mb": 25.5
  }
}
```

#### `GET /instances`
List all instances

**Response:**
```json
{
  "instances": ["array1", "array2", "array3"],
  "count": 3
}
```

#### `DELETE /instance/{name}`
Delete instance

**Response:**
```json
{
  "success": true,
  "message": "Instance 'array1' deleted"
}
```

### Value Operations

#### `GET /value`
Get cube value at coordinate

**Query Parameters:**
- `array_name` (string): Array identifier
- `x` (int): X coordinate
- `y` (int): Y coordinate
- `z` (int): Z coordinate

**Example:**
```
GET /value?array_name=array1&x=5&y=5&z=5
```

**Response:**
```json
{
  "array_name": "array1",
  "x": 5,
  "y": 5,
  "z": 5,
  "value": 2.5
}
```

#### `POST /value`
Set cube value at coordinate

**Request:**
```json
{
  "array_name": "array1",
  "x": 5,
  "y": 5,
  "z": 5,
  "value": 2.5
}
```

**Response:**
```json
{
  "success": true,
  "array_name": "array1",
  "coordinates": [5, 5, 5],
  "value": 2.5
}
```

### LLM Operations

#### `POST /llm/process`
Process text with LLM at coordinate

**Request:**
```json
{
  "array_name": "array1",
  "x": 0,
  "y": 0,
  "z": 0,
  "text": "Hello Konomi"
}
```

**Response:**
```json
{
  "success": true,
  "array_name": "array1",
  "coordinates": [0, 0, 0],
  "input": "Hello Konomi",
  "output": "[Hello Konomi]→a1b2c3d4"
}
```

#### `POST /llm/interlock`
Face interlock operation (1M cubes)

**Request:**
```json
{
  "array_name": "array1",
  "face": "top",
  "operation": "activate"
}
```

**Valid Faces:**
- `top`, `bottom`, `north`, `south`, `east`, `west`

**Valid Operations:**
- `activate` - Set all face cubes to 1.0
- `clear` - Set all face cubes to 0.0
- `process` - Run LLM on face cubes (limited sample)

**Response:**
```json
{
  "success": true,
  "array_name": "array1",
  "face": "top",
  "operation": "activate",
  "cubes_affected": 10000
}
```

### Maintenance

#### `POST /optimize`
Run memory optimization

**Response:**
```json
{
  "success": true,
  "message": "Memory optimization complete"
}
```

---

## WebSocket API (Port 3002)

Connection URL: `ws://localhost:3002`

### Connection Flow

1. Connect to WebSocket
2. Receive welcome message
3. Send commands as JSON
4. Receive responses as JSON

### Message Format

**Request:**
```json
{
  "action": "command_name",
  "param1": "value1",
  "param2": "value2"
}
```

**Response:**
```json
{
  "action": "command_name",
  "success": true,
  "result": {...}
}
```

### Commands

#### `initialize`
Create or get cube

**Request:**
```json
{
  "action": "initialize",
  "cube_id": "c1",
  "seed": 42
}
```

**Response:**
```json
{
  "action": "initialize",
  "success": true,
  "cube_id": "c1",
  "info": {
    "cube_id": "c1",
    "vertices": 8,
    "total_nodes": 9,
    "edges": 32,
    "state": "Idle"
  }
}
```

#### `process`
Process text at vertex

**Request:**
```json
{
  "action": "process",
  "cube_id": "c1",
  "vertex": "NEU",
  "text": "Hello from NEU"
}
```

**Vertices:**
- `NEU`, `NED`, `NWU`, `NWD` (North)
- `SEU`, `SED`, `SWU`, `SWD` (South)

**Response:**
```json
{
  "action": "process",
  "success": true,
  "cube_id": "c1",
  "vertex": "NEU",
  "input": "Hello from NEU",
  "output": "[Hello from NEU]→x1y2z3"
}
```

#### `process_central`
Process at central node

**Request:**
```json
{
  "action": "process_central",
  "cube_id": "c1",
  "text": "Central processing"
}
```

**Response:**
```json
{
  "action": "process_central",
  "success": true,
  "cube_id": "c1",
  "output": "[Central processing]→a1b2c3"
}
```

#### `connect`
Create connection between vertices

**Request:**
```json
{
  "action": "connect",
  "cube_id": "c1",
  "source": "NEU",
  "target": "SWD"
}
```

**Response:**
```json
{
  "action": "connect",
  "success": true,
  "cube_id": "c1",
  "source": "NEU",
  "target": "SWD"
}
```

#### `connect_diagonals`
Connect all space diagonals

**Request:**
```json
{
  "action": "connect_diagonals",
  "cube_id": "c1"
}
```

**Response:**
```json
{
  "action": "connect_diagonals",
  "success": true,
  "cube_id": "c1",
  "info": {...}
}
```

#### `send_message`
Send message between vertices

**Request:**
```json
{
  "action": "send_message",
  "cube_id": "c1",
  "source": "NEU",
  "target": "CENTRAL",
  "message": "Test message"
}
```

**Response:**
```json
{
  "action": "send_message",
  "success": true,
  "cube_id": "c1",
  "from": "NEU",
  "to": "CENTRAL",
  "message": "Test message"
}
```

#### `get_messages`
Get messages for vertex

**Request:**
```json
{
  "action": "get_messages",
  "cube_id": "c1",
  "vertex": "CENTRAL"
}
```

**Response:**
```json
{
  "action": "get_messages",
  "success": true,
  "cube_id": "c1",
  "vertex": "CENTRAL",
  "messages": ["NEU→Test message"],
  "count": 1
}
```

#### `execute`
Execute full PackML cycle

**Request:**
```json
{
  "action": "execute",
  "cube_id": "c1",
  "input": "Cycle input"
}
```

**Response:**
```json
{
  "action": "execute",
  "success": true,
  "cube_id": "c1",
  "state": "Idle",
  "results": {
    "NEU": "[Cycle input]→...",
    "NED": "[Cycle input]→...",
    ...,
    "CENTRAL": "[Cycle input]→..."
  }
}
```

#### `status`
Get cube status

**Request (specific cube):**
```json
{
  "action": "status",
  "cube_id": "c1"
}
```

**Request (system-wide):**
```json
{
  "action": "status"
}
```

**Response (specific cube):**
```json
{
  "action": "status",
  "success": true,
  "cube_id": "c1",
  "info": {...},
  "vertices": {
    "NEU": {
      "llm_stats": {...},
      "connections": ["NWU", "SEU", "CENTRAL"],
      "messages": 0
    },
    ...
  }
}
```

**Response (system-wide):**
```json
{
  "action": "status",
  "success": true,
  "system": {...},
  "cubes": ["c1", "c2", "c3"]
}
```

#### `list_cubes`
List all cubes

**Request:**
```json
{
  "action": "list_cubes"
}
```

**Response:**
```json
{
  "action": "list_cubes",
  "success": true,
  "cubes": {
    "c1": {...},
    "c2": {...}
  },
  "count": 2
}
```

### Error Handling

**Error Response:**
```json
{
  "action": "command_name",
  "success": false,
  "error": "Error description"
}
```

**Common Errors:**
- `Unknown action` - Invalid command
- `Cube not found` - Invalid cube_id
- `Missing required fields` - Incomplete request
- `Invalid JSON` - Malformed request

---

## Client Examples

### Python REST Client

```python
import requests

base_url = "http://localhost:3001"

# Create instance
response = requests.post(f"{base_url}/instance/create", json={
    "instance_name": "test",
    "dimensions": [10, 10, 10]
})

# Set value
requests.post(f"{base_url}/value", json={
    "array_name": "test",
    "x": 5, "y": 5, "z": 5,
    "value": 2.5
})

# Get value
response = requests.get(f"{base_url}/value", params={
    "array_name": "test",
    "x": 5, "y": 5, "z": 5
})
print(response.json())
```

### Python WebSocket Client

```python
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:3002') as ws:
        # Initialize
        await ws.send(json.dumps({
            "action": "initialize",
            "cube_id": "test"
        }))

        response = json.loads(await ws.recv())
        print(response)

        # Process
        await ws.send(json.dumps({
            "action": "process",
            "cube_id": "test",
            "vertex": "NEU",
            "text": "Hello"
        }))

        response = json.loads(await ws.recv())
        print(response)

asyncio.run(test())
```

### JavaScript WebSocket Client

```javascript
const ws = new WebSocket('ws://localhost:3002');

ws.onopen = () => {
    console.log('Connected');

    // Initialize cube
    ws.send(JSON.stringify({
        action: 'initialize',
        cube_id: 'js_cube'
    }));
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('Response:', response);

    if (response.type === 'welcome') {
        // Send process command
        ws.send(JSON.stringify({
            action: 'process',
            cube_id: 'js_cube',
            vertex: 'NEU',
            text: 'Hello from JavaScript'
        }));
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

### cURL Examples

```bash
# Health check
curl http://localhost:3001/health

# Create instance
curl -X POST http://localhost:3001/instance/create \
  -H "Content-Type: application/json" \
  -d '{"instance_name":"curl_test","dimensions":[10,10,10]}'

# Set value
curl -X POST http://localhost:3001/value \
  -H "Content-Type: application/json" \
  -d '{"array_name":"curl_test","x":5,"y":5,"z":5,"value":2.5}'

# Get value
curl "http://localhost:3001/value?array_name=curl_test&x=5&y=5&z=5"

# LLM process
curl -X POST http://localhost:3001/llm/process \
  -H "Content-Type: application/json" \
  -d '{"array_name":"curl_test","x":0,"y":0,"z":0,"text":"Hello"}'

# Stats
curl http://localhost:3001/stats
```

---

## Rate Limits & Performance

- **REST API**: No rate limits (local deployment)
- **WebSocket**: No connection limits
- **LLM Processing**: ~0.1s per request
- **Face Interlock**: <1s for 10,000 cubes
- **Concurrent Requests**: Limited by CPU cores

## Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad Request (invalid params) |
| 404 | Not Found (instance/cube) |
| 500 | Internal Server Error |

---

Built for the KONOMI SYSTEM 🧬
