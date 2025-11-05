"""
🧬 KONOMI SYSTEM - Base Template
Main orchestrator bringing together eVGPU, FemtoLLM, BlockArray, and Cube
"""
import asyncio
from typing import Dict, Optional, Tuple, List
from evgpu import eVGPU
from femtollm import FemtoLLM
from blockarray import BlockArray
from cube import Cube, MachineState
import numpy as np
import time


class KonomiSystem:
    """
    KonomiSystem: Main orchestration layer

    Components:
    - eVGPU: CPU-based tensor operations
    - FemtoLLM: Lightweight language models
    - BlockArray: 1000³ computational grid
    - Cube: 9-node computational systems

    Goal: Distributed AI without GPUs. Pure efficiency. CPU is enough!
    """

    def __init__(self, evgpu_cores: int = 4):
        """
        Initialize KONOMI System

        Args:
            evgpu_cores: Number of CPU cores for eVGPU
        """
        # Core components
        self.evgpu = eVGPU(cores=evgpu_cores)

        # Storage
        self.block_arrays: Dict[str, BlockArray] = {}
        self.cubes: Dict[str, Cube] = {}
        self.llms: Dict[str, FemtoLLM] = {}

        # Templates
        self.templates: Dict[str, dict] = {}

        # System stats
        self.start_time = time.time()
        self.operation_count = 0

        print("🧬 KONOMI SYSTEM initialized")
        print(f"⚡ eVGPU: {self.evgpu.info()}")

    def create_block_array(self, name: str, dimensions: Tuple[int, int, int] = (10, 10, 10)) -> BlockArray:
        """
        Create new BlockArray

        Args:
            name: Array identifier
            dimensions: (x, y, z) dimensions

        Returns:
            BlockArray instance
        """
        ba = BlockArray(dimensions=dimensions, name=name)
        self.block_arrays[name] = ba
        self.operation_count += 1

        print(f"🧊 Created BlockArray '{name}' with dimensions {dimensions}")
        return ba

    def get_block_array(self, name: str) -> Optional[BlockArray]:
        """Get BlockArray by name"""
        return self.block_arrays.get(name)

    def create_cube(self, cube_id: str, seed: Optional[int] = None) -> Cube:
        """
        Create new Cube

        Args:
            cube_id: Cube identifier
            seed: Random seed for LLMs

        Returns:
            Cube instance
        """
        cube = Cube(cube_id=cube_id, llm_seed=seed)
        self.cubes[cube_id] = cube
        self.operation_count += 1

        print(f"🎲 Created Cube '{cube_id}' with 9 nodes")
        return cube

    def get_cube(self, cube_id: str) -> Optional[Cube]:
        """Get Cube by ID"""
        return self.cubes.get(cube_id)

    def create_llm(self, name: str, seed: Optional[int] = None) -> FemtoLLM:
        """
        Create standalone FemtoLLM

        Args:
            name: LLM identifier
            seed: Random seed

        Returns:
            FemtoLLM instance
        """
        llm = FemtoLLM(seed=seed)
        self.llms[name] = llm
        self.operation_count += 1

        print(f"🧠 Created FemtoLLM '{name}'")
        return llm

    def get_llm(self, name: str) -> Optional[FemtoLLM]:
        """Get LLM by name"""
        return self.llms.get(name)

    async def process_distributed(self, text: str, cube_ids: List[str]) -> Dict[str, dict]:
        """
        Process text across multiple cubes in parallel

        Args:
            text: Input text
            cube_ids: List of cube IDs to use

        Returns:
            Results from each cube
        """
        tasks = {}

        for cube_id in cube_ids:
            cube = self.get_cube(cube_id)
            if cube:
                tasks[cube_id] = cube.execute_cycle(text)

        # Execute in parallel
        results = {}
        completed = await asyncio.gather(*tasks.values())

        for cube_id, result in zip(tasks.keys(), completed):
            results[cube_id] = result

        self.operation_count += len(cube_ids)
        return results

    def tensor_compute(self, a: np.ndarray, b: np.ndarray, op: str = '@') -> np.ndarray:
        """
        Perform tensor computation using eVGPU

        Args:
            a, b: Input tensors
            op: Operation type

        Returns:
            Result tensor
        """
        result = self.evgpu.tensor(a, b, op)
        self.operation_count += 1
        return result

    def create_template(self, template_id: str, config: dict) -> dict:
        """
        Create reusable template configuration

        Args:
            template_id: Template identifier
            config: Template configuration

        Returns:
            Template metadata
        """
        template = {
            "id": template_id,
            "config": config,
            "created_at": time.time(),
            "instances": []
        }

        self.templates[template_id] = template
        print(f"📋 Created template '{template_id}'")
        return template

    def instantiate_template(self, template_id: str, instance_name: str) -> Optional[BlockArray]:
        """
        Create instance from template

        Args:
            template_id: Template to instantiate
            instance_name: Name for new instance

        Returns:
            BlockArray instance or None
        """
        template = self.templates.get(template_id)
        if not template:
            return None

        config = template["config"]
        dimensions = config.get("dimensions", (10, 10, 10))

        ba = self.create_block_array(instance_name, dimensions)
        template["instances"].append(instance_name)

        return ba

    async def interlock_operation(self,
                                  array_name: str,
                                  face: str,
                                  operation: str = "activate") -> int:
        """
        Perform interlock operation on BlockArray face

        Args:
            array_name: BlockArray name
            face: Face identifier
            operation: Operation type

        Returns:
            Number of cubes affected
        """
        ba = self.get_block_array(array_name)
        if not ba:
            return 0

        count = await ba.interlock_face(face, operation)
        self.operation_count += 1

        print(f"🔄 Interlock {operation} on {face} face: {count} cubes")
        return count

    def get_system_stats(self) -> dict:
        """Get comprehensive system statistics"""
        uptime = time.time() - self.start_time

        # Aggregate BlockArray stats
        total_active_cubes = sum(len(ba.sparse_data) for ba in self.block_arrays.values())
        total_active_llms = sum(len(ba.llms) for ba in self.block_arrays.values())

        # Aggregate Cube stats
        total_cube_nodes = len(self.cubes) * 9
        cube_messages = sum(cube.stats["messages_processed"] for cube in self.cubes.values())

        return {
            "system": "KONOMI",
            "uptime_seconds": round(uptime, 2),
            "operations": self.operation_count,
            "components": {
                "evgpu": self.evgpu.info(),
                "block_arrays": len(self.block_arrays),
                "cubes": len(self.cubes),
                "standalone_llms": len(self.llms),
            },
            "computation": {
                "active_cubes": total_active_cubes,
                "active_llms": total_active_llms,
                "cube_nodes": total_cube_nodes,
                "messages_processed": cube_messages,
            },
            "templates": len(self.templates),
            "performance_targets": {
                "llm_latency": "0.1s/req",
                "memory": "<2GB",
                "gpu_required": False,
                "cpu_efficiency": "100%"
            }
        }

    def optimize_memory(self):
        """Run memory optimization across all components"""
        optimized = 0

        # Clear empty BlockArrays
        for name, ba in list(self.block_arrays.items()):
            if len(ba.sparse_data) == 0:
                del self.block_arrays[name]
                optimized += 1

        print(f"🔧 Optimized: removed {optimized} empty arrays")

    async def health_check(self) -> dict:
        """System health check"""
        health = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {}
        }

        # Check eVGPU
        try:
            test_a = np.random.randn(2, 2)
            test_b = np.random.randn(2, 2)
            self.evgpu.tensor(test_a, test_b, '@')
            health["components"]["evgpu"] = "ok"
        except Exception as e:
            health["components"]["evgpu"] = f"error: {str(e)}"
            health["status"] = "degraded"

        # Check LLMs
        try:
            test_llm = FemtoLLM()
            await test_llm.process("health check")
            health["components"]["llm"] = "ok"
        except Exception as e:
            health["components"]["llm"] = f"error: {str(e)}"
            health["status"] = "degraded"

        # Check BlockArrays
        health["components"]["block_arrays"] = f"{len(self.block_arrays)} active"

        # Check Cubes
        health["components"]["cubes"] = f"{len(self.cubes)} active"

        return health

    def __repr__(self) -> str:
        return (f"KonomiSystem(arrays={len(self.block_arrays)}, "
                f"cubes={len(self.cubes)}, ops={self.operation_count})")


