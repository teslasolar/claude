"""
🎲 Cube - 9-node system
8 vertices + 1 central node with LLM processing
Vertices: NEU, NED, NWU, NWD, SEU, SED, SWU, SWD
"""
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
from femtollm import FemtoLLM
from enum import Enum


class VertexPosition(Enum):
    """Vertex position enumeration"""
    NEU = "NEU"  # North-East-Up
    NED = "NED"  # North-East-Down
    NWU = "NWU"  # North-West-Up
    NWD = "NWD"  # North-West-Down
    SEU = "SEU"  # South-East-Up
    SED = "SED"  # South-East-Down
    SWU = "SWU"  # South-West-Up
    SWD = "SWD"  # South-West-Down
    CENTRAL = "CENTRAL"  # Central node


class MachineState(Enum):
    """PackML machine states"""
    IDLE = "Idle"
    STARTING = "Starting"
    EXECUTE = "Execute"
    COMPLETE = "Complete"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    ABORTING = "Aborting"
    ABORTED = "Aborted"
    CLEARING = "Clearing"


class Cube:
    """
    Cube: 9-node computational system
    - 8 vertices (corners of cube)
    - 1 central node (center of cube)
    - Each node has dedicated FemtoLLM
    - Nodes can message each other via edges
    - State machine: PackML states
    """

    # Class variable: vertex positions
    V = ['NEU', 'NED', 'NWU', 'NWD', 'SEU', 'SED', 'SWU', 'SWD']

    def __init__(self, cube_id: str, llm_seed: Optional[int] = None):
        """
        Initialize Cube

        Args:
            cube_id: Unique identifier for this cube
            llm_seed: Seed for LLM initialization
        """
        self.cube_id = cube_id
        self.llm_seed = llm_seed

        # Create LLM for each vertex
        self.vertices: Dict[str, FemtoLLM] = {
            vertex: FemtoLLM(seed=llm_seed + i if llm_seed else None)
            for i, vertex in enumerate(self.V)
        }

        # Central LLM
        self.central = FemtoLLM(seed=llm_seed + 8 if llm_seed else None)

        # Edge connections: source -> [targets]
        self.edges: Dict[str, List[str]] = defaultdict(list)

        # Initialize default adjacency (cube edges)
        self._initialize_topology()

        # State machine
        self.state = MachineState.IDLE
        self.state_history: List[Tuple[MachineState, float]] = []

        # Message queue for inter-node communication
        self.message_queue: Dict[str, List[str]] = defaultdict(list)

        # Processing statistics
        self.stats = {
            "messages_sent": 0,
            "messages_processed": 0,
            "state_transitions": 0
        }

    def _initialize_topology(self):
        """
        Initialize default cube topology
        Connects adjacent vertices along cube edges
        """
        # Define cube edges (12 edges total)
        edge_pairs = [
            # Top face (U)
            ('NEU', 'NWU'), ('NWU', 'SWU'), ('SWU', 'SEU'), ('SEU', 'NEU'),
            # Bottom face (D)
            ('NED', 'NWD'), ('NWD', 'SWD'), ('SWD', 'SED'), ('SED', 'NED'),
            # Vertical edges
            ('NEU', 'NED'), ('NWU', 'NWD'), ('SWU', 'SWD'), ('SEU', 'SED'),
        ]

        for v1, v2 in edge_pairs:
            self.connect(v1, v2)
            self.connect(v2, v1)  # Bidirectional

        # Connect all vertices to central
        for vertex in self.V:
            self.connect(vertex, 'CENTRAL')
            self.connect('CENTRAL', vertex)

    def connect(self, source: str, target: str) -> bool:
        """
        Create edge connection between nodes

        Args:
            source: Source node name
            target: Target node name

        Returns:
            True if successful
        """
        valid_nodes = set(self.V + ['CENTRAL'])

        if source not in valid_nodes or target not in valid_nodes:
            return False

        if target not in self.edges[source]:
            self.edges[source].append(target)

        return True

    def disconnect(self, source: str, target: str) -> bool:
        """Remove edge connection"""
        if source in self.edges and target in self.edges[source]:
            self.edges[source].remove(target)
            return True
        return False

    def get_connections(self, node: str) -> List[str]:
        """Get all outgoing connections from node"""
        return self.edges.get(node, [])

    def get_llm(self, node: str) -> Optional[FemtoLLM]:
        """Get LLM for specific node"""
        if node == 'CENTRAL':
            return self.central
        elif node in self.vertices:
            return self.vertices[node]
        return None

    async def process_vertex(self, vertex: str, text: str) -> Optional[str]:
        """
        Process text at specific vertex

        Args:
            vertex: Vertex name
            text: Input text

        Returns:
            Processed result or None
        """
        llm = self.get_llm(vertex)
        if llm is None:
            return None

        result = await llm.process(text)
        self.stats["messages_processed"] += 1

        return result

    async def process_central(self, text: str) -> str:
        """Process text at central node"""
        result = await self.central.process(text)
        self.stats["messages_processed"] += 1
        return result

    async def send_message(self, source: str, target: str, message: str) -> bool:
        """
        Send message from source to target

        Args:
            source: Source node
            target: Target node
            message: Message content

        Returns:
            True if message sent successfully
        """
        # Check if connection exists
        if target not in self.edges.get(source, []):
            return False

        # Add to target's message queue
        self.message_queue[target].append(f"{source}→{message}")
        self.stats["messages_sent"] += 1

        return True

    async def broadcast(self, source: str, message: str) -> int:
        """
        Broadcast message to all connected nodes

        Args:
            source: Source node
            message: Message content

        Returns:
            Number of nodes reached
        """
        targets = self.edges.get(source, [])
        count = 0

        for target in targets:
            if await self.send_message(source, target, message):
                count += 1

        return count

    def get_messages(self, node: str) -> List[str]:
        """Get all messages for node"""
        return self.message_queue.get(node, [])

    def clear_messages(self, node: str):
        """Clear message queue for node"""
        if node in self.message_queue:
            self.message_queue[node].clear()

    def set_state(self, new_state: MachineState):
        """
        Transition to new state

        Args:
            new_state: Target state
        """
        import time
        self.state_history.append((self.state, time.time()))
        self.state = new_state
        self.stats["state_transitions"] += 1

    async def execute_cycle(self, input_data: str) -> dict:
        """
        Execute full PackML cycle

        Args:
            input_data: Input for processing

        Returns:
            Results from all vertices
        """
        # State: IDLE → STARTING
        self.set_state(MachineState.STARTING)
        await asyncio.sleep(0.01)

        # State: STARTING → EXECUTE
        self.set_state(MachineState.EXECUTE)

        # Process at all vertices in parallel
        tasks = {}
        for vertex in self.V:
            tasks[vertex] = self.process_vertex(vertex, input_data)

        # Also process at central
        tasks['CENTRAL'] = self.process_central(input_data)

        # Gather results
        results = {}
        completed = await asyncio.gather(*tasks.values())

        for vertex, result in zip(tasks.keys(), completed):
            results[vertex] = result

        # State: EXECUTE → COMPLETE
        self.set_state(MachineState.COMPLETE)

        # State: COMPLETE → IDLE
        await asyncio.sleep(0.01)
        self.set_state(MachineState.IDLE)

        return results

    def get_diagonals(self) -> List[Tuple[str, str]]:
        """Get all diagonal connections (4 space diagonals)"""
        return [
            ('NEU', 'SWD'),
            ('NWU', 'SED'),
            ('NED', 'SWU'),
            ('NWD', 'SEU'),
        ]

    def connect_diagonals(self):
        """Connect all space diagonal vertices"""
        for v1, v2 in self.get_diagonals():
            self.connect(v1, v2)
            self.connect(v2, v1)

    def get_face_vertices(self, face: str) -> List[str]:
        """
        Get vertices on a specific face

        Args:
            face: 'north', 'south', 'east', 'west', 'up', 'down'

        Returns:
            List of vertex names
        """
        face_map = {
            'north': ['NEU', 'NED', 'NWU', 'NWD'],
            'south': ['SEU', 'SED', 'SWU', 'SWD'],
            'east': ['NEU', 'NED', 'SEU', 'SED'],
            'west': ['NWU', 'NWD', 'SWU', 'SWD'],
            'up': ['NEU', 'NWU', 'SEU', 'SWU'],
            'down': ['NED', 'NWD', 'SED', 'SWD'],
        }
        return face_map.get(face.lower(), [])

    def cube_info(self) -> dict:
        """Get cube information"""
        return {
            "cube_id": self.cube_id,
            "vertices": len(self.vertices),
            "central": "CENTRAL",
            "total_nodes": len(self.vertices) + 1,
            "edges": sum(len(targets) for targets in self.edges.values()),
            "state": self.state.value,
            "state_transitions": len(self.state_history),
            **self.stats
        }

    def __repr__(self) -> str:
        return f"Cube(id={self.cube_id}, nodes=9, state={self.state.value})"


if __name__ == "__main__":
    # Quick test
    print("🎲 Cube Test")

    cube = Cube(cube_id="test_cube", llm_seed=42)
    print(f"Created: {cube}")
    print(f"Info: {cube.cube_info()}")

    # Test processing
    async def test():
        # Process at vertex
        result = await cube.process_vertex('NEU', "Hello from NEU")
        print(f"NEU result: {result}")

        # Process at central
        result = await cube.process_central("Central processing")
        print(f"Central result: {result}")

        # Send message
        success = await cube.send_message('NEU', 'CENTRAL', "Test message")
        print(f"Message sent: {success}")

        messages = cube.get_messages('CENTRAL')
        print(f"Central messages: {messages}")

        # Execute full cycle
        results = await cube.execute_cycle("Cycle test")
        print(f"Cycle results: {len(results)} nodes processed")
        print(f"Final state: {cube.state.value}")

        # Test diagonals
        cube.connect_diagonals()
        print(f"Connections after diagonals: {cube.cube_info()['edges']}")

    asyncio.run(test())

    print("✓ Cube tests passed!")
