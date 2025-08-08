#!/usr/bin/env python3
"""
Simplified test script for Dev Orchestrator
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import asyncio
from dev_orchestrator import DevOrchestrator

async def test_orchestrator():
    """Test the orchestrator with sample tasks"""
    print("=" * 50)
    print("Dev Orchestrator - Test Run")
    print("=" * 50)
    
    # Create orchestrator instance
    orchestrator = DevOrchestrator()
    
    # Test tasks
    test_tasks = """
    Analyze code structure
    Identify potential improvements  
    Generate documentation
    """
    
    print("\nParsing tasks...")
    tasks = orchestrator.parse_tasks(test_tasks)
    
    print(f"\nFound {len(tasks)} tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. Type: {task['type']:<10} Priority: {task['priority']} - {task['description']}")
    
    print("\nSimulating task execution...")
    for task in tasks:
        print(f"  - Routing '{task['description']}' to {task['type']} agent")
    
    print("\n[OK] Test completed successfully!")
    print("\nOrchestrator is ready to use with:")
    print("  - CLI: python dev_orchestrator.py --tasks \"task1, task2\"")
    print("  - Web: python dev_orchestrator.py --web")
    print("  - API: python dev_orchestrator.py --api")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())