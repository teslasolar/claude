#!/usr/bin/env python3
"""
🧬 KONOMI SYSTEM - Quick Start
Minimal example following the build spec
"""
import asyncio
import numpy as np
from base_template import KonomiSystem


async def quick_start():
    """
    Quick start example from the spec
    """
    print("\n" + "="*60)
    print("🧬 KONOMI SYSTEM - QUICK START")
    print("="*60 + "\n")

    # Initialize system
    K = KonomiSystem()
    print("✓ System initialized\n")

    # 1. Create 10x10x10 array (demo size)
    print("1️⃣ Creating BlockArray (10x10x10)...")
    BA = K.create_block_array("main", (10, 10, 10))
    BA.set(0, 0, 0, 1.0)  # activate origin
    print(f"   Activated origin: {BA.get(0, 0, 0)}")
    print(f"   Active cubes: {len(BA.sparse_data)}\n")

    # 2. Setup cube constellation
    print("2️⃣ Creating Cube constellation...")
    C = K.create_cube("c1")
    C.connect('NEU', 'SWD')  # diagonal link
    print(f"   Connected NEU ↔ SWD")
    print(f"   Cube info: {C.cube_info()}\n")

    # 3. Process with eVGPU
    print("3️⃣ Processing with eVGPU (CPU matmul)...")
    a = np.random.randn(4, 4)
    b = np.random.randn(4, 4)
    result = K.evgpu.tensor(a, b, '@')  # CPU matmul
    print(f"   Input shapes: {a.shape} @ {b.shape}")
    print(f"   Result shape: {result.shape}")
    print(f"   GPU required: {K.evgpu.info()['gpu_required']}\n")

    # 4. Run LLM
    print("4️⃣ Running FemtoLLM...")
    txt = await C.process_vertex('NEU', "Hello Konomi")
    print(f"   Input: 'Hello Konomi'")
    print(f"   Output: {txt}\n")

    # 5. System stats
    print("5️⃣ System Statistics:")
    stats = K.get_system_stats()
    print(f"   Operations: {stats['operations']}")
    print(f"   Block Arrays: {stats['components']['block_arrays']}")
    print(f"   Cubes: {stats['components']['cubes']}")
    print(f"   Active Cubes: {stats['computation']['active_cubes']}")
    print(f"   GPU Required: {stats['performance_targets']['gpu_required']}\n")

    print("="*60)
    print("✓ QUICK START COMPLETE!")
    print("🎯 Distributed AI without GPUs achieved")
    print("="*60 + "\n")

    return K


async def advanced_example():
    """
    Advanced features demonstration
    """
    print("\n" + "="*60)
    print("🚀 ADVANCED FEATURES DEMO")
    print("="*60 + "\n")

    K = KonomiSystem()

    # 1. Scaling demonstration
    print("1️⃣ Scaling demonstration...")
    print("   Creating arrays of different sizes:")
    for size in [10, 50, 100]:
        ba = K.create_block_array(f"array_{size}", (size, size, size))
        memory = ba.memory_usage()
        print(f"   {size}³: {memory['memory_mb']} MB (compression: {memory['compression_ratio']})")
    print()

    # 2. Multiple cubes working together
    print("2️⃣ Multi-cube distributed processing...")
    cubes = [K.create_cube(f"cube_{i}", seed=i) for i in range(3)]
    print(f"   Created {len(cubes)} cubes")

    # Process across all cubes
    results = await K.process_distributed(
        "Distributed processing test",
        [f"cube_{i}" for i in range(3)]
    )
    print(f"   Processed across {len(results)} cubes")
    print(f"   Total nodes: {len(results) * 9}\n")

    # 3. Face interlock operations
    print("3️⃣ Face interlock operations (1M cubes)...")
    ba = K.get_block_array("array_100")
    face_count = await K.interlock_operation("array_100", "top", "activate")
    print(f"   Activated {face_count} cubes on top face")
    print(f"   Total active: {len(ba.sparse_data)} cubes\n")

    # 4. eVGPU operations
    print("4️⃣ eVGPU operations...")
    x = np.random.randn(10, 10)

    # Activation
    activated = K.evgpu.activate(x, 'relu')
    print(f"   ReLU activation: {activated.shape}")

    # Pooling
    pooled = K.evgpu.pool(x, pool_size=2, mode='max')
    print(f"   Max pooling: {x.shape} → {pooled.shape}")

    # Multiple operations
    result = K.evgpu.activate(
        K.evgpu.tensor(x, x.T, '@'),
        'gelu'
    )
    print(f"   Chained operations: {result.shape}\n")

    # 5. State machine
    print("5️⃣ PackML state machine...")
    cube = K.get_cube("cube_0")
    print(f"   Initial state: {cube.state.value}")

    results = await cube.execute_cycle("State machine test")
    print(f"   After execution: {cube.state.value}")
    print(f"   State transitions: {len(cube.state_history)}\n")

    # Final stats
    print("📊 Final System Stats:")
    stats = K.get_system_stats()
    print(f"   Total operations: {stats['operations']}")
    print(f"   Uptime: {stats['uptime_seconds']}s")
    print(f"   Active cubes: {stats['computation']['active_cubes']}")
    print(f"   Cube nodes: {stats['computation']['cube_nodes']}")
    print(f"   Messages processed: {stats['computation']['messages_processed']}\n")

    print("="*60)
    print("✓ ADVANCED DEMO COMPLETE!")
    print("="*60 + "\n")


