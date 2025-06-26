#!/usr/bin/env python3
"""
Tool Integration and Orchestration
Complete integration of all tools and capabilities
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

# Import all our modules
from deepseek_client import DeepSeekClient, PlanningContext
from mcp_server_config import MCPServerManager, EnhancedMCPIntegration
from filesystem_integration import FilesystemManager
from github_integration import GitHubIntegration
from code_execution import CodeInteractionEngine
from enhanced_planning_mode import EnhancedPlanningMode
from secure_config import SecureConfig, get_github_credentials, get_api_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ToolCapability:
    """Tool capability definition"""
    name: str
    description: str
    category: str
    available: bool
    required_config: List[str]
    tools: List[str]

@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    workflow_id: str
    name: str
    steps: List[Dict[str, Any]]
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = {}

class ToolOrchestrator:
    """Central orchestrator for all tools and capabilities"""
    
    def __init__(self, workspace_dir: str = "./orchestrator_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize configuration
        self.config = SecureConfig()
        
        # Initialize tool managers
        self.filesystem_manager = FilesystemManager(str(self.workspace_dir / "filesystem"))
        self.mcp_manager = MCPServerManager(str(self.workspace_dir / "mcp_config"))
        self.code_engine = CodeInteractionEngine(str(self.workspace_dir / "code_workspace"))
        
        # Will be initialized in async context
        self.deepseek_client = None
        self.github_integration = None
        self.planning_mode = None
        self.mcp_integration = None
        
        # Workflow tracking
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_history: List[WorkflowExecution] = []
        
        # Tool capabilities registry
        self.capabilities = self._register_capabilities()
    
    async def __aenter__(self):
        """Async context manager entry"""
        
        # Initialize async components
        deepseek_key = get_api_key("deepseek")
        if deepseek_key:
            self.deepseek_client = DeepSeekClient(deepseek_key)
            await self.deepseek_client.__aenter__()
        
        github_username, github_token = get_github_credentials()
        if github_username and github_token:
            self.github_integration = GitHubIntegration(github_token)
            await self.github_integration.__aenter__()
        
        self.planning_mode = EnhancedPlanningMode(str(self.workspace_dir / "planning"))
        await self.planning_mode.__aenter__()
        
        self.mcp_integration = EnhancedMCPIntegration(self.mcp_manager)
        
        # Start essential MCP servers
        await self._initialize_infrastructure()
        
        logger.info("🚀 Tool Orchestrator initialized")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        
        if self.deepseek_client:
            await self.deepseek_client.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.github_integration:
            await self.github_integration.__aexit__(exc_type, exc_val, exc_tb)
        
        if self.planning_mode:
            await self.planning_mode.__aexit__(exc_type, exc_val, exc_tb)
        
        # Stop MCP servers
        await self.mcp_manager.stop_all_servers()
    
    def _register_capabilities(self) -> Dict[str, ToolCapability]:
        """Register all available tool capabilities"""
        
        capabilities = {}
        
        # Filesystem capabilities
        capabilities["filesystem_operations"] = ToolCapability(
            name="Filesystem Operations",
            description="File and directory management, project scanning, search",
            category="filesystem",
            available=True,
            required_config=[],
            tools=["scan_project", "create_structure", "search_files", "copy_files"]
        )
        
        # GitHub capabilities
        capabilities["github_integration"] = ToolCapability(
            name="GitHub Integration", 
            description="Repository management, pull requests, issues",
            category="version_control",
            available=bool(get_github_credentials()[0]),
            required_config=["github_username", "github_token"],
            tools=["create_repo", "clone_repo", "create_pr", "manage_issues"]
        )
        
        # Code execution capabilities
        capabilities["code_execution"] = ToolCapability(
            name="Code Execution",
            description="Safe code execution, testing, building",
            category="development",
            available=True,
            required_config=[],
            tools=["execute_code", "run_tests", "build_project", "interactive_session"]
        )
        
        # AI planning capabilities
        capabilities["ai_planning"] = ToolCapability(
            name="AI-Powered Planning",
            description="Intelligent project planning with iteration and refinement",
            category="planning",
            available=bool(get_api_key("deepseek")),
            required_config=["deepseek_api_key"],
            tools=["create_plan", "iterate_plan", "analyze_requirements"]
        )
        
        # MCP server capabilities
        capabilities["mcp_servers"] = ToolCapability(
            name="MCP Server Integration",
            description="Model Context Protocol servers for enhanced functionality",
            category="integration",
            available=True,
            required_config=[],
            tools=["search_web", "database_operations", "api_integration"]
        )
        
        return capabilities
    
    async def _initialize_infrastructure(self):
        """Initialize essential infrastructure"""
        
        logger.info("🔧 Initializing infrastructure...")
        
        # Start essential MCP servers
        essential_servers = ["filesystem", "planning"]
        for server_name in essential_servers:
            if server_name in self.mcp_manager.servers:
                await self.mcp_manager.start_server(server_name)
        
        # Health check
        if self.mcp_integration:
            health = await self.mcp_integration.health_check()
            logger.info(f"MCP Status: {health['overall_status']}")
    
    async def execute_complete_workflow(self, 
                                      workflow_name: str,
                                      requirements: Dict[str, Any]) -> str:
        """Execute a complete end-to-end workflow"""
        
        workflow_id = f"workflow_{int(datetime.now().timestamp())}"
        
        workflow = WorkflowExecution(
            workflow_id=workflow_id,
            name=workflow_name,
            steps=[],
            status="running",
            started_at=datetime.now()
        )
        
        self.active_workflows[workflow_id] = workflow
        
        logger.info(f"🚀 Starting workflow: {workflow_name} ({workflow_id})")
        
        try:
            if workflow_name == "complete_project_development":
                await self._execute_project_development_workflow(workflow, requirements)
            elif workflow_name == "ai_planning_with_implementation":
                await self._execute_planning_implementation_workflow(workflow, requirements)
            elif workflow_name == "code_analysis_and_improvement":
                await self._execute_code_analysis_workflow(workflow, requirements)
            else:
                raise ValueError(f"Unknown workflow: {workflow_name}")
            
            workflow.status = "completed"
            workflow.completed_at = datetime.now()
            
        except Exception as e:
            workflow.status = "failed"
            workflow.results["error"] = str(e)
            logger.error(f"Workflow failed: {e}")
        
        finally:
            # Move to history
            self.workflow_history.append(workflow)
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
        
        logger.info(f"✅ Workflow completed: {workflow_id}")
        return workflow_id
    
    async def _execute_project_development_workflow(self, 
                                                  workflow: WorkflowExecution,
                                                  requirements: Dict[str, Any]):
        """Execute complete project development workflow"""
        
        # Step 1: AI-powered planning
        workflow.steps.append({"step": "ai_planning", "status": "running"})
        
        if self.planning_mode:
            session_id = await self.planning_mode.start_planning_session(
                domain=requirements.get("domain", "software_development"),
                requirements=requirements,
                max_iterations=3
            )
            workflow.results["planning_session"] = session_id
            workflow.steps[-1]["status"] = "completed"
        
        # Step 2: Create project structure
        workflow.steps.append({"step": "create_structure", "status": "running"})
        
        project_name = requirements.get("project_name", "generated_project")
        project_path = await self.filesystem_manager.create_project_structure(
            project_name=project_name,
            template=requirements.get("template", "default")
        )
        workflow.results["project_path"] = project_path
        workflow.steps[-1]["status"] = "completed"
        
        # Step 3: GitHub repository creation
        if self.github_integration and requirements.get("create_github_repo", False):
            workflow.steps.append({"step": "github_repo", "status": "running"})
            
            github_result = await self.github_integration.create_project_with_github(
                project_name=project_name,
                local_path=project_path,
                description=requirements.get("description", ""),
                private=requirements.get("private", False)
            )
            workflow.results["github_repo"] = github_result
            workflow.steps[-1]["status"] = "completed"
        
        # Step 4: Code generation and implementation
        workflow.steps.append({"step": "code_implementation", "status": "running"})
        
        if "code_files" in requirements:
            project_config = {
                "name": project_name,
                "language": requirements.get("language", "python"),
                "files": requirements["code_files"],
                "main_file": requirements.get("main_file"),
                "build": requirements.get("build", False)
            }
            
            implementation_result = await self.code_engine.create_and_run_project(project_config)
            workflow.results["implementation"] = implementation_result
        
        workflow.steps[-1]["status"] = "completed"
        
        # Step 5: Testing and quality checks
        if requirements.get("run_tests", False):
            workflow.steps.append({"step": "testing", "status": "running"})
            
            # Run quality checks
            quality_result = await self.code_engine.build_system.run_quality_checks(
                project_path,
                requirements.get("language", "python")
            )
            workflow.results["quality_checks"] = quality_result
            workflow.steps[-1]["status"] = "completed"
    
    async def _execute_planning_implementation_workflow(self, 
                                                      workflow: WorkflowExecution,
                                                      requirements: Dict[str, Any]):
        """Execute AI planning with implementation workflow"""
        
        # Step 1: Enhanced planning with iteration
        workflow.steps.append({"step": "enhanced_planning", "status": "running"})
        
        if self.planning_mode:
            session_id = await self.planning_mode.start_planning_session(
                domain=requirements.get("domain", "software_development"),
                requirements=requirements,
                max_iterations=requirements.get("planning_iterations", 3)
            )
            workflow.results["planning_session"] = session_id
        
        workflow.steps[-1]["status"] = "completed"
        
        # Step 2: MCP-enhanced analysis
        workflow.steps.append({"step": "mcp_analysis", "status": "running"})
        
        if self.mcp_integration:
            mcp_result = await self.mcp_integration.execute_planning_workflow(requirements)
            workflow.results["mcp_analysis"] = mcp_result
        
        workflow.steps[-1]["status"] = "completed"
        
        # Step 3: DeepSeek reasoning
        if self.deepseek_client:
            workflow.steps.append({"step": "deepseek_reasoning", "status": "running"})
            
            analysis_result = await self.deepseek_client.deep_analysis(
                subject=requirements.get("domain", "project"),
                context=requirements,
                analysis_type="comprehensive"
            )
            workflow.results["deepseek_analysis"] = analysis_result
            workflow.steps[-1]["status"] = "completed"
    
    async def _execute_code_analysis_workflow(self, 
                                            workflow: WorkflowExecution,
                                            requirements: Dict[str, Any]):
        """Execute code analysis and improvement workflow"""
        
        # Step 1: Project scanning
        workflow.steps.append({"step": "project_scan", "status": "running"})
        
        project_path = requirements.get("project_path", ".")
        project_structure = await self.filesystem_manager.scan_project(project_path)
        workflow.results["project_structure"] = asdict(project_structure)
        workflow.steps[-1]["status"] = "completed"
        
        # Step 2: Code quality analysis
        workflow.steps.append({"step": "quality_analysis", "status": "running"})
        
        quality_checks = await self.code_engine.build_system.run_quality_checks(
            project_path,
            requirements.get("language", "python")
        )
        workflow.results["quality_checks"] = quality_checks
        workflow.steps[-1]["status"] = "completed"
        
        # Step 3: AI-powered code suggestions
        if self.deepseek_client:
            workflow.steps.append({"step": "ai_suggestions", "status": "running"})
            
            # Analyze code with AI
            analysis_context = {
                "project_structure": asdict(project_structure),
                "quality_checks": quality_checks,
                "improvement_goals": requirements.get("improvement_goals", [])
            }
            
            suggestions = await self.deepseek_client.deep_analysis(
                subject="code_improvement",
                context=analysis_context,
                analysis_type="code_optimization"
            )
            workflow.results["ai_suggestions"] = suggestions
            workflow.steps[-1]["status"] = "completed"
    
    def get_available_capabilities(self) -> List[ToolCapability]:
        """Get list of available capabilities"""
        
        return [cap for cap in self.capabilities.values() if cap.available]
    
    def get_capability_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all capabilities"""
        
        status = {}
        
        for name, capability in self.capabilities.items():
            status[name] = {
                "available": capability.available,
                "description": capability.description,
                "category": capability.category,
                "tools_count": len(capability.tools),
                "missing_config": [
                    config for config in capability.required_config
                    if not self.config.get(config)
                ]
            }
        
        return status
    
    async def execute_tool_command(self, 
                                 tool_name: str,
                                 command: str,
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool command"""
        
        logger.info(f"🔧 Executing {tool_name}.{command}")
        
        try:
            if tool_name == "filesystem":
                return await self._execute_filesystem_command(command, parameters)
            elif tool_name == "github":
                return await self._execute_github_command(command, parameters)
            elif tool_name == "code":
                return await self._execute_code_command(command, parameters)
            elif tool_name == "planning":
                return await self._execute_planning_command(command, parameters)
            elif tool_name == "mcp":
                return await self._execute_mcp_command(command, parameters)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            logger.error(f"Tool command failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_filesystem_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute filesystem command"""
        
        if command == "scan_project":
            result = await self.filesystem_manager.scan_project(
                params["path"],
                params.get("include_hidden", False)
            )
            return {"success": True, "result": asdict(result)}
        
        elif command == "create_structure":
            result = await self.filesystem_manager.create_project_structure(
                params["name"],
                params.get("template", "default")
            )
            return {"success": True, "project_path": result}
        
        elif command == "search_files":
            result = await self.filesystem_manager.search_in_files(
                params["path"],
                params["query"],
                params.get("patterns", ["*"])
            )
            return {"success": True, "matches": result}
        
        else:
            raise ValueError(f"Unknown filesystem command: {command}")
    
    async def _execute_github_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub command"""
        
        if not self.github_integration:
            return {"success": False, "error": "GitHub integration not available"}
        
        if command == "create_repo":
            result = await self.github_integration.github_manager.create_repository(
                params["name"],
                params.get("description", ""),
                params.get("private", False)
            )
            return {"success": True, "repository": asdict(result)}
        
        elif command == "create_pr":
            result = await self.github_integration.github_manager.create_pull_request(
                params["owner"],
                params["repo"],
                params["title"],
                params["head"],
                params["base"],
                params.get("description", "")
            )
            return {"success": True, "pull_request": asdict(result)}
        
        else:
            raise ValueError(f"Unknown GitHub command: {command}")
    
    async def _execute_code_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code command"""
        
        if command == "execute":
            result = await self.code_engine.executor.execute_code(
                params["code"],
                params["language"],
                params.get("timeout", 30)
            )
            return {"success": True, "result": asdict(result)}
        
        elif command == "run_tests":
            if params["language"].lower() == "python":
                result = await self.code_engine.test_runner.run_python_tests(
                    params["test_directory"],
                    params.get("pattern", "test_*.py")
                )
            else:
                result = []
            
            return {"success": True, "test_results": [asdict(r) for r in result]}
        
        else:
            raise ValueError(f"Unknown code command: {command}")
    
    async def _execute_planning_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning command"""
        
        if not self.planning_mode:
            return {"success": False, "error": "Planning mode not available"}
        
        if command == "create_session":
            session_id = await self.planning_mode.start_planning_session(
                params["domain"],
                params["requirements"],
                params.get("max_iterations", 3)
            )
            return {"success": True, "session_id": session_id}
        
        elif command == "get_status":
            status = self.planning_mode.get_session_status(params["session_id"])
            return {"success": True, "status": status}
        
        else:
            raise ValueError(f"Unknown planning command: {command}")
    
    async def _execute_mcp_command(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP command"""
        
        if command == "call_tool":
            result = await self.mcp_manager.call_tool(
                params["tool_name"],
                **params.get("args", {})
            )
            return {"success": True, "result": result}
        
        elif command == "health_check":
            result = await self.mcp_integration.health_check()
            return {"success": True, "health": result}
        
        else:
            raise ValueError(f"Unknown MCP command: {command}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status"""
        
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                "status": workflow.status,
                "steps_completed": len([s for s in workflow.steps if s.get("status") == "completed"]),
                "total_steps": len(workflow.steps),
                "started_at": workflow.started_at.isoformat(),
                "current_step": next((s for s in workflow.steps if s.get("status") == "running"), None)
            }
        
        # Check history
        for workflow in self.workflow_history:
            if workflow.workflow_id == workflow_id:
                return {
                    "status": workflow.status,
                    "steps_completed": len(workflow.steps),
                    "total_steps": len(workflow.steps),
                    "started_at": workflow.started_at.isoformat(),
                    "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                    "results": workflow.results
                }
        
        return {"error": "Workflow not found"}
    
    def display_system_status(self):
        """Display comprehensive system status"""
        
        print("\n" + "="*80)
        print("🎯 IDEATION ASSISTANT - SYSTEM STATUS")
        print("="*80)
        
        # Configuration status
        print(f"\n🔐 Configuration:")
        validations = self.config.validate_configuration()
        for key, valid in validations.items():
            status = "✅ Configured" if valid else "❌ Missing"
            print(f"   {key}: {status}")
        
        # Capabilities status
        print(f"\n🛠️  Capabilities:")
        capabilities_status = self.get_capability_status()
        for name, status in capabilities_status.items():
            available = "✅ Available" if status["available"] else "❌ Unavailable"
            print(f"   {name}: {available}")
            if status["missing_config"]:
                print(f"     Missing: {', '.join(status['missing_config'])}")
        
        # Active workflows
        print(f"\n🔄 Active Workflows: {len(self.active_workflows)}")
        for workflow_id, workflow in self.active_workflows.items():
            print(f"   {workflow_id}: {workflow.name} ({workflow.status})")
        
        # Recent history
        print(f"\n📋 Recent Workflows: {len(self.workflow_history[-5:])}")
        for workflow in self.workflow_history[-5:]:
            print(f"   {workflow.workflow_id}: {workflow.name} ({workflow.status})")

async def main():
    """Demo complete tool integration"""
    
    print("🚀 Complete Tool Integration Demo")
    print("=" * 50)
    
    async with ToolOrchestrator() as orchestrator:
        
        # Display system status
        orchestrator.display_system_status()
        
        # Demo 1: Check capabilities
        print("\n1. Available Capabilities:")
        capabilities = orchestrator.get_available_capabilities()
        for cap in capabilities:
            print(f"   • {cap.name}: {cap.description}")
        
        # Demo 2: Execute tool commands
        print("\n2. Executing tool commands...")
        
        # Filesystem command
        fs_result = await orchestrator.execute_tool_command(
            "filesystem",
            "scan_project",
            {"path": "."}
        )
        print(f"   Filesystem scan: {'✅ Success' if fs_result['success'] else '❌ Failed'}")
        
        # Code execution command
        code_result = await orchestrator.execute_tool_command(
            "code",
            "execute",
            {
                "code": "print('Hello from integrated tool system!')",
                "language": "python"
            }
        )
        print(f"   Code execution: {'✅ Success' if code_result['success'] else '❌ Failed'}")
        if code_result["success"]:
            print(f"   Output: {code_result['result']['stdout'].strip()}")
        
        # Demo 3: Complete workflow
        print("\n3. Executing complete workflow...")
        
        workflow_requirements = {
            "domain": "web_development",
            "project_name": "demo_web_app",
            "description": "A demo web application",
            "language": "python",
            "template": "web_app",
            "code_files": {
                "app.py": """
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello from the Integrated Tool System!</h1>'

if __name__ == '__main__':
    app.run(debug=True)
""",
                "requirements.txt": "flask>=2.0.0\n"
            },
            "main_file": "app.py",
            "create_github_repo": False,  # Set to True if GitHub is configured
            "run_tests": False,
            "build": False
        }
        
        workflow_id = await orchestrator.execute_complete_workflow(
            "complete_project_development",
            workflow_requirements
        )
        
        print(f"   Workflow ID: {workflow_id}")
        
        # Get workflow status
        status = orchestrator.get_workflow_status(workflow_id)
        print(f"   Status: {status['status']}")
        print(f"   Steps: {status['steps_completed']}/{status['total_steps']}")
        
        print("\n✅ Complete tool integration demo finished!")

if __name__ == "__main__":
    asyncio.run(main())
