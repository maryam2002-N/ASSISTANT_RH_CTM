import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from contextlib import asynccontextmanager

@asynccontextmanager
async def create_email_mcp_client():
    """Crée un client MCP pour l'email"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server_email"],
        env={
            "SMTP_SERVER": os.getenv("SMTP_SERVER", "smtp-mail.outlook.com"),
            "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
            "SMTP_USERNAME": os.getenv("EMAIL_USER", ""),
            "SMTP_PASSWORD": os.getenv("EMAIL_PASSWORD", ""),
            "SMTP_USE_TLS": "true"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        yield read, write