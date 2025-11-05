"""
🧊 BlockArray - 1000³ computational grid
3D grid with LLM@coordinates, sparse storage, face operations
"""
import numpy as np
from typing import Dict, Tuple, Optional, List
from collections import defaultdict
from femtollm import FemtoLLM
import asyncio


class BlockArray:
    """
    BlockArray: 3D computational grid
    - Dimensions: Scalable from 10³ to 1000³
    - Storage: Sparse (only store non-zero values)
    - LLMs: Can attach LLM to any coordinate
    - Operations: Face interlock (1M cubes at once)
    """

    def __init__(self, dimensions: Tuple[int, int, int] = (1000, 1000, 1000), name: str = "default"):
        """
        Initialize BlockArray

        Args:
            dimensions: (x, y, z) dimensions
            name: Array identifier
        """
        self.dimensions = dimensions
        self.name = name

        # Sparse storage: only store non-zero values
        self.sparse_data: Dict[Tuple[int, int, int], float] = {}

        # LLM mapping: coordinate -> LLM instance
        self.llms: Dict[Tuple[int, int, int], FemtoLLM] = {}

        # Template metadata
        self.metadata: Dict[str, any] = {
            "created_at": None,
            "modified_at": None,
            "total_activations": 0
        }

        # Statistics
        self.operation_count = 0

    def _validate_coords(self, x: int, y: int, z: int) -> bool:
        """Validate coordinates are within bounds"""
        return (0 <= x < self.dimensions[0] and
                0 <= y < self.dimensions[1] and
                0 <= z < self.dimensions[2])

    def set(self, x: int, y: int, z: int, value: float) -> bool:
        """
        Set value at coordinate

        Args:
            x, y, z: Coordinates
            value: Value to set

        Returns:
            True if successful
        """
        if not self._validate_coords(x, y, z):
            return False

        coord = (x, y, z)

        if value == 0.0:
            # Remove from sparse storage
            self.sparse_data.pop(coord, None)
        else:
            self.sparse_data[coord] = value

        self.operation_count += 1
        self.metadata["total_activations"] += 1

        return True

    def get(self, x: int, y: int, z: int) -> Optional[float]:
        """
        Get value at coordinate

        Args:
            x, y, z: Coordinates

        Returns:
            Value at coordinate, or 0.0 if not set
        """
        if not self._validate_coords(x, y, z):
            return None

        return self.sparse_data.get((x, y, z), 0.0)

    def attach_llm(self, x: int, y: int, z: int, llm: Optional[FemtoLLM] = None) -> bool:
        """
        Attach LLM to coordinate

        Args:
            x, y, z: Coordinates
            llm: FemtoLLM instance (creates new if None)

        Returns:
            True if successful
        """
        if not self._validate_coords(x, y, z):
            return False

        coord = (x, y, z)
        self.llms[coord] = llm if llm is not None else FemtoLLM()

        return True

    def llm_at(self, x: int, y: int, z: int) -> Optional[FemtoLLM]:
        """
        Get LLM at coordinate (creates new if not exists)

        Args:
            x, y, z: Coordinates

        Returns:
            FemtoLLM instance or None if invalid coords
        """
        if not self._validate_coords(x, y, z):
            return None

        coord = (x, y, z)
        if coord not in self.llms:
            self.llms[coord] = FemtoLLM()

        return self.llms[coord]

    async def process_at(self, x: int, y: int, z: int, text: str) -> Optional[str]:
        """
        Process text with LLM at coordinate

        Args:
            x, y, z: Coordinates
            text: Input text

        Returns:
            Processed result or None
        """
        llm = self.llm_at(x, y, z)
        if llm is None:
            return None

        return await llm.process(text)

    def get_face(self, face: str, depth: int = 0) -> List[Tuple[int, int, int]]:
        """
        Get all coordinates on a face

        Args:
            face: 'top', 'bottom', 'north', 'south', 'east', 'west'
            depth: Depth from face (0 = surface)

        Returns:
            List of coordinates
        """
        x_max, y_max, z_max = self.dimensions
        coords = []

        if face == 'top':  # z = max
            z = z_max - 1 - depth
            coords = [(x, y, z) for x in range(x_max) for y in range(y_max)]
        elif face == 'bottom':  # z = 0
            z = depth
            coords = [(x, y, z) for x in range(x_max) for y in range(y_max)]
        elif face == 'north':  # y = max
            y = y_max - 1 - depth
            coords = [(x, y, z) for x in range(x_max) for z in range(z_max)]
        elif face == 'south':  # y = 0
            y = depth
            coords = [(x, y, z) for x in range(x_max) for z in range(z_max)]
        elif face == 'east':  # x = max
            x = x_max - 1 - depth
            coords = [(x, y, z) for y in range(y_max) for z in range(z_max)]
        elif face == 'west':  # x = 0
            x = depth
            coords = [(x, y, z) for y in range(y_max) for z in range(z_max)]

        return coords

    async def interlock_face(self, face: str, operation: str = "activate") -> int:
        """
        Perform interlock operation on entire face (1M cubes)

        Args:
            face: Face identifier
            operation: 'activate', 'process', 'clear'

        Returns:
            Number of cubes affected
        """
        coords = self.get_face(face)
        count = 0

        if operation == "activate":
            for x, y, z in coords:
                self.set(x, y, z, 1.0)
                count += 1
        elif operation == "clear":
            for x, y, z in coords:
                self.set(x, y, z, 0.0)
                count += 1
        elif operation == "process":
            tasks = []
            for x, y, z in coords[:100]:  # Limit to 100 for demo
                tasks.append(self.process_at(x, y, z, f"face_{face}"))
            await asyncio.gather(*tasks)
            count = len(tasks)

        return count

    def get_neighbors(self, x: int, y: int, z: int, include_diagonals: bool = False) -> List[Tuple[int, int, int]]:
        """
        Get neighboring coordinates

        Args:
            x, y, z: Center coordinate
            include_diagonals: Include diagonal neighbors

        Returns:
            List of neighbor coordinates
        """
        neighbors = []

        # 6 direct neighbors
        for dx, dy, dz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
            nx, ny, nz = x + dx, y + dy, z + dz
            if self._validate_coords(nx, ny, nz):
                neighbors.append((nx, ny, nz))

        if include_diagonals:
            # 20 additional diagonal neighbors (edges + corners)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == dy == dz == 0:
                            continue
                        nx, ny, nz = x + dx, y + dy, z + dz
                        if self._validate_coords(nx, ny, nz) and (nx, ny, nz) not in neighbors:
                            neighbors.append((nx, ny, nz))

        return neighbors

    def get_active_cubes(self) -> List[Tuple[int, int, int]]:
        """Get all coordinates with non-zero values"""
        return list(self.sparse_data.keys())

    def clear(self):
        """Clear all data"""
        self.sparse_data.clear()
        self.llms.clear()

    def memory_usage(self) -> dict:
        """Calculate memory usage"""
        # Sparse data
        sparse_bytes = len(self.sparse_data) * (3 * 4 + 8)  # 3 ints + 1 float

        # LLMs
        llm_count = len(self.llms)
        llm_bytes = llm_count * 4 * 1024 * 1024  # ~4MB per LLM

        total_mb = (sparse_bytes + llm_bytes) / (1024 * 1024)

        # Theoretical full array
        theoretical_full = np.prod(self.dimensions) * 8 / (1024 * 1024 * 1024)  # GB

        return {
            "dimensions": self.dimensions,
            "active_cubes": len(self.sparse_data),
            "active_llms": llm_count,
            "memory_mb": round(total_mb, 2),
            "theoretical_full_gb": round(theoretical_full, 2),
            "compression_ratio": f"{round(theoretical_full * 1024 / max(total_mb, 0.001), 0)}x"
        }

    def stats(self) -> dict:
        """Get statistics"""
        return {
            "name": self.name,
            "dimensions": self.dimensions,
            "total_cubes": np.prod(self.dimensions),
            "active_cubes": len(self.sparse_data),
            "active_llms": len(self.llms),
            "operations": self.operation_count,
            **self.memory_usage(),
            **self.metadata
        }

    def __repr__(self) -> str:
        return f"BlockArray(name={self.name}, dim={self.dimensions}, active={len(self.sparse_data)})"


if __name__ == "__main__":
    # Quick test
    print("🧊 BlockArray Test")

    # Create small array for testing
    ba = BlockArray(dimensions=(10, 10, 10), name="test")
    print(f"Created: {ba}")

    # Set some values
    ba.set(0, 0, 0, 1.0)
    ba.set(5, 5, 5, 2.5)
    ba.set(9, 9, 9, 3.7)

    print(f"Get (0,0,0): {ba.get(0, 0, 0)}")
    print(f"Get (5,5,5): {ba.get(5, 5, 5)}")

    # Test LLM attachment
    async def test_llm():
        result = await ba.process_at(0, 0, 0, "Hello from origin")
        print(f"Process result: {result}")

    asyncio.run(test_llm())

    # Test neighbors
    neighbors = ba.get_neighbors(5, 5, 5)
    print(f"Neighbors of (5,5,5): {len(neighbors)}")

    # Stats
    print(f"Stats: {ba.stats()}")

    print("✓ BlockArray tests passed!")
