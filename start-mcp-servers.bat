@echo off
echo ========================================
echo Starting MCP Docker Servers
echo ========================================

REM Load environment variables
if exist .env.mcp (
    echo Loading MCP environment variables...
    for /f "delims=" %%x in (.env.mcp) do (
        echo %%x | findstr /r "^[^#]" >nul && set "%%x"
    )
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Start MCP Docker services
echo Starting MCP Docker services...
docker-compose -f docker-compose.mcp.yml up -d

REM Check status
echo.
echo Checking MCP server status...
docker-compose -f docker-compose.mcp.yml ps

echo.
echo ========================================
echo MCP Servers Started Successfully!
echo ========================================
echo.
echo Available MCP Servers:
echo - GitHub MCP Server
echo - Filesystem MCP Server
echo - Git MCP Server
echo - Memory MCP Server
echo - Playwright MCP Server
echo - Wikipedia MCP Server
echo - YouTube Transcript MCP Server
echo - And 15+ more...
echo.
echo To stop servers: docker-compose -f docker-compose.mcp.yml down
echo To view logs: docker-compose -f docker-compose.mcp.yml logs -f [service-name]
echo.
pause