# 🚀 Enhanced DeepSeek CLI with MCP Integration

A powerful command-line interface for DeepSeek AI with integrated Model Context Protocol (MCP) servers, designed specifically for software engineering workflows.

## ✨ Features

### 🤖 AI Capabilities
- **Interactive Chat Sessions** - Continuous conversations with context retention
- **Quick Questions** - Single-shot Q&A with smart responses
- **File Analysis** - Code review, summarization, and optimization suggestions
- **Context-Aware Responses** - Leverages MCP tools for enhanced answers

### 🔌 MCP Integration
- **10+ Pre-configured Servers** - Ready-to-use integrations for software engineering
- **Tool Discovery** - Automatic detection and listing of available tools
- **Smart Tool Suggestions** - AI recommends relevant tools based on context
- **Session-Persistent Connections** - Maintains tool state across conversations

### 📊 Software Engineering Focus
- **Version Control** - Git and GitHub operations
- **Cloud Services** - AWS, Docker, and infrastructure management
- **Development Tools** - File system operations, database queries
- **Communication** - Slack integration for team workflows
- **AI/ML** - Hugging Face models and datasets access

## 🛠️ Pre-configured MCP Servers

| Server | Category | Description | Key Tools |
|--------|----------|-------------|-----------|
| **GitHub** | Version Control | Repository management and code analysis | `create_repository`, `list_repositories`, `get_file_contents`, `search_repositories`, `create_issue` |
| **Hugging Face** | AI/ML | Access to models, datasets, and spaces | `search_models`, `get_model_info`, `search_datasets`, `get_dataset_info` |
| **Docker** | Infrastructure | Container and image management | `list_containers`, `list_images`, `container_logs`, `create_container` |
| **AWS** | Cloud | Amazon Web Services management | `list_ec2_instances`, `list_s3_buckets`, `list_lambda_functions` |
| **Slack** | Communication | Workspace integration | `list_channels`, `send_message`, `get_user_profile`, `list_users` |
| **File System** | System | Local file operations | `read_file`, `write_file`, `list_directory`, `create_directory` |
| **Git** | Version Control | Version control operations | `git_status`, `git_log`, `git_diff`, `git_add`, `git_commit` |
| **PostgreSQL** | Database | Database operations | `list_tables`, `describe_table`, `query`, `read_query` |
| **Brave Search** | Search | Web search capabilities | `brave_web_search` |
| **Google Drive** | Cloud Storage | File management | `list_files`, `get_file`, `create_file`, `update_file` |

## 🚀 Quick Start

### Installation

```bash
# Run the installation script
./install-enhanced-cli.sh
```

### Setup

1. **Configure DeepSeek API**:
```bash
deepseek-enhanced setup
```

2. **Set up MCP Servers**:
```bash
deepseek-enhanced mcp setup
```

3. **Start using**:
```bash
deepseek-enhanced chat
```

## 📚 Usage Examples

### Basic Commands

```bash
# Interactive chat session
deepseek-enhanced chat

# Quick question
deepseek-enhanced ask "How do I optimize this React component?"

# Analyze a file
deepseek-enhanced file ./src/components/App.js

# List available MCP tools
deepseek-enhanced mcp tools

# Use a specific tool
deepseek-enhanced mcp use git_status
```

### Advanced Workflows

#### 1. Code Review Workflow
```bash
# Analyze code file with AI
deepseek-enhanced file ./api/server.js --action review

# Check git status using MCP
deepseek-enhanced mcp use git_status

# Create GitHub issue for found problems
deepseek-enhanced mcp use create_issue '{"title":"Code review findings","body":"..."}'
```

## ⚙️ Configuration

### MCP Server Configuration
MCP servers are configured in `~/.deepseek-mcp-config.json`:

```json
{
  "servers": {
    "github": {
      "enabled": true,
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    },
    "slack": {
      "enabled": true,
      "env": {
        "SLACK_BOT_TOKEN": "your-bot-token",
        "SLACK_APP_TOKEN": "your-app-token"
      }
    }
  }
}
```

## 🔐 Security & Authentication

### Required Credentials

Different MCP servers require different authentication:

- **GitHub**: Personal Access Token
- **Slack**: Bot Token and App Token
- **AWS**: Access Key ID and Secret Access Key
- **Hugging Face**: API Token
- **Google Drive**: OAuth2 Client ID and Secret

## 📄 License

This project is licensed under the MIT License.

---

**Made with ❤️ for the developer community**