"""
📡 KONOMI WebSocket Server
Real-time Cube operations via WebSocket
"""
import asyncio
import json
import websockets
from websockets.server import serve
from typing import Dict, Set
from base_template import KonomiSystem
from cube import Cube
import traceback

# Global KONOMI System instance
konomi = KonomiSystem()

# Connected clients
connected_clients: Set[websockets.WebSocketServerProtocol] = set()


async def handle_message(websocket, message: str) -> dict:
    """
    Handle incoming WebSocket message

    Message format:
    {
        "action": "initialize" | "process" | "connect" | "status" | "execute",
        "cube_id": "c1",
        "vertex": "NEU",
        "text": "...",
        ...
    }
    """
    try:
        data = json.loads(message)
        action = data.get("action")

        if action == "initialize":
            # Create or get cube
            cube_id = data.get("cube_id", "default")
            seed = data.get("seed")

            if cube_id in konomi.cubes:
                cube = konomi.get_cube(cube_id)
            else:
                cube = konomi.create_cube(cube_id, seed)

            return {
                "action": "initialize",
                "success": True,
                "cube_id": cube_id,
                "info": cube.cube_info()
            }

        elif action == "process":
            # Process text at vertex
            cube_id = data.get("cube_id")
            vertex = data.get("vertex")
            text = data.get("text")

            if not all([cube_id, vertex, text]):
                return {
                    "action": "process",
                    "success": False,
                    "error": "Missing required fields: cube_id, vertex, text"
                }

            cube = konomi.get_cube(cube_id)
            if not cube:
                return {
                    "action": "process",
                    "success": False,
                    "error": f"Cube '{cube_id}' not found"
                }

            result = await cube.process_vertex(vertex, text)

            return {
                "action": "process",
                "success": True,
                "cube_id": cube_id,
                "vertex": vertex,
                "input": text,
                "output": result
            }

        elif action == "process_central":
            # Process at central node
            cube_id = data.get("cube_id")
            text = data.get("text")

            cube = konomi.get_cube(cube_id)
            if not cube:
                return {
                    "action": "process_central",
                    "success": False,
                    "error": f"Cube '{cube_id}' not found"
                }

            result = await cube.process_central(text)

            return {
                "action": "process_central",
                "success": True,
                "cube_id": cube_id,
                "output": result
            }

        elif action == "connect":
            # Create connection between vertices
            cube_id = data.get("cube_id")
            source = data.get("source")
            target = data.get("target")

            cube = konomi.get_cube(cube_id)
            if not cube:
                return {
                    "action": "connect",
                    "success": False,
                    "error": f"Cube '{cube_id}' not found"
                }

            success = cube.connect(source, target)

            return {
                "action": "connect",
                "success": success,
                "cube_id": cube_id,
                "source": source,
                "target": target
            }

        elif action == "connect_diagonals":
            # Connect all diagonals
            cube_id = data.get("cube_id")

            cube = konomi.get_cube(cube_id)
            if not cube:
                return {
                    "action": "connect_diagonals",
                    "success": False,
                    "error": f"Cube '{cube_id}' not found"
                }

            cube.connect_diagonals()

            return {
                "action": "connect_diagonals",
                "success": True,
                "cube_id": cube_id,
                "info": cube.cube_info()
            }

        elif action == "send_message":
            # Send message between vertices
            cube_id = data.get("cube_id")
            source = data.get("source")
            target = data.get("target")
            message = data.get("message")

            cube = konomi.get_cube(cube_id)
            if not cube:
                return {
                    "action": "send_message",
                    "success": False,
                    "error": f"Cube '{cube_id}' not found"
                }

            success = await cube.send_message(source, target, message)

            return {
                "action": "send_message",
                "success": success,
                "cube_id": cube_id,
                "from": source,
                "to": target,
                "message": message
            }

        elif action == "get_messages":
            # Get messages for vertex
            cube_id = data.get("cube_id")
            vertex = data.get("vertex")

            cube = konomi.get_cube(cube_id)
            if not cube:
                return {
                    "action": "get_messages",
                    "success": False,
                    "error": f"Cube '{cube_id}' not found"
                }

            messages = cube.get_messages(vertex)

            return {
                "action": "get_messages",
                "success": True,
                "cube_id": cube_id,
                "vertex": vertex,
                "messages": messages,
                "count": len(messages)
            }

        elif action == "execute":
            # Execute full cycle
            cube_id = data.get("cube_id")
            input_data = data.get("input", "")

            cube = konomi.get_cube(cube_id)
            if not cube:
                return {
                    "action": "execute",
                    "success": False,
                    "error": f"Cube '{cube_id}' not found"
                }

            results = await cube.execute_cycle(input_data)

            return {
                "action": "execute",
                "success": True,
                "cube_id": cube_id,
                "state": cube.state.value,
                "results": results
            }

        elif action == "status":
            # Get cube status
            cube_id = data.get("cube_id")

            if cube_id:
                cube = konomi.get_cube(cube_id)
                if not cube:
                    return {
                        "action": "status",
                        "success": False,
                        "error": f"Cube '{cube_id}' not found"
                    }

                # Get all vertex states
                vertex_states = {}
                for vertex in cube.V + ['CENTRAL']:
                    llm = cube.get_llm(vertex)
                    vertex_states[vertex] = {
                        "llm_stats": llm.stats() if llm else None,
                        "connections": cube.get_connections(vertex),
                        "messages": len(cube.get_messages(vertex))
                    }

                return {
                    "action": "status",
                    "success": True,
                    "cube_id": cube_id,
                    "info": cube.cube_info(),
                    "vertices": vertex_states
                }
            else:
                # System-wide status
                return {
                    "action": "status",
                    "success": True,
                    "system": konomi.get_system_stats(),
                    "cubes": list(konomi.cubes.keys())
                }

        elif action == "list_cubes":
            # List all cubes
            cubes_info = {
                cube_id: cube.cube_info()
                for cube_id, cube in konomi.cubes.items()
            }

            return {
                "action": "list_cubes",
                "success": True,
                "cubes": cubes_info,
                "count": len(cubes_info)
            }

        else:
            return {
                "action": action,
                "success": False,
                "error": f"Unknown action: {action}"
            }

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Invalid JSON"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Internal error: {str(e)}",
            "traceback": traceback.format_exc()
        }