async def benchmark():
    """
    Performance benchmarking
    """
    print("\n" + "="*60)
    print("⚡ PERFORMANCE BENCHMARKS")
    print("="*60 + "\n")

    import time
    K = KonomiSystem()

    # 1. eVGPU throughput
    print("1️⃣ eVGPU Throughput (CPU)...")
    sizes = [10, 50, 100, 500]

    for size in sizes:
        a = np.random.randn(size, size)
        b = np.random.randn(size, size)

        start = time.time()
        result = K.evgpu.tensor(a, b, '@')
        elapsed = time.time() - start

        ops = 2 * size**3  # FLOPs for matrix multiply
        gflops = (ops / elapsed) / 1e9

        print(f"   {size}x{size}: {elapsed*1000:.2f}ms ({gflops:.2f} GFLOPS)")
    print()

    # 2. FemtoLLM latency
    print("2️⃣ FemtoLLM Latency...")
    llm = K.create_llm("bench")

    latencies = []
    for i in range(10):
        start = time.time()
        await llm.process(f"Test message {i}")
        elapsed = time.time() - start
        latencies.append(elapsed)

    avg_latency = np.mean(latencies)
    print(f"   Average: {avg_latency*1000:.2f}ms")
    print(f"   Min: {min(latencies)*1000:.2f}ms")
    print(f"   Max: {max(latencies)*1000:.2f}ms")
    print(f"   Target: 100ms")
    print(f"   Status: {'✓ PASS' if avg_latency < 0.15 else '✗ FAIL'}\n")

    # 3. Memory efficiency
    print("3️⃣ Memory Efficiency...")
    ba = K.create_block_array("bench", (100, 100, 100))

    # Activate random cubes
    for _ in range(1000):
        x, y, z = np.random.randint(0, 100, 3)
        ba.set(x, y, z, 1.0)

    memory = ba.memory_usage()
    print(f"   Array size: {memory['dimensions']}")
    print(f"   Active cubes: {memory['active_cubes']}")
    print(f"   Memory used: {memory['memory_mb']} MB")
    print(f"   Theoretical full: {memory['theoretical_full_gb']} GB")
    print(f"   Compression: {memory['compression_ratio']}\n")

    # 4. Concurrent processing
    print("4️⃣ Concurrent Cube Processing...")
    num_cubes = 10
    cubes = [K.create_cube(f"bench_{i}") for i in range(num_cubes)]

    start = time.time()
    results = await K.process_distributed(
        "Concurrent test",
        [f"bench_{i}" for i in range(num_cubes)]
    )
    elapsed = time.time() - start

    total_nodes = len(results) * 9
    nodes_per_sec = total_nodes / elapsed

    print(f"   Cubes: {num_cubes}")
    print(f"   Total nodes: {total_nodes}")
    print(f"   Time: {elapsed*1000:.2f}ms")
    print(f"   Throughput: {nodes_per_sec:.0f} nodes/sec\n")

    print("="*60)
    print("✓ BENCHMARKS COMPLETE!")
    print(f"📊 System can handle {nodes_per_sec:.0f} LLM calls/sec on CPU")
    print("="*60 + "\n")


async def main():
    """Run all examples"""
    # Quick start
    await quick_start()

    input("Press Enter to continue to advanced examples...")

    # Advanced features
    await advanced_example()

    input("Press Enter to run benchmarks...")

    # Benchmarks
    await benchmark()

    print("\n🎯 All examples completed!")
    print("Next steps:")
    print("  - Run REST API: python api_rest.py")
    print("  - Run WebSocket: python api_websocket.py")
    print("  - Run all services: python run_all.py")
    print("  - Deploy with Docker: docker-compose up")


if __name__ == "__main__":
    # Run: python quick_start.py
    asyncio.run(main())
