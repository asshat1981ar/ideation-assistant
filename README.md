# Ideation Assistant 🧠⚡

**Advanced AI-powered development tool with DeepSeek, MCP, and GitHub integration**

A comprehensive development assistant that combines AI-powered planning, iterative refinement, filesystem integration, GitHub automation, and safe code execution capabilities.

## 🌟 Features

### Core Capabilities
- **🧠 AI-Powered Planning**: DeepSeek integration for intelligent project planning and analysis
- **🔄 Iterative Refinement**: Multi-iteration planning with continuous improvement
- **📂 Filesystem Integration**: Advanced file operations, project scanning, and management
- **🐙 GitHub Integration**: Complete repository management, PR creation, and automation
- **⚡ Code Execution**: Safe code execution with sandboxing and build automation
- **🔧 MCP Server Integration**: Model Context Protocol servers for enhanced functionality
- **🛡️ Secure Configuration**: Proper credential management and security practices

### Advanced Features
- **🎯 Complete Workflows**: End-to-end project development automation
- **🔍 Code Analysis**: Quality checks, linting, and improvement suggestions
- **📊 Project Planning**: Multi-phase planning with resource estimation
- **🚀 Build Systems**: Automated building and testing for multiple languages
- **📈 Progress Tracking**: Comprehensive workflow and execution monitoring

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/asshat1981ar/ideation-assistant.git
cd ideation-assistant

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Set up your environment variables
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export GITHUB_USERNAME="your_github_username"
export GITHUB_TOKEN="your_github_personal_access_token"

# Or run the interactive setup
python main_interface.py setup
```

### 3. Usage

```bash
# Show system status
python main_interface.py status

# Create an AI-powered plan
python main_interface.py plan --domain="web_development" --iterations=3

# Develop a complete project
python main_interface.py develop --name="my_app" --language="python" --github

# Analyze existing code
python main_interface.py analyze --path="./my_project" --language="python"

# Execute code safely
python main_interface.py execute --language="python" --code="print('Hello World!')"

# Start interactive mode
python main_interface.py interactive
```

## 📋 Component Architecture

### Core Modules

1. **`main_interface.py`** - Main CLI interface and orchestration
2. **`tool_integration.py`** - Central tool orchestrator
3. **`enhanced_planning_mode.py`** - AI-powered planning with iteration
4. **`deepseek_client.py`** - DeepSeek API integration
5. **`github_integration.py`** - Complete GitHub automation
6. **`filesystem_integration.py`** - Advanced file operations
7. **`code_execution.py`** - Safe code execution and testing
8. **`mcp_server_config.py`** - MCP server management
9. **`secure_config.py`** - Security and credential management

### Legacy Modules (Enhanced)

- **`ideation_system.py`** - Feature ideation with market analysis
- **`framework_planner.py`** - Technology stack selection
- **`iterative_coder.py`** - Iterative development cycles
- **`main_engine.py`** - Original workflow orchestration

## 🔧 Configuration

### Environment Variables

```bash
# Required for AI features
DEEPSEEK_API_KEY="sk-your-key"

# Required for GitHub integration
GITHUB_USERNAME="your_username"
GITHUB_TOKEN="your_personal_access_token"

# Optional API keys
BRAVE_API_KEY="your_brave_search_key"
OPENAI_API_KEY="your_openai_key"

# Configuration paths
MCP_CONFIG_DIR="./mcp_config"
IDEATION_WORKSPACE="./workspace"
```

### Security Notes

- **Never commit API keys to repositories**
- Use environment variables or secure configuration files
- The tool includes built-in security checks and warnings
- Credentials are never stored in plaintext in code files

## 🎯 Example Workflows

### Complete Project Development

```bash
python main_interface.py develop \
  --name="ai_chatbot" \
  --language="python" \
  --template="web_app" \
  --description="AI-powered chatbot" \
  --github \
  --tests \
  --build
```

### AI-Powered Planning Session

```bash
python main_interface.py plan \
  --domain="fintech" \
  --iterations=3 \
  --requirements=requirements.json
```

### Code Analysis and Improvement

```bash
python main_interface.py analyze \
  --path="./existing_project" \
  --language="python"
```

### Interactive Development

```bash
python main_interface.py interactive
ideation> plan domain=web_development
ideation> develop name=myapp language=python
ideation> github operation=create_repo name=myapp
ideation> execute code="print('Project created!')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepSeek AI** for advanced reasoning capabilities
- **Model Context Protocol (MCP)** for enhanced integration
- **GitHub API** for repository automation
- The open-source community for inspiration and tools

---

**🧠⚡ Unleash the power of AI-driven development!**