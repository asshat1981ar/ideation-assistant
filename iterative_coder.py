#!/usr/bin/env python3
"""
Iterative Coding Engine
Advanced AI-powered code generation with continuous feedback and improvement
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import shutil
import re

@dataclass
class CodeGeneration:
    """Represents a single code generation task"""
    task_id: str
    description: str
    file_path: str
    code_content: str
    language: str
    framework: str
    dependencies: List[str]
    test_requirements: List[str]
    
@dataclass
class IterationResult:
    """Results from a single iteration"""
    iteration_number: int
    timestamp: datetime
    
    # Code generation
    files_created: List[str]
    files_modified: List[str]
    lines_of_code: int
    
    # Quality metrics
    syntax_errors: List[str]
    type_errors: List[str]
    linting_issues: List[str]
    test_results: Dict[str, Any]
    
    # Performance metrics
    generation_time: float
    compilation_time: float
    test_execution_time: float
    
    # Feedback and improvements
    ai_feedback: List[str]
    suggested_improvements: List[str]
    refactoring_opportunities: List[str]
    
    # Completion status
    completion_percentage: float
    quality_score: float
    is_iteration_successful: bool
    requires_human_review: bool

@dataclass
class ProjectContext:
    """Context information for the project being developed"""
    project_name: str
    project_type: str
    tech_stack: Dict[str, List[str]]
    target_features: List[str]
    quality_requirements: Dict[str, Any]
    constraints: Dict[str, Any]
    
    # Progress tracking
    completed_features: List[str] = None
    current_phase: str = "initialization"
    overall_progress: float = 0.0
    
    def __post_init__(self):
        if self.completed_features is None:
            self.completed_features = []

class IterativeCoder:
    """Advanced iterative coding engine with AI-powered development"""
    
    def __init__(self, workspace_dir: str = "./generated_projects"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        
        self.code_generators = {
            "frontend": FrontendGenerator(),
            "backend": BackendGenerator(),
            "database": DatabaseGenerator(),
            "testing": TestGenerator(),
            "infrastructure": InfrastructureGenerator()
        }
        
        self.quality_analyzer = CodeQualityAnalyzer()
        self.test_runner = TestRunner()
        self.ai_reviewer = AICodeReviewer()
        
        # Configuration
        self.config = {
            "max_iterations": 15,
            "quality_threshold": 0.8,
            "test_coverage_threshold": 0.85,
            "auto_fix_issues": True,
            "generate_documentation": True,
            "enable_ai_review": True
        }
    
    async def start_iterative_development(self, 
                                        project_context: ProjectContext) -> Dict[str, Any]:
        """Start the iterative development process"""
        
        print(f"🚀 Starting iterative development for: {project_context.project_name}")
        
        # Create project directory
        project_dir = self.workspace_dir / project_context.project_name.lower().replace(" ", "_")
        project_dir.mkdir(exist_ok=True)
        
        # Initialize project structure
        await self._initialize_project(project_dir, project_context)
        
        # Development iterations
        iteration_results = []
        current_context = project_context
        
        for iteration in range(self.config["max_iterations"]):
            print(f"\n🔄 Iteration {iteration + 1}/{self.config['max_iterations']}")
            
            iteration_result = await self._execute_development_iteration(
                project_dir, current_context, iteration
            )
            
            iteration_results.append(iteration_result)
            
            # Update context based on results
            current_context = await self._update_project_context(
                current_context, iteration_result
            )
            
            # Check completion criteria
            if await self._check_completion_criteria(iteration_result, current_context):
                print("✅ Project completion criteria met!")
                break
            
            # Check if human intervention is needed
            if iteration_result.requires_human_review:
                print("⏸️  Pausing for human review...")
                break
            
            # Brief pause between iterations
            await asyncio.sleep(1)
        
        # Generate final summary
        final_summary = await self._generate_final_summary(
            project_dir, current_context, iteration_results
        )
        
        return {
            "project_path": str(project_dir),
            "iterations": iteration_results,
            "final_context": current_context,
            "summary": final_summary
        }
    
    async def _initialize_project(self, 
                                project_dir: Path,
                                context: ProjectContext):
        """Initialize project structure and basic files"""
        
        print("📁 Initializing project structure...")
        
        # Create basic directory structure
        directories = self._get_project_directories(context)
        for directory in directories:
            (project_dir / directory).mkdir(parents=True, exist_ok=True)
        
        # Generate initial configuration files
        config_files = await self._generate_config_files(context)
        for file_path, content in config_files.items():
            with open(project_dir / file_path, 'w') as f:
                f.write(content)
        
        # Initialize version control
        if (project_dir / ".git").exists():
            subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        
        print(f"✅ Project structure initialized at {project_dir}")
    
    def _get_project_directories(self, context: ProjectContext) -> List[str]:
        """Get required directory structure based on project type"""
        
        base_dirs = ["src", "tests", "docs", "config"]
        
        if context.project_type == "web_app":
            return base_dirs + [
                "src/components", "src/pages", "src/services", "src/utils",
                "src/styles", "public", "tests/unit", "tests/integration"
            ]
        elif context.project_type == "api_service":
            return base_dirs + [
                "src/routes", "src/models", "src/services", "src/middleware",
                "src/utils", "tests/unit", "tests/integration", "migrations"
            ]
        elif context.project_type == "cli_tool":
            return base_dirs + [
                "src/commands", "src/utils", "tests/unit", "bin"
            ]
        else:
            return base_dirs
    
    async def _generate_config_files(self, context: ProjectContext) -> Dict[str, str]:
        """Generate initial configuration files"""
        
        config_files = {}
        
        # Package.json for Node.js projects
        if "javascript" in context.tech_stack.get("frontend", []) or \
           "node.js" in context.tech_stack.get("backend", []):
            config_files["package.json"] = json.dumps({
                "name": context.project_name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "description": f"Generated {context.project_type}",
                "main": "src/index.js",
                "scripts": {
                    "start": "node src/index.js",
                    "dev": "nodemon src/index.js",
                    "test": "jest",
                    "lint": "eslint src/",
                    "build": "webpack --mode production"
                },
                "dependencies": {},
                "devDependencies": {
                    "jest": "^29.0.0",
                    "eslint": "^8.0.0",
                    "nodemon": "^2.0.0"
                }
            }, indent=2)
        
        # Requirements.txt for Python projects  
        if "python" in context.tech_stack.get("backend", []):
            requirements = [
                "fastapi>=0.100.0",
                "uvicorn>=0.23.0", 
                "pydantic>=2.0.0",
                "pytest>=7.0.0",
                "pytest-asyncio>=0.21.0"
            ]
            config_files["requirements.txt"] = "\n".join(requirements)
        
        # Docker configuration
        if "docker" in context.tech_stack.get("infrastructure", []):
            config_files["Dockerfile"] = self._generate_dockerfile(context)
            config_files["docker-compose.yml"] = self._generate_docker_compose(context)
        
        # README.md
        config_files["README.md"] = self._generate_readme(context)
        
        # .gitignore
        config_files[".gitignore"] = self._generate_gitignore(context)
        
        return config_files
    
    def _generate_dockerfile(self, context: ProjectContext) -> str:
        """Generate Dockerfile based on tech stack"""
        
        if "python" in context.tech_stack.get("backend", []):
            return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        elif "node.js" in context.tech_stack.get("backend", []):
            return """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""
        else:
            return "# Dockerfile template"
    
    def _generate_docker_compose(self, context: ProjectContext) -> str:
        """Generate docker-compose.yml"""
        
        return f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=development
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: {context.project_name.lower()}
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
    
    def _generate_readme(self, context: ProjectContext) -> str:
        """Generate README.md"""
        
        return f"""# {context.project_name}

{context.project_type.replace('_', ' ').title()} generated by Smart Coding Engine

## Features

{chr(10).join(f"- {feature}" for feature in context.target_features)}

## Tech Stack

**Frontend:** {', '.join(context.tech_stack.get('frontend', []))}
**Backend:** {', '.join(context.tech_stack.get('backend', []))}
**Database:** {', '.join(context.tech_stack.get('database', []))}

## Getting Started

1. Install dependencies
2. Configure environment variables
3. Run development server
4. Open application in browser

## Development

- `npm run dev` - Start development server
- `npm test` - Run tests
- `npm run build` - Build for production

## Generated by Smart Coding Engine

This project was automatically generated using AI-powered iterative development.
"""
    
    def _generate_gitignore(self, context: ProjectContext) -> str:
        """Generate .gitignore file"""
        
        gitignore_content = """# Dependencies
node_modules/
venv/
env/
.env

# Build outputs
dist/
build/
*.pyc
__pycache__/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Coverage reports
coverage/
.coverage
.nyc_output
"""
        return gitignore_content
    
    async def _execute_development_iteration(self, 
                                           project_dir: Path,
                                           context: ProjectContext,
                                           iteration_number: int) -> IterationResult:
        """Execute a single development iteration"""
        
        start_time = datetime.now()
        
        # Determine current development phase
        current_phase = self._determine_current_phase(context, iteration_number)
        
        # Generate code for current phase
        generation_results = await self._generate_code_for_phase(
            project_dir, context, current_phase
        )
        
        # Analyze code quality
        quality_results = await self._analyze_code_quality(
            project_dir, generation_results
        )
        
        # Run tests
        test_results = await self._run_tests(project_dir, context)
        
        # Get AI feedback
        ai_feedback = await self._get_ai_feedback(
            generation_results, quality_results, test_results
        )
        
        # Calculate metrics
        completion_percentage = self._calculate_completion_percentage(
            context, generation_results
        )
        quality_score = self._calculate_quality_score(quality_results, test_results)
        
        # Determine if human review is needed
        requires_human_review = (
            quality_score < self.config["quality_threshold"] or
            len(quality_results["critical_issues"]) > 0 or
            completion_percentage > 80
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        return IterationResult(
            iteration_number=iteration_number + 1,
            timestamp=start_time,
            files_created=generation_results["files_created"],
            files_modified=generation_results["files_modified"],
            lines_of_code=generation_results["lines_of_code"],
            syntax_errors=quality_results["syntax_errors"],
            type_errors=quality_results["type_errors"],
            linting_issues=quality_results["linting_issues"],
            test_results=test_results,
            generation_time=generation_time,
            compilation_time=quality_results["compilation_time"],
            test_execution_time=test_results["execution_time"],
            ai_feedback=ai_feedback["feedback"],
            suggested_improvements=ai_feedback["improvements"],
            refactoring_opportunities=ai_feedback["refactoring"],
            completion_percentage=completion_percentage,
            quality_score=quality_score,
            is_iteration_successful=quality_score >= 0.7,
            requires_human_review=requires_human_review
        )
    
    def _determine_current_phase(self, context: ProjectContext, iteration: int) -> str:
        """Determine current development phase"""
        
        phases = [
            "setup", "models", "api", "frontend", "integration", 
            "testing", "optimization", "documentation", "deployment"
        ]
        
        phase_index = min(iteration // 2, len(phases) - 1)
        return phases[phase_index]
    
    async def _generate_code_for_phase(self, 
                                     project_dir: Path,
                                     context: ProjectContext,
                                     phase: str) -> Dict[str, Any]:
        """Generate code for the current development phase"""
        
        print(f"  🏗️  Generating code for phase: {phase}")
        
        results = {
            "files_created": [],
            "files_modified": [],
            "lines_of_code": 0,
            "generated_components": []
        }
        
        if phase == "models":
            # Generate data models
            if "python" in context.tech_stack.get("backend", []):
                model_code = await self.code_generators["backend"].generate_models(context)
                model_file = project_dir / "src" / "models.py"
                with open(model_file, 'w') as f:
                    f.write(model_code)
                results["files_created"].append(str(model_file))
                results["lines_of_code"] += len(model_code.splitlines())
        
        elif phase == "api":
            # Generate API endpoints
            if "fastapi" in context.tech_stack.get("backend", []):
                api_code = await self.code_generators["backend"].generate_api_endpoints(context)
                api_file = project_dir / "src" / "main.py"
                with open(api_file, 'w') as f:
                    f.write(api_code)
                results["files_created"].append(str(api_file))
                results["lines_of_code"] += len(api_code.splitlines())
        
        elif phase == "frontend":
            # Generate frontend components
            if "react" in context.tech_stack.get("frontend", []):
                components = await self.code_generators["frontend"].generate_components(context)
                for component_name, component_code in components.items():
                    component_file = project_dir / "src" / "components" / f"{component_name}.jsx"
                    component_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(component_file, 'w') as f:
                        f.write(component_code)
                    results["files_created"].append(str(component_file))
                    results["lines_of_code"] += len(component_code.splitlines())
        
        elif phase == "testing":
            # Generate test files
            test_code = await self.code_generators["testing"].generate_tests(context, project_dir)
            for test_file_path, test_content in test_code.items():
                test_file = project_dir / test_file_path
                test_file.parent.mkdir(parents=True, exist_ok=True)
                with open(test_file, 'w') as f:
                    f.write(test_content)
                results["files_created"].append(str(test_file))
                results["lines_of_code"] += len(test_content.splitlines())
        
        return results
    
    async def _analyze_code_quality(self, 
                                  project_dir: Path,
                                  generation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code quality and identify issues"""
        
        print("  🔍 Analyzing code quality...")
        
        return await self.quality_analyzer.analyze_project(
            project_dir, generation_results["files_created"]
        )
    
    async def _run_tests(self, project_dir: Path, context: ProjectContext) -> Dict[str, Any]:
        """Run automated tests"""
        
        print("  🧪 Running tests...")
        
        return await self.test_runner.run_tests(project_dir, context)
    
    async def _get_ai_feedback(self, 
                             generation_results: Dict[str, Any],
                             quality_results: Dict[str, Any],
                             test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered feedback and suggestions"""
        
        if not self.config["enable_ai_review"]:
            return {"feedback": [], "improvements": [], "refactoring": []}
        
        return await self.ai_reviewer.review_iteration(
            generation_results, quality_results, test_results
        )
    
    def _calculate_completion_percentage(self, 
                                       context: ProjectContext,
                                       generation_results: Dict[str, Any]) -> float:
        """Calculate project completion percentage"""
        
        target_features = len(context.target_features)
        completed_features = len(context.completed_features)
        
        feature_completion = (completed_features / target_features) * 100 if target_features > 0 else 0
        
        # Factor in code generation progress
        files_generated = len(generation_results["files_created"])
        expected_files = self._estimate_expected_files(context)
        file_completion = (files_generated / expected_files) * 100 if expected_files > 0 else 0
        
        return min(100, (feature_completion * 0.6 + file_completion * 0.4))
    
    def _estimate_expected_files(self, context: ProjectContext) -> int:
        """Estimate expected number of files for project"""
        
        base_files = 10  # Basic config and structure files
        
        if context.project_type == "web_app":
            return base_files + len(context.target_features) * 3  # Component, test, style
        elif context.project_type == "api_service":
            return base_files + len(context.target_features) * 2  # Route, test
        else:
            return base_files + len(context.target_features)
    
    def _calculate_quality_score(self, 
                               quality_results: Dict[str, Any],
                               test_results: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        
        # Quality metrics scoring
        syntax_score = 1.0 if len(quality_results["syntax_errors"]) == 0 else 0.5
        linting_score = max(0, 1.0 - (len(quality_results["linting_issues"]) * 0.1))
        
        # Test metrics scoring
        test_coverage = test_results.get("coverage", 0)
        test_score = test_coverage / 100 if test_coverage > 0 else 0
        
        # Weighted average
        quality_score = (syntax_score * 0.4 + linting_score * 0.3 + test_score * 0.3)
        
        return min(1.0, quality_score)
    
    async def _update_project_context(self, 
                                    context: ProjectContext,
                                    iteration_result: IterationResult) -> ProjectContext:
        """Update project context based on iteration results"""
        
        # Update progress
        context.overall_progress = iteration_result.completion_percentage
        
        # Update completed features based on generated files
        if iteration_result.completion_percentage > context.overall_progress:
            # Simulate feature completion based on files generated
            features_to_add = max(0, int(iteration_result.completion_percentage / 20) - len(context.completed_features))
            remaining_features = [f for f in context.target_features if f not in context.completed_features]
            
            for i in range(min(features_to_add, len(remaining_features))):
                context.completed_features.append(remaining_features[i])
        
        return context
    
    async def _check_completion_criteria(self, 
                                       iteration_result: IterationResult,
                                       context: ProjectContext) -> bool:
        """Check if project completion criteria are met"""
        
        criteria_met = (
            iteration_result.completion_percentage >= 90 and
            iteration_result.quality_score >= self.config["quality_threshold"] and
            len(iteration_result.syntax_errors) == 0 and
            iteration_result.test_results.get("coverage", 0) >= self.config["test_coverage_threshold"] * 100
        )
        
        return criteria_met
    
    async def _generate_final_summary(self, 
                                    project_dir: Path,
                                    context: ProjectContext,
                                    iteration_results: List[IterationResult]) -> Dict[str, Any]:
        """Generate final project summary"""
        
        total_files = sum(len(r.files_created) for r in iteration_results)
        total_lines = sum(r.lines_of_code for r in iteration_results)
        avg_quality = sum(r.quality_score for r in iteration_results) / len(iteration_results)
        
        return {
            "project_name": context.project_name,
            "total_iterations": len(iteration_results),
            "completion_percentage": context.overall_progress,
            "files_generated": total_files,
            "lines_of_code": total_lines,
            "average_quality_score": avg_quality,
            "features_completed": len(context.completed_features),
            "features_remaining": len(context.target_features) - len(context.completed_features),
            "final_recommendation": self._generate_final_recommendation(context, iteration_results)
        }
    
    def _generate_final_recommendation(self, 
                                     context: ProjectContext,
                                     iteration_results: List[IterationResult]) -> str:
        """Generate final recommendation"""
        
        if context.overall_progress >= 90:
            return "🎉 Project is ready for deployment with high confidence"
        elif context.overall_progress >= 70:
            return "✅ Project is mostly complete, requires minor finishing touches"
        elif context.overall_progress >= 50:
            return "⚠️ Project has good foundation, needs additional development"
        else:
            return "🔄 Project requires significant additional development"

class FrontendGenerator:
    """Frontend code generator"""
    
    async def generate_components(self, context: ProjectContext) -> Dict[str, str]:
        """Generate React components"""
        
        components = {}
        
        # Generate App component
        components["App"] = """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {}</h1>
        <p>Generated by Smart Coding Engine</p>
      </header>
      <main>
        {/* Main content will be added here */}
      </main>
    </div>
  );
}

export default App;
""".format(context.project_name)
        
        # Generate components for each feature
        for feature in context.target_features:
            component_name = feature.replace(" ", "").title()
            components[component_name] = f"""import React, {{ useState, useEffect }} from 'react';

const {component_name} = () => {{
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {{
    // Fetch data for {feature}
    fetchData();
  }}, []);

  const fetchData = async () => {{
    try {{
      // API call would go here
      setData({{ message: '{feature} data loaded' }});
    }} catch (error) {{
      console.error('Error fetching {feature} data:', error);
    }} finally {{
      setLoading(false);
    }}
  }};

  if (loading) {{
    return <div>Loading {feature}...</div>;
  }}

  return (
    <div className="{feature.lower().replace(' ', '-')}-container">
      <h2>{feature}</h2>
      {{data && <p>{{data.message}}</p>}}
    </div>
  );
}};

export default {component_name};
"""
        
        return components

class BackendGenerator:
    """Backend code generator"""
    
    async def generate_models(self, context: ProjectContext) -> str:
        """Generate data models"""
        
        models_code = """from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BaseEntity(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

"""
        
        # Generate models for each feature
        for feature in context.target_features:
            model_name = feature.replace(" ", "").title()
            models_code += f"""
class {model_name}(BaseEntity):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True

class {model_name}Create(BaseModel):
    name: str
    description: Optional[str] = None

class {model_name}Update(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
"""
        
        return models_code
    
    async def generate_api_endpoints(self, context: ProjectContext) -> str:
        """Generate FastAPI endpoints"""
        
        api_code = """from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

app = FastAPI(
    title="{}",
    description="Generated by Smart Coding Engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"message": "Welcome to {} API"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}}

""".format(context.project_name, context.project_name)
        
        # Generate endpoints for each feature
        for feature in context.target_features:
            endpoint_name = feature.lower().replace(" ", "_")
            model_name = feature.replace(" ", "").title()
            
            api_code += f"""
@app.get("/{endpoint_name}")
async def get_{endpoint_name}():
    return {{"message": "Get all {feature.lower()}"}}

@app.post("/{endpoint_name}")
async def create_{endpoint_name}(item: dict):
    return {{"message": "Created {feature.lower()}", "data": item}}

@app.get("/{endpoint_name}/{{item_id}}")
async def get_{endpoint_name}_by_id(item_id: int):
    return {{"message": f"Get {feature.lower()} {{item_id}}"}}

@app.put("/{endpoint_name}/{{item_id}}")
async def update_{endpoint_name}(item_id: int, item: dict):
    return {{"message": f"Updated {feature.lower()} {{item_id}}", "data": item}}

@app.delete("/{endpoint_name}/{{item_id}}")
async def delete_{endpoint_name}(item_id: int):
    return {{"message": f"Deleted {feature.lower()} {{item_id}}"}}
"""
        
        api_code += """
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        return api_code

class DatabaseGenerator:
    """Database code generator"""
    
    async def generate_schema(self, context: ProjectContext) -> str:
        """Generate database schema"""
        return "-- Database schema generation placeholder"

class TestGenerator:
    """Test code generator"""
    
    async def generate_tests(self, context: ProjectContext, project_dir: Path) -> Dict[str, str]:
        """Generate test files"""
        
        tests = {}
        
        # Generate API tests
        if "python" in context.tech_stack.get("backend", []):
            tests["tests/test_api.py"] = """import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

"""
            
            # Add tests for each feature
            for feature in context.target_features:
                endpoint_name = feature.lower().replace(" ", "_")
                tests["tests/test_api.py"] += f"""
def test_get_{endpoint_name}():
    response = client.get("/{endpoint_name}")
    assert response.status_code == 200

def test_create_{endpoint_name}():
    test_data = {{"name": "Test {feature}", "description": "Test description"}}
    response = client.post("/{endpoint_name}", json=test_data)
    assert response.status_code == 200
"""
        
        # Generate frontend tests
        if "react" in context.tech_stack.get("frontend", []):
            tests["tests/App.test.js"] = """import { render, screen } from '@testing-library/react';
import App from '../src/components/App';

test('renders welcome message', () => {
  render(<App />);
  const welcomeElement = screen.getByText(/Welcome to/i);
  expect(welcomeElement).toBeInTheDocument();
});

test('renders generated by message', () => {
  render(<App />);
  const generatedElement = screen.getByText(/Generated by Smart Coding Engine/i);
  expect(generatedElement).toBeInTheDocument();
});
"""
        
        return tests

class InfrastructureGenerator:
    """Infrastructure code generator"""
    
    async def generate_deployment_configs(self, context: ProjectContext) -> Dict[str, str]:
        """Generate deployment configurations"""
        return {}

class CodeQualityAnalyzer:
    """Analyze code quality and identify issues"""
    
    async def analyze_project(self, project_dir: Path, files: List[str]) -> Dict[str, Any]:
        """Analyze project code quality"""
        
        # Mock analysis - in production, integrate with real linting tools
        return {
            "syntax_errors": [],
            "type_errors": [],
            "linting_issues": ["Unused import in src/main.py:1"],
            "critical_issues": [],
            "compilation_time": 0.5,
            "code_coverage": 0.85
        }

class TestRunner:
    """Run automated tests"""
    
    async def run_tests(self, project_dir: Path, context: ProjectContext) -> Dict[str, Any]:
        """Run all available tests"""
        
        # Mock test results - in production, run actual test suites
        return {
            "total_tests": 8,
            "passed": 7,
            "failed": 1,
            "coverage": 85,
            "execution_time": 2.3,
            "failed_tests": ["test_create_user_validation"]
        }

class AICodeReviewer:
    """AI-powered code review and feedback"""
    
    async def review_iteration(self, 
                             generation_results: Dict[str, Any],
                             quality_results: Dict[str, Any],
                             test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Provide AI-powered code review"""
        
        # Mock AI feedback - in production, integrate with LLM APIs
        return {
            "feedback": [
                "Code structure follows best practices",
                "API endpoints are well-organized",
                "Test coverage could be improved"
            ],
            "improvements": [
                "Add input validation to API endpoints",
                "Implement error handling middleware",
                "Add logging for debugging"
            ],
            "refactoring": [
                "Extract common database operations into repository pattern",
                "Consolidate similar API endpoints",
                "Improve component prop types"
            ]
        }

async def main():
    """Demo the iterative coder"""
    
    print("🚀 Iterative Coding Engine Demo")
    print("=" * 50)
    
    # Create iterative coder
    coder = IterativeCoder()
    
    # Define project context
    context = ProjectContext(
        project_name="Task Management App",
        project_type="web_app",
        tech_stack={
            "frontend": ["react", "javascript"],
            "backend": ["python", "fastapi"],
            "database": ["postgresql"],
            "infrastructure": ["docker"]
        },
        target_features=[
            "User Authentication",
            "Task Management", 
            "Project Organization",
            "Team Collaboration"
        ],
        quality_requirements={
            "test_coverage": 0.85,
            "performance": "< 200ms API response",
            "security": "JWT authentication"
        },
        constraints={
            "timeline": "4 weeks",
            "team_size": 3,
            "budget": "medium"
        }
    )
    
    # Start iterative development
    results = await coder.start_iterative_development(context)
    
    print(f"\n✅ Development completed!")
    print(f"   Project Path: {results['project_path']}")
    print(f"   Total Iterations: {len(results['iterations'])}")
    print(f"   Final Progress: {results['final_context'].overall_progress:.1f}%")
    print(f"   Recommendation: {results['summary']['final_recommendation']}")

if __name__ == "__main__":
    asyncio.run(main())