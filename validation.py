#!/usr/bin/env python3
"""
Input Validation Module
Pydantic models for validating user inputs and API parameters
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, validator, Field
from enum import Enum

class LanguageType(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    SHELL = "shell"

class DomainType(str, Enum):
    """Supported development domains"""
    WEB_DEVELOPMENT = "web_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    DEVOPS = "devops"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    ECOMMERCE = "ecommerce"
    GAMING = "gaming"
    IOT = "iot"

class PlanningRequest(BaseModel):
    """Validation for planning requests"""
    domain: DomainType
    requirements: Dict[str, Any] = Field(default_factory=dict)
    iterations: int = Field(default=3, ge=1, le=10)
    target_market: Optional[str] = None
    expected_users: Optional[int] = Field(None, ge=1)
    
    @validator('requirements')
    def validate_requirements(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Requirements must be a dictionary')
        return v

class CodeExecutionRequest(BaseModel):
    """Validation for code execution requests"""
    code: str = Field(..., min_length=1, max_length=50000)
    language: LanguageType
    timeout: int = Field(default=30, ge=1, le=300)
    working_dir: Optional[str] = None
    environment: Dict[str, str] = Field(default_factory=dict)
    
    @validator('code')
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty or whitespace only')
        return v.strip()

class ProjectDevelopmentRequest(BaseModel):
    """Validation for project development requests"""
    name: str = Field(..., min_length=1, max_length=100)
    language: LanguageType
    description: Optional[str] = Field(None, max_length=500)
    template: str = Field(default="default")
    github: bool = Field(default=False)
    tests: bool = Field(default=False)
    build: bool = Field(default=False)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Project name must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()

class AnalysisRequest(BaseModel):
    """Validation for code analysis requests"""
    path: str = Field(..., min_length=1)
    language: Optional[LanguageType] = None
    include_hidden: bool = Field(default=False)
    improvement_goals: List[str] = Field(default_factory=list)
    
    @validator('path')
    def validate_path(cls, v):
        import os
        if not os.path.exists(v):
            raise ValueError(f'Path does not exist: {v}')
        return v

class GitHubRequest(BaseModel):
    """Validation for GitHub operations"""
    operation: str = Field(..., regex=r'^(create_repo|clone|push|pull|create_pr)$')
    repository: Optional[str] = None
    branch: str = Field(default="main")
    private: bool = Field(default=False)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('repository')
    def validate_repository(cls, v, values):
        if values.get('operation') in ['create_repo', 'clone'] and not v:
            raise ValueError('Repository name is required for this operation')
        return v

class WorkflowRequest(BaseModel):
    """Validation for workflow execution"""
    workflow_name: str = Field(..., regex=r'^(complete_project_development|ai_planning_with_implementation|code_analysis_and_improvement)$')
    requirements: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('requirements')
    def validate_requirements(cls, v, values):
        workflow_name = values.get('workflow_name')
        
        if workflow_name == 'complete_project_development':
            required_fields = ['project_name', 'language']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Field {field} is required for project development workflow')
        
        elif workflow_name == 'code_analysis_and_improvement':
            if 'project_path' not in v:
                raise ValueError('project_path is required for code analysis workflow')
        
        return v

class APIKeyValidation(BaseModel):
    """Validation for API keys"""
    service: str = Field(..., regex=r'^(deepseek|github|openai|anthropic)$')
    key: str = Field(..., min_length=10)
    
    @validator('key')
    def validate_key_format(cls, v, values):
        service = values.get('service')
        
        # Basic format validation for different services
        if service == 'deepseek' and not v.startswith('sk-'):
            raise ValueError('DeepSeek API key must start with "sk-"')
        elif service == 'github' and not (v.startswith('ghp_') or v.startswith('ghs_')):
            raise ValueError('GitHub token must start with "ghp_" or "ghs_"')
        elif service == 'openai' and not v.startswith('sk-'):
            raise ValueError('OpenAI API key must start with "sk-"')
        
        return v

def validate_request(request_type: str, data: Dict[str, Any]) -> BaseModel:
    """
    Validate request data based on type
    
    Args:
        request_type: Type of request to validate
        data: Request data to validate
        
    Returns:
        Validated Pydantic model instance
        
    Raises:
        ValidationError: If validation fails
    """
    validators = {
        'planning': PlanningRequest,
        'code_execution': CodeExecutionRequest,
        'project_development': ProjectDevelopmentRequest,
        'analysis': AnalysisRequest,
        'github': GitHubRequest,
        'workflow': WorkflowRequest,
        'api_key': APIKeyValidation
    }
    
    validator_class = validators.get(request_type)
    if not validator_class:
        raise ValueError(f'Unknown request type: {request_type}')
    
    return validator_class(**data)

# Error handling utilities
class ValidationResult:
    """Result of validation with success/error information"""
    
    def __init__(self, success: bool, data: Any = None, errors: List[str] = None):
        self.success = success
        self.data = data
        self.errors = errors or []

def safe_validate(request_type: str, data: Dict[str, Any]) -> ValidationResult:
    """
    Safely validate request with error handling
    
    Args:
        request_type: Type of request to validate
        data: Request data to validate
        
    Returns:
        ValidationResult with success status and data or errors
    """
    try:
        validated_data = validate_request(request_type, data)
        return ValidationResult(success=True, data=validated_data)
    except Exception as e:
        error_messages = []
        
        # Extract detailed error messages from Pydantic ValidationError
        if hasattr(e, 'errors'):
            for error in e.errors():
                field = ' -> '.join(str(loc) for loc in error['loc'])
                message = error['msg']
                error_messages.append(f"{field}: {message}")
        else:
            error_messages.append(str(e))
        
        return ValidationResult(success=False, errors=error_messages)

# Example usage and testing
if __name__ == "__main__":
    # Test planning request validation
    planning_data = {
        "domain": "web_development",
        "iterations": 3,
        "requirements": {"target_users": 1000}
    }
    
    result = safe_validate("planning", planning_data)
    if result.success:
        print("✅ Planning validation passed")
        print(f"Domain: {result.data.domain}")
        print(f"Iterations: {result.data.iterations}")
    else:
        print("❌ Planning validation failed:")
        for error in result.errors:
            print(f"  - {error}")
    
    # Test invalid code execution request
    invalid_code_data = {
        "code": "",  # Invalid: empty code
        "language": "python",
        "timeout": 500  # Invalid: too long
    }
    
    result = safe_validate("code_execution", invalid_code_data)
    if not result.success:
        print("\n❌ Code execution validation failed (as expected):")
        for error in result.errors:
            print(f"  - {error}")
