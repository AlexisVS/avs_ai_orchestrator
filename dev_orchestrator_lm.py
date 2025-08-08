#!/usr/bin/env python3
"""
Dev Orchestrator avec intégration LM Studio
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
import httpx

# Fix encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

class LMStudioClient:
    """Client pour communiquer avec LM Studio"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234"):
        self.base_url = base_url
        
    async def is_available(self) -> bool:
        """Vérifie si LM Studio est disponible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/v1/models", timeout=5.0)
                return response.status_code == 200
        except:
            return False
    
    async def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Génère une réponse via LM Studio"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "model": "qwen/qwen3-coder-30b",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are a software development consultant. Analyze tasks and provide detailed guidance, recommendations, and step-by-step plans. DO NOT attempt to modify files directly - only provide analysis and actionable advice that a developer can implement."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "stream": False
                }
                
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=data,
                    timeout=300.0  # 5 minutes pour Qwen3-Coder 30B
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"Error: LM Studio returned status {response.status_code}"
                    
        except Exception as e:
            print(f"[DEBUG] LM Studio error: {type(e).__name__}: {str(e)}")
            return f"Error connecting to LM Studio: {type(e).__name__}: {str(e)}"

class DevOrchestratorLM:
    """Orchestrateur avec intégration LM Studio"""
    
    def __init__(self, config_path: str = "mcp_agent.config.yaml", 
                 secrets_path: str = "mcp_agent.secrets.yaml"):
        self.config_path = Path(config_path)
        self.secrets_path = Path(secrets_path)
        self.config = self._load_config()
        self.lm_client = LMStudioClient()
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
        
        patterns = {
            'refactor': r'refactor|solid|clean|improve|optimize code|authentication',
            'test': r'test|unit test|coverage|pytest|jest|spec|comprehensive',
            'docs': r'document|docs|readme|api doc|comment|documentation|update.*doc',
            'database': r'database|query|sql|index|optimize db',
            'git': r'commit|pull request|pr|merge|branch',
            'analysis': r'analyz|review|inspect|audit|examine'
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
    
    def _create_agent_prompt(self, task: Dict[str, Any]) -> str:
        """Crée le prompt spécifique pour chaque type d'agent"""
        task_type = task['type']
        task_desc = task['description']
        
        prompts = {
            'refactor': f"""You are a code refactoring specialist. 

Task: {task_desc}

Please provide a detailed plan for refactoring this code, including:
1. SOLID principles to apply
2. Code smells to address
3. Specific refactoring steps
4. Testing strategy during refactoring

Provide actionable, step-by-step guidance.""",

            'test': f"""You are a testing specialist focused on comprehensive test coverage.

Task: {task_desc}

Please provide a detailed testing strategy including:
1. Types of tests needed (unit, integration, e2e)
2. Test scenarios to cover
3. Testing frameworks to use
4. Coverage goals and metrics
5. Specific test cases to implement

Focus on practical, implementable testing approaches.""",

            'docs': f"""You are a technical documentation specialist.

Task: {task_desc}

Please provide a documentation plan including:
1. Types of documentation needed
2. Target audience for each document
3. Structure and content outline
4. Documentation tools and formats
5. Maintenance strategy

Focus on clear, useful documentation that developers will actually use.""",

            'analysis': f"""You are a code analysis specialist.

Task: {task_desc}

Please provide a thorough analysis including:
1. Code structure assessment
2. Potential issues and improvements
3. Architecture recommendations
4. Performance considerations
5. Security aspects

Provide specific, actionable insights."""
        }
        
        return prompts.get(task_type, f"""You are a software development specialist.

Task: {task_desc}

Please provide detailed guidance on how to approach this task, including:
1. Analysis of requirements
2. Recommended approach
3. Implementation steps
4. Best practices to follow
5. Potential challenges and solutions

Focus on practical, actionable advice.""")
    
    async def execute_task_with_lm(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une tâche en utilisant LM Studio"""
        print(f"\n[EXECUTING] {task['description']}")
        print(f"  -> Agent type: {task['type']}")
        
        # Vérifier que LM Studio est disponible
        if not await self.lm_client.is_available():
            print(f"  -> [WARNING] LM Studio not available - using fallback mode")
            return {
                'task': task['description'],
                'agent': task['type'],
                'status': 'completed_fallback',
                'timestamp': datetime.now().isoformat(),
                'output': f"[FALLBACK] Task routed to {task['type']} agent but LM Studio unavailable"
            }
        
        # Créer le prompt spécifique à l'agent
        prompt = self._create_agent_prompt(task)
        
        print(f"  -> Sending to LM Studio...")
        
        # Envoyer à LM Studio
        ai_response = await self.lm_client.generate_response(prompt, max_tokens=800)
        
        print(f"  -> Response received ({len(ai_response)} chars)")
        
        result = {
            'task': task['description'],
            'agent': task['type'],
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'output': ai_response,
            'prompt_used': prompt[:100] + "..." if len(prompt) > 100 else prompt
        }
        
        self.task_history.append(result)
        return result
    
    async def execute_tasks(self, tasks: List[Dict[str, Any]], parallel: bool = True) -> List[Dict[str, Any]]:
        """Execute multiple tasks"""
        results = []
        
        # Vérifier LM Studio au début
        lm_available = await self.lm_client.is_available()
        print(f"\n[LM STUDIO] Status: {'AVAILABLE' if lm_available else 'NOT AVAILABLE'}")
        
        if not lm_available:
            print("[WARNING] LM Studio not running. Make sure to:")
            print("  1. Open LM Studio")
            print("  2. Load a model")
            print("  3. Start the local server")
            print("  4. Verify it's running on http://localhost:1234")
        
        if parallel and len(tasks) > 1:
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
                print(f"\n[BATCH] Processing priority {priority} tasks ({len(group_tasks)} tasks)...")
                
                # Execute tasks in parallel within priority group
                group_results = await asyncio.gather(
                    *[self.execute_task_with_lm(task) for task in group_tasks],
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
            print(f"\n[SEQUENTIAL] Processing {len(tasks)} tasks...")
            for task in tasks:
                result = await self.execute_task_with_lm(task)
                results.append(result)
                
        return results
    
    def display_results(self, results: List[Dict[str, Any]]):
        """Display execution results"""
        print("\n" + "="*80)
        print("TASK EXECUTION RESULTS WITH LM STUDIO")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            status = "[OK]" if result['status'] == 'completed' else f"[{result['status'].upper()}]"
            timestamp = result['timestamp'].split('T')[1].split('.')[0]
            
            print(f"\n{i:2d}. {status} {result['agent']:<15} | {timestamp}")
            print(f"    Task: {result['task']}")
            print(f"    AI Response:")
            print(f"    {'-' * 60}")
            
            # Afficher la réponse de l'IA avec indentation
            response_lines = result['output'].split('\n')
            for line in response_lines[:10]:  # Limiter à 10 lignes par tâche
                print(f"    {line}")
            
            if len(response_lines) > 10:
                print(f"    ... ({len(response_lines)-10} more lines)")
            
            print(f"    {'-' * 60}")
    
    def save_history(self, filename: str = "task_history_lm.json"):
        """Save task history to file"""
        history_file = Path(filename)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.task_history, f, indent=2, ensure_ascii=False)
        print(f"\n[SAVED] Detailed history with AI responses saved to {history_file}")
    
    async def run(self, task_input: str, parallel: bool = True, save_history: bool = True):
        """Main orchestration flow"""
        print("="*80)
        print("DEV ORCHESTRATOR + LM STUDIO - AI-Powered Task Execution")
        print("="*80)
        
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
            print(f"  {i}. Type: {task['type']:<12} Priority: {priority_stars} - {task['description']}")
        
        # Execute tasks
        print(f"\n[EXECUTION] Starting AI-powered execution (parallel={parallel})...")
        results = await self.execute_tasks(tasks, parallel=parallel)
        
        # Display results
        self.display_results(results)
        
        # Save history if requested
        if save_history:
            self.save_history()
        
        print(f"\n[COMPLETE] All tasks processed!")
        print(f"Total tasks: {len(results)} | LM Studio integration: ACTIVE")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dev Orchestrator with LM Studio Integration"
    )
    parser.add_argument("--tasks", "-t", type=str, help="Tasks to execute")
    parser.add_argument("--sequential", action="store_true", help="Execute sequentially")
    parser.add_argument("--no-history", action="store_true", help="Don't save history")
    
    args = parser.parse_args()
    
    if not args.tasks:
        print("[INPUT] Enter tasks (one per line, empty line to finish):")
        lines = []
        while True:
            try:
                line = input("> ")
                if not line:
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print("\n[CANCELLED] Operation cancelled")
                return
        task_input = "\n".join(lines)
    else:
        task_input = args.tasks
    
    if not task_input:
        print("[ERROR] No tasks provided")
        return
    
    # Create orchestrator
    orchestrator = DevOrchestratorLM()
    
    # Run orchestration
    await orchestrator.run(
        task_input,
        parallel=not args.sequential,
        save_history=not args.no_history
    )

if __name__ == "__main__":
    asyncio.run(main())