async def demo():
    """Demo: Quick showcase of KONOMI System"""
    print("\n" + "="*60)
    print("🧬 KONOMI SYSTEM DEMO")
    print("="*60 + "\n")

    # Initialize
    K = KonomiSystem(evgpu_cores=4)

    print("\n1️⃣ Creating BlockArray...")
    BA = K.create_block_array("main", (10, 10, 10))
    BA.set(0, 0, 0, 1.0)
    BA.set(5, 5, 5, 2.5)
    BA.set(9, 9, 9, 3.7)
    print(f"   Active cubes: {len(BA.sparse_data)}")

    print("\n2️⃣ Creating Cube constellation...")
    C = K.create_cube("c1", seed=42)
    C.connect('NEU', 'SWD')  # Diagonal link
    C.connect_diagonals()
    print(f"   {C.cube_info()}")

    print("\n3️⃣ eVGPU tensor operations...")
    a = np.random.randn(4, 4)
    b = np.random.randn(4, 4)
    result = K.tensor_compute(a, b, '@')
    print(f"   Matmul result shape: {result.shape}")

    print("\n4️⃣ Processing with Cube...")
    results = await C.execute_cycle("Hello Konomi System!")
    print(f"   Processed at {len(results)} nodes")
    print(f"   State: {C.state.value}")

    print("\n5️⃣ LLM processing in BlockArray...")
    llm_result = await BA.process_at(0, 0, 0, "Origin processing")
    print(f"   Result: {llm_result}")

    print("\n6️⃣ Face interlock operation...")
    count = await K.interlock_operation("main", "top", "activate")
    print(f"   Activated {count} cubes on top face")

    print("\n7️⃣ Distributed processing...")
    K.create_cube("c2", seed=43)
    K.create_cube("c3", seed=44)
    dist_results = await K.process_distributed("Distributed test", ["c1", "c2", "c3"])
    print(f"   Processed across {len(dist_results)} cubes")

    print("\n8️⃣ System statistics...")
    stats = K.get_system_stats()
    print(f"   Operations: {stats['operations']}")
    print(f"   Active cubes: {stats['computation']['active_cubes']}")
    print(f"   Cube nodes: {stats['computation']['cube_nodes']}")
    print(f"   GPU required: {stats['performance_targets']['gpu_required']}")

    print("\n9️⃣ Health check...")
    health = await K.health_check()
    print(f"   Status: {health['status']}")
    print(f"   Components: {health['components']}")

    print("\n" + "="*60)
    print("✓ DEMO COMPLETE - KONOMI System operational!")
    print("🎯 Goal achieved: Distributed AI without GPUs")
    print("="*60 + "\n")

    return K


if __name__ == "__main__":
    # Run demo
    system = asyncio.run(demo())
