#!/usr/bin/env python3
"""
Dev Orchestrator - Intelligent Task Router for Development Tasks
Automatically analyzes, routes, and executes development tasks using MCP agents
"""

import asyncio
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

# Add src to path for imports (commented out - not needed for simplified version)
# sys.path.insert(0, str(Path(__file__).parent / "src"))

# Simplified imports - we'll use the basic functionality without MCP agent for now
# from mcp_agent import MCPAgent
# from mcp_agent.config import MCPAgentConfig
# from mcp_agent.models import Task, TaskResult, AgentCapability

console = Console()

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
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
        if self.secrets_path.exists():
            with open(self.secrets_path, 'r') as f:
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
            'refactor': r'refactor|solid|clean|improve|optimize code',
            'test': r'test|unit test|coverage|pytest|jest|spec',
            'docs': r'document|docs|readme|api doc|comment',
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
        medium_priority_keywords = ['important', 'needed', 'should']
        
        task_lower = task_desc.lower()
        
        for keyword in high_priority_keywords:
            if keyword in task_lower:
                return 5
                
        for keyword in medium_priority_keywords:
            if keyword in task_lower:
                return 3
                
        return 2
    
    async def route_task(self, task: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Route task to appropriate agent"""
        task_type = task.get('type', 'general')
        
        # Get agent configuration
        agent_config = self.config.get('agents', {}).get(f"{task_type}_agent")
        
        if not agent_config:
            # Use default agent
            agent_config = self.config.get('agents', {}).get('refactor_agent', {})
            
        return task_type, agent_config
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        console.print(f"\n[bold cyan]Executing:[/bold cyan] {task['description']}")
        
        agent_type, agent_config = await self.route_task(task)
        
        # Simulate task execution (replace with actual MCP agent call)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task_id = progress.add_task(f"Processing with {agent_type} agent...", total=None)
            
            # Here you would actually call the MCP agent
            await asyncio.sleep(2)  # Simulate processing
            
            progress.update(task_id, completed=True)
        
        result = {
            'task': task['description'],
            'agent': agent_type,
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'output': f"Task completed by {agent_type} agent"
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
                console.print(f"\n[bold yellow]Executing priority {priority} tasks...[/bold yellow]")
                
                # Execute tasks in parallel within priority group
                group_results = await asyncio.gather(
                    *[self.execute_task(task) for task in group_tasks],
                    return_exceptions=True
                )
                results.extend(group_results)
        else:
            # Sequential execution
            for task in tasks:
                result = await self.execute_task(task)
                results.append(result)
                
        return results
    
    def display_results(self, results: List[Dict[str, Any]]):
        """Display execution results in a formatted table"""
        table = Table(title="Task Execution Results", show_header=True)
        table.add_column("Task", style="cyan", width=40)
        table.add_column("Agent", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Time", style="yellow")
        
        for result in results:
            status_icon = "[OK]" if result['status'] == 'completed' else "[FAIL]"
            table.add_row(
                result['task'][:40] + "..." if len(result['task']) > 40 else result['task'],
                result['agent'],
                f"{status_icon} {result['status']}",
                result['timestamp'].split('T')[1].split('.')[0]
            )
            
        console.print(table)
    
    def save_history(self, filename: str = "task_history.json"):
        """Save task history to file"""
        history_file = Path(filename)
        with open(history_file, 'w') as f:
            json.dump(self.task_history, f, indent=2)
        console.print(f"[green]Task history saved to {history_file}[/green]")
    
    async def run(self, task_input: str, parallel: bool = True, 
                  save_history: bool = True):
        """Main orchestration flow"""
        console.print(Panel.fit(
            "[bold green]Dev Orchestrator[/bold green]\n"
            "Intelligent Task Routing & Execution",
            border_style="green"
        ))
        
        # Parse tasks
        console.print("\n[bold]Analyzing tasks...[/bold]")
        tasks = self.parse_tasks(task_input)
        
        if not tasks:
            console.print("[red]No tasks found to execute[/red]")
            return
        
        # Display parsed tasks
        console.print(f"\n[bold]Found {len(tasks)} tasks:[/bold]")
        for i, task in enumerate(tasks, 1):
            priority_stars = "*" * task['priority']
            console.print(f"  {i}. [{task['type']}] {task['description']} Priority: {priority_stars}")
        
        # Execute tasks
        console.print("\n[bold]Executing tasks...[/bold]")
        results = await self.execute_tasks(tasks, parallel=parallel)
        
        # Display results
        self.display_results(results)
        
        # Save history if requested
        if save_history:
            self.save_history()
        
        console.print("\n[bold green]All tasks completed![/bold green]")

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
        console.print("[bold cyan]Launching web interface...[/bold cyan]")
        import subprocess
        subprocess.Popen([sys.executable, "streamlit_orchestrator.py"])
        return
    
    # Handle API server
    if args.api:
        console.print("[bold cyan]Starting API server...[/bold cyan]")
        import subprocess
        subprocess.Popen([sys.executable, "api_server.py"])
        return
    
    # Get tasks
    task_input = ""
    if args.tasks:
        task_input = args.tasks
    elif args.file:
        with open(args.file, 'r') as f:
            task_input = f.read()
    else:
        # Interactive mode
        console.print("[bold]Enter tasks (one per line, empty line to finish):[/bold]")
        lines = []
        while True:
            line = input("> ")
            if not line:
                break
            lines.append(line)
        task_input = "\n".join(lines)
    
    if not task_input:
        console.print("[red]No tasks provided[/red]")
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