async def handler(websocket):
    """WebSocket connection handler"""
    # Register client
    connected_clients.add(websocket)
    client_id = id(websocket)

    try:
        print(f"🔌 Client {client_id} connected")

        # Send welcome message
        welcome = {
            "type": "welcome",
            "message": "Connected to KONOMI WebSocket Server",
            "system": "Cube Operations",
            "commands": [
                "initialize", "process", "process_central", "connect",
                "connect_diagonals", "send_message", "get_messages",
                "execute", "status", "list_cubes"
            ]
        }
        await websocket.send(json.dumps(welcome))

        # Message loop
        async for message in websocket:
            response = await handle_message(websocket, message)
            await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 Client {client_id} disconnected")
    except Exception as e:
        print(f"❌ Error with client {client_id}: {e}")
        traceback.print_exc()
    finally:
        # Unregister client
        connected_clients.discard(websocket)


async def broadcast(message: dict):
    """Broadcast message to all connected clients"""
    if connected_clients:
        message_str = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_str) for client in connected_clients],
            return_exceptions=True
        )


async def main(host: str = "0.0.0.0", port: int = 3002):
    """Run WebSocket server"""
    print(f"""
    🧬 KONOMI WebSocket Server
    ═══════════════════════════════════════
    📡 Listening on: ws://{host}:{port}
    🎲 Cube Operations: Real-time
    ═══════════════════════════════════════
    """)

    async with serve(handler, host, port):
        await asyncio.Future()  # Run forever


def run_server(host: str = "0.0.0.0", port: int = 3002):
    """Entry point for WebSocket server"""
    asyncio.run(main(host, port))


if __name__ == "__main__":
    run_server()
