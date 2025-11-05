#!/usr/bin/env python3
"""
🧬 KONOMI SYSTEM - Test Suite
Basic tests for all components
"""
import asyncio
import numpy as np
from evgpu import eVGPU
from femtollm import FemtoLLM
from blockarray import BlockArray
from cube import Cube
from base_template import KonomiSystem


def test_evgpu():
    """Test eVGPU functionality"""
    print("Testing eVGPU...")

    gpu = eVGPU(cores=4)

    # Test matmul
    a = np.random.randn(4, 4)
    b = np.random.randn(4, 4)
    result = gpu.tensor(a, b, '@')
    assert result.shape == (4, 4), "Matmul shape mismatch"

    # Test activation
    x = np.random.randn(10)
    activated = gpu.activate(x, 'relu')
    assert activated.shape == x.shape, "Activation shape mismatch"
    assert np.all(activated >= 0), "ReLU should be non-negative"

    # Test pooling
    x = np.random.randn(10, 10)
    pooled = gpu.pool(x, pool_size=2, mode='max')
    assert pooled.shape == (5, 5), "Pooling shape mismatch"

    print("  ✓ eVGPU tests passed")


async def test_femtollm():
    """Test FemtoLLM functionality"""
    print("Testing FemtoLLM...")

    llm = FemtoLLM(seed=42)

    # Test processing
    result = await llm.process("Test input")
    assert isinstance(result, str), "Process should return string"
    assert len(result) > 0, "Process should return non-empty string"

    # Test embedding
    embedding = llm.get_embedding("test")
    assert embedding.shape == (16,), "Embedding should be 16-dim"

    # Test memory usage
    memory = llm.memory_usage()
    assert memory['megabytes'] < 10, "Memory should be < 10MB"

    print("  ✓ FemtoLLM tests passed")


async def test_blockarray():
    """Test BlockArray functionality"""
    print("Testing BlockArray...")

    ba = BlockArray(dimensions=(10, 10, 10), name="test")

    # Test set/get
    ba.set(5, 5, 5, 2.5)
    value = ba.get(5, 5, 5)
    assert value == 2.5, "Set/get value mismatch"

    # Test out of bounds
    value = ba.get(100, 100, 100)
    assert value is None, "Out of bounds should return None"

    # Test LLM attachment
    result = await ba.process_at(0, 0, 0, "Test")
    assert isinstance(result, str), "Process should return string"

    # Test neighbors
    neighbors = ba.get_neighbors(5, 5, 5)
    assert len(neighbors) == 6, "Should have 6 direct neighbors"

    # Test face
    face_coords = ba.get_face('top')
    assert len(face_coords) == 100, "Top face should have 100 cubes"

    print("  ✓ BlockArray tests passed")


async def test_cube():
    """Test Cube functionality"""
    print("Testing Cube...")

    cube = Cube(cube_id="test", llm_seed=42)

    # Test vertices
    assert len(cube.vertices) == 8, "Should have 8 vertices"
    assert cube.central is not None, "Should have central node"

    # Test processing
    result = await cube.process_vertex('NEU', "Test")
    assert isinstance(result, str), "Process should return string"

    result = await cube.process_central("Test")
    assert isinstance(result, str), "Process should return string"

    # Test connections
    success = cube.connect('NEU', 'SWD')
    assert success, "Connection should succeed"

    connections = cube.get_connections('NEU')
    assert 'SWD' in connections, "SWD should be in NEU connections"

    # Test messages
    success = await cube.send_message('NEU', 'SWD', "Test message")
    assert success, "Message send should succeed"

    messages = cube.get_messages('SWD')
    assert len(messages) > 0, "Should have messages"

    # Test execute cycle
    results = await cube.execute_cycle("Cycle test")
    assert len(results) == 9, "Should process all 9 nodes"

    print("  ✓ Cube tests passed")


async def test_konomi_system():
    """Test KonomiSystem integration"""
    print("Testing KonomiSystem...")

    K = KonomiSystem(evgpu_cores=4)

    # Test BlockArray creation
    ba = K.create_block_array("test", (10, 10, 10))
    assert ba.name == "test", "Array name mismatch"
    assert ba in K.block_arrays.values(), "Array should be registered"

    # Test Cube creation
    cube = K.create_cube("c1", seed=42)
    assert cube.cube_id == "c1", "Cube ID mismatch"
    assert cube in K.cubes.values(), "Cube should be registered"

    # Test LLM creation
    llm = K.create_llm("llm1", seed=42)
    assert llm in K.llms.values(), "LLM should be registered"

    # Test tensor computation
    a = np.random.randn(4, 4)
    b = np.random.randn(4, 4)
    result = K.tensor_compute(a, b, '@')
    assert result.shape == (4, 4), "Tensor computation shape mismatch"

    # Test distributed processing
    K.create_cube("c2")
    K.create_cube("c3")
    results = await K.process_distributed("Test", ["c1", "c2", "c3"])
    assert len(results) == 3, "Should process 3 cubes"

    # Test stats
    stats = K.get_system_stats()
    assert stats['components']['block_arrays'] > 0, "Should have arrays"
    assert stats['components']['cubes'] > 0, "Should have cubes"

    # Test health check
    health = await K.health_check()
    assert health['status'] in ['healthy', 'degraded'], "Should have valid status"

    print("  ✓ KonomiSystem tests passed")


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧬 KONOMI SYSTEM - TEST SUITE")
    print("="*60 + "\n")

    try:
        test_evgpu()
        await test_femtollm()
        await test_blockarray()
        await test_cube()
        await test_konomi_system()

        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
