# MCP (Model Context Protocol) Setup Guide

## Overview
This project is configured to use 22 MCP servers via Docker, plus a parent MCP agent, providing comprehensive AI-powered development capabilities.

## Available MCP Servers

### Core Services
- **mcp-agent**: Parent MCP agent (local Python)
- **github**: GitHub operations and issue management
- **filesystem**: File system operations
- **git**: Version control operations
- **memory**: Persistent context storage
- **python**: Python code execution

### Browser & Web
- **playwright**: Browser automation
- **mcp-playwright**: Enhanced Playwright integration
- **fetch**: HTTP requests and web fetching

### Knowledge & Search
- **wikipedia**: Wikipedia search and retrieval
- **youtube-transcript**: YouTube video transcripts
- **paper-search**: Academic paper search
- **needle**: Document search and analysis

### Development Tools
- **dockerhub**: Docker Hub integration
- **npm-sentinel**: NPM package monitoring
- **node-code-sandbox**: Node.js code execution
- **jetbrains**: JetBrains IDE integration

### API & Schema
- **api-gateway**: API gateway management
- **openapi-schema**: OpenAPI schema tools

### AI Enhancement
- **ref-tools**: Reference and citation tools
- **sequential-thinking**: Sequential reasoning
- **time**: Time and scheduling utilities

## Setup Instructions

### 1. Environment Configuration
```bash
# Copy and edit the environment file
cp .env.mcp .env
# Edit .env with your GitHub token and other credentials
```

### 2. Start All MCP Servers
```bash
# Windows
.\scripts/start_mcp.bat

# Linux/Mac
docker-compose -f docker_compose_mcp.yml up -d
```

### 3. Verify Installation
```bash
# Check running containers
docker ps | grep mcp

# View logs for a specific service
docker-compose -f docker_compose_mcp.yml logs -f github-mcp
```

## Using MCP Servers in Claude Desktop

Add this configuration to your Claude Desktop config file:
`%APPDATA%\Claude\config.json` (Windows)
`~/.config/claude/config.json` (Linux/Mac)

```json
{
  "mcpServers": {
    "avs-orchestrator": {
      "command": "python",
      "args": ["C:/Users/alexi/mcp-agent/avs_ai_orchestrator/mcp_launcher.py"],
      "env": {
        "MCP_CONFIG": "C:/Users/alexi/mcp-agent/avs_ai_orchestrator/mcp.json"
      }
    }
  }
}
```

## Project Integration

The MCP servers are integrated with your AI Orchestrator project to provide:

1. **Automated Development**: GitHub issue to code pipeline
2. **TDD Workflow**: Test-driven development with automatic test generation
3. **Multi-Agent Orchestration**: Specialized agents for different tasks
4. **Knowledge Integration**: Access to documentation, papers, and web resources
5. **Browser Automation**: Web testing and scraping capabilities

## Managing MCP Servers

### Start Services
```bash
docker-compose -f docker_compose_mcp.yml up -d
```

### Stop Services
```bash
docker-compose -f docker_compose_mcp.yml down
```

### Update Images
```bash
docker-compose -f docker_compose_mcp.yml pull
docker-compose -f docker_compose_mcp.yml up -d
```

### View Logs
```bash
# All services
docker-compose -f docker_compose_mcp.yml logs -f

# Specific service
docker-compose -f docker_compose_mcp.yml logs -f github-mcp
```

## Troubleshooting

### Docker Not Running
Ensure Docker Desktop is running before starting MCP servers.

### Port Conflicts
Check `docker_compose_mcp.yml` and adjust ports if needed.

### Permission Issues
Run Docker commands with administrator privileges on Windows.

### Container Fails to Start
Check logs: `docker logs mcp-[service-name]`

## Development Workflow

1. **Issue Creation**: Use GitHub MCP to create/fetch issues
2. **TDD Development**: Orchestrator generates tests first
3. **Code Generation**: AI agents write implementation
4. **Version Control**: Git MCP handles commits
5. **Documentation**: Automatic documentation generation
6. **Deployment**: Containerized deployment ready

## Security Notes

- Never commit `.env` files with real tokens
- Use Docker secrets for production
- Regularly update MCP server images
- Monitor container resource usage

## Support

For issues with:
- MCP Servers: Check individual server documentation
- Docker: Refer to Docker documentation
- This setup: Create an issue in the GitHub repository