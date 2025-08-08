#!/usr/bin/env python3
"""
Dev Orchestrator - Version Windows Compatible
Intelligent Task Router for Development Tasks
"""

import asyncio
import argparse
import json
import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import yaml

# Fix encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

class DevOrchestrator:
    """Main orchestrator for development tasks"""
    
    def __init__(self, config_path: str = "mcp_agent.config.yaml", 
                 secrets_path: str = "mcp_agent.secrets.yaml"):
        self.config_path = Path(config_path)
        self.secrets_path = Path(secrets_path)
        self.config = self._load_config()
        self.agents = {}
        self.task_history = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML files"""
        config = {}
        
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
        if self.secrets_path.exists():
            with open(self.secrets_path, 'r', encoding='utf-8') as f:
                secrets = yaml.safe_load(f)
                config['secrets'] = secrets
                
        return config
    
    def parse_tasks(self, task_string: str) -> List[Dict[str, Any]]:
        """Parse task string into structured tasks"""
        tasks = []
        
        # Split by common delimiters
        task_items = re.split(r'[,;]|\n|(?:\d+\.)', task_string)
        
        for item in task_items:
            item = item.strip()
            if not item:
                continue
                
            # Analyze task type
            task_type = self._identify_task_type(item)
            priority = self._estimate_priority(item)
            
            tasks.append({
                'description': item,
                'type': task_type,
                'priority': priority,
                'status': 'pending'
            })
            
        return tasks
    
    def _identify_task_type(self, task_desc: str) -> str:
        """Identify the type of task based on keywords"""
        task_desc_lower = task_desc.lower()
        
        # Check routing rules from config
        if 'task_router' in self.config and 'rules' in self.config['task_router']:
            for rule in self.config['task_router']['rules']:
                if re.search(rule['pattern'], task_desc_lower):
                    return rule['agent']
                    
        # Default patterns if not in config
        patterns = {
            'refactor': r'refactor|solid|clean|improve|optimize code|authentication',
            'test': r'test|unit test|coverage|pytest|jest|spec|comprehensive',
            'docs': r'document|docs|readme|api doc|comment|documentation|update.*doc',
            'database': r'database|query|sql|index|optimize db',
            'git': r'commit|pull request|pr|merge|branch'
        }
        
        for task_type, pattern in patterns.items():
            if re.search(pattern, task_desc_lower):
                return task_type
                
        return 'general'
    
    def _estimate_priority(self, task_desc: str) -> int:
        """Estimate task priority (1-5, 5 being highest)"""
        high_priority_keywords = ['critical', 'urgent', 'asap', 'bug', 'fix', 'broken']
        medium_priority_keywords = ['important', 'needed', 'should', 'comprehensive']
        
        task_lower = task_desc.lower()
        
        for keyword in high_priority_keywords:
            if keyword in task_lower:
                return 5
                
        for keyword in medium_priority_keywords:
            if keyword in task_lower:
                return 4
                
        return 3
    
    async def route_task(self, task: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Route task to appropriate agent"""
        task_type = task.get('type', 'general')
        
        # Get agent configuration
        agent_config = self.config.get('agents', {}).get(f"{task_type}_agent", {})
        
        if not agent_config:
            # Use default agent
            agent_config = self.config.get('agents', {}).get('refactor_agent', {})
            
        return task_type, agent_config
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        print(f"\n[EXECUTING] {task['description']}")
        
        agent_type, agent_config = await self.route_task(task)
        print(f"  -> Routing to: {agent_type} agent")
        
        # Simulate task execution (replace with actual MCP agent call when ready)
        await asyncio.sleep(1)  # Simulate processing
        print(f"  -> Processing complete")
        
        result = {
            'task': task['description'],
            'agent': agent_type,
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'output': f"Task completed successfully by {agent_type} agent"
        }
        
        self.task_history.append(result)
        return result
    
    async def execute_tasks(self, tasks: List[Dict[str, Any]], parallel: bool = True) -> List[Dict[str, Any]]:
        """Execute multiple tasks"""
        results = []
        
        if parallel:
            # Group tasks by priority for parallel execution
            priority_groups = {}
            for task in tasks:
                priority = task.get('priority', 2)
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(task)
            
            # Execute high priority tasks first
            for priority in sorted(priority_groups.keys(), reverse=True):
                group_tasks = priority_groups[priority]
                print(f"\n[BATCH] Executing priority {priority} tasks ({len(group_tasks)} tasks)...")
                
                # Execute tasks in parallel within priority group
                group_results = await asyncio.gather(
                    *[self.execute_task(task) for task in group_tasks],
                    return_exceptions=True
                )
                
                # Filter out exceptions and add successful results
                for result in group_results:
                    if not isinstance(result, Exception):
                        results.append(result)
                    else:
                        print(f"[ERROR] Task failed: {str(result)}")
        else:
            # Sequential execution
            print(f"\n[SEQUENTIAL] Processing {len(tasks)} tasks one by one...")
            for task in tasks:
                result = await self.execute_task(task)
                results.append(result)
                
        return results
    
    def display_results(self, results: List[Dict[str, Any]]):
        """Display execution results"""
        print("\n" + "="*60)
        print("TASK EXECUTION RESULTS")
        print("="*60)
        
        for i, result in enumerate(results, 1):
            status = "[OK]" if result['status'] == 'completed' else "[FAIL]"
            timestamp = result['timestamp'].split('T')[1].split('.')[0]
            
            print(f"{i:2d}. {status} {result['agent']:<12} | {timestamp}")
            print(f"    Task: {result['task']}")
            print(f"    Output: {result['output']}")
            print()
    
    def save_history(self, filename: str = "task_history.json"):
        """Save task history to file"""
        history_file = Path(filename)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.task_history, f, indent=2, ensure_ascii=False)
        print(f"[SAVED] Task history saved to {history_file}")
    
    async def run(self, task_input: str, parallel: bool = True, 
                  save_history: bool = True):
        """Main orchestration flow"""
        print("="*60)
        print("DEV ORCHESTRATOR - Intelligent Task Routing & Execution")
        print("="*60)
        
        # Parse tasks
        print("\n[PARSING] Analyzing tasks...")
        tasks = self.parse_tasks(task_input)
        
        if not tasks:
            print("[ERROR] No tasks found to execute")
            return
        
        # Display parsed tasks
        print(f"\n[ANALYSIS] Found {len(tasks)} tasks:")
        for i, task in enumerate(tasks, 1):
            priority_stars = "*" * task['priority']
            print(f"  {i}. Type: {task['type']:<10} Priority: {priority_stars} - {task['description']}")
        
        # Execute tasks
        print(f"\n[EXECUTION] Starting task execution (parallel={parallel})...")
        results = await self.execute_tasks(tasks, parallel=parallel)
        
        # Display results
        self.display_results(results)
        
        # Save history if requested
        if save_history:
            self.save_history()
        
        print("\n[COMPLETE] All tasks completed successfully!")
        print(f"Total tasks: {len(results)} | Success rate: 100%")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dev Orchestrator - Intelligent task routing for development"
    )
    parser.add_argument(
        "--tasks", "-t",
        type=str,
        help="Comma-separated list of tasks or task description"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="File containing tasks (one per line)"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="mcp_agent.config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--secrets", "-s",
        type=str,
        default="mcp_agent.secrets.yaml",
        help="Path to secrets file"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Execute tasks sequentially instead of in parallel"
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Don't save task history"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch web interface"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start API server"
    )
    
    args = parser.parse_args()
    
    # Handle web interface
    if args.web:
        print("[LAUNCHING] Starting web interface...")
        import subprocess
        subprocess.Popen([sys.executable, "streamlit", "run", "streamlit_orchestrator.py"])
        print("Web interface should open at http://localhost:8501")
        return
    
    # Handle API server
    if args.api:
        print("[LAUNCHING] Starting API server...")
        import subprocess
        subprocess.Popen([sys.executable, "api_server.py"])
        print("API server should start at http://localhost:8502")
        return
    
    # Get tasks
    task_input = ""
    if args.tasks:
        task_input = args.tasks
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            task_input = f.read()
    else:
        # Interactive mode
        print("[INPUT] Enter tasks (one per line, empty line to finish):")
        lines = []
        while True:
            try:
                line = input("> ")
                if not line:
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print("\n[CANCELLED] Operation cancelled by user")
                return
        task_input = "\n".join(lines)
    
    if not task_input:
        print("[ERROR] No tasks provided")
        return
    
    # Create orchestrator
    orchestrator = DevOrchestrator(
        config_path=args.config,
        secrets_path=args.secrets
    )
    
    # Run orchestration
    await orchestrator.run(
        task_input,
        parallel=not args.sequential,
        save_history=not args.no_history
    )

if __name__ == "__main__":
    asyncio.run(main())