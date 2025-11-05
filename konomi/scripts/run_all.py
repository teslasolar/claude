#!/usr/bin/env python3
"""
🧬 KONOMI SYSTEM - Run All Services
Launch REST API, WebSocket, and demo simultaneously
"""
import asyncio
import multiprocessing
from api_rest import run_server as run_rest
from api_websocket import run_server as run_websocket
from base_template import demo
import time


def rest_api_process():
    """Run REST API in separate process"""
    print("🚀 Starting REST API server...")
    run_rest(host="0.0.0.0", port=3001)


def websocket_process():
    """Run WebSocket server in separate process"""
    print("🚀 Starting WebSocket server...")
    run_websocket(host="0.0.0.0", port=3002)


async def demo_process():
    """Run demo"""
    print("🚀 Starting KONOMI demo...")
    await asyncio.sleep(2)  # Wait for servers to start
    await demo()


def main():
    """Launch all services"""
    print("""
    ╔═══════════════════════════════════════╗
    ║    🧬 KONOMI SYSTEM - LAUNCHER 🧬     ║
    ╚═══════════════════════════════════════╝
    """)

    # Start REST API in separate process
    rest_process = multiprocessing.Process(target=rest_api_process)
    rest_process.start()

    # Wait a bit
    time.sleep(1)

    # Start WebSocket in separate process
    ws_process = multiprocessing.Process(target=websocket_process)
    ws_process.start()

    print("""
    ✓ Services launched!

    📡 REST API:    http://localhost:3001
    📡 API Docs:    http://localhost:3001/docs
    📡 WebSocket:   ws://localhost:3002
    📡 Health:      http://localhost:3001/health

    Press Ctrl+C to stop all services
    """)

    try:
        # Keep main process alive
        rest_process.join()
        ws_process.join()
    except KeyboardInterrupt:
        print("\n⏹ Stopping services...")
        rest_process.terminate()
        ws_process.terminate()
        rest_process.join()
        ws_process.join()
        print("✓ All services stopped")


if __name__ == "__main__":
    main()
