#!/usr/bin/env python3
"""
QACDCO Performance Reporter MCP Server
Manages performance reports via Django API from qacdco-reporter-performance system
"""

import asyncio
import logging
import os
from typing import Optional, List, Dict

import aiohttp
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qacdco-performance-reporter-mcp")

# Configuration
DJANGO_API_BASE = os.getenv("DJANGO_API_BASE", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Simple notification options object
class NotificationOptions:
    def __init__(self):
        self.tools_changed = None

server = Server("qacdco-performance-reporter-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools for report management."""
    return [
        Tool(
            name="get_report_link",
            description="Get download link for a performance report (lightweight, no file download)",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "integer",
                        "description": "Report ID to get download link for"
                    }
                },
                "required": ["report_id"]
            }
        ),
        Tool(
            name="list_reports",
            description="List available performance reports with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "execution_id": {
                        "type": "integer",
                        "description": "Filter by execution ID (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of reports to return (default: 20)",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="get_report_status",
            description="Check report status and metadata by report ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "integer",
                        "description": "Report ID to check"
                    }
                },
                "required": ["report_id"]
            }
        ),
        Tool(
            name="generate_report",
            description="Generate a new performance report for an execution (future functionality)",
            inputSchema={
                "type": "object",
                "properties": {
                    "execution_id": {
                        "type": "integer",
                        "description": "Execution ID to generate report for"
                    },
                    "threshold": {
                        "type": "integer",
                        "description": "Performance threshold (optional)",
                        "default": 95
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report to generate",
                        "default": "performance"
                    }
                },
                "required": ["execution_id"]
            }
        )
    ]

async def get_report_by_id(report_id: int) -> Optional[Dict]:
    """Get report metadata from Django API."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
            url = f"{DJANGO_API_BASE}/performance/reporter/api/1.0/reports/?id={report_id}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        return data[0]  # API returns list, get first item
                else:
                    logger.warning(f"API request failed with status {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error fetching report {report_id}: {e}")
        return None

async def list_reports_api(execution_id: Optional[int] = None, limit: int = 20) -> List[Dict]:
    """Get list of reports from Django API."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
            url = f"{DJANGO_API_BASE}/performance/reporter/api/1.0/reports/"
            params = {}
            if execution_id:
                params["execution_id"] = execution_id

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[:limit] if data else []
                else:
                    logger.warning(f"API request failed with status {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error fetching reports list: {e}")
        return []


async def generate_report_api(execution_id: int, threshold: int = 95, report_type: str = "performance") -> Optional[Dict]:
    """Generate new report via Django API."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
            url = f"{DJANGO_API_BASE}/performance/reporter/api/1.0/reports/"
            data = {
                "execution": execution_id,
                "threshold": threshold,
                "report_type": report_type
            }

            async with session.post(url, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    logger.warning(f"Report generation failed with status {response.status}")
                    error_text = await response.text()
                    logger.warning(f"Error details: {error_text}")
                    return None
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return None

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls for report management."""

    if name == "get_report_link":
        report_id = arguments.get("report_id")

        # Get report metadata
        report_data = await get_report_by_id(report_id)
        if not report_data:
            return [TextContent(
                type="text",
                text=f"❌ Report not found: ID {report_id}"
            )]

        # Check if file is generated
        generated_file = report_data.get("generated_file")
        if not generated_file:
            return [TextContent(
                type="text",
                text=f"❌ Report {report_id} exists but file not generated yet. Status: {report_data.get('ended_at', 'Processing...')}"
            )]

        # Construct download URL
        if generated_file.startswith('/'):
            download_url = f"{DJANGO_API_BASE}{generated_file}"
        elif generated_file.startswith('http'):
            download_url = generated_file
        else:
            download_url = f"{DJANGO_API_BASE}/performance/reporter/media/{generated_file}"

        filename = generated_file.split('/')[-1] if '/' in generated_file else generated_file

        return [TextContent(
            type="text",
            text=f"""📊 **Performance Report Link**

**Report ID:** {report_id}
**Execution:** {report_data.get('execution', 'Unknown')}
**Created:** {report_data.get('created_at', 'Unknown')}
**Type:** {report_data.get('report_type', 'performance')}
**Threshold:** {report_data.get('threshold', 'N/A')}

**📁 Download Link:**
```
{download_url}
```

**File:** {filename}
**Status:** ✅ Ready for download

💡 **Uso:** Copia el enlace para descargar el archivo DOCX directamente"""
        )]

    elif name == "list_reports":
        execution_id = arguments.get("execution_id")
        limit = arguments.get("limit", 20)

        reports = await list_reports_api(execution_id, limit)

        if not reports:
            filter_msg = f" for execution {execution_id}" if execution_id else ""
            return [TextContent(
                type="text",
                text=f"📂 No reports found{filter_msg}"
            )]

        result = "📋 **Available Performance Reports**\n\n"

        for i, report in enumerate(reports, 1):
            status = "✅ Ready" if report.get("generated_file") else "⏳ Processing"
            result += f"{i}. **Report #{report.get('id')}**\n"
            result += f"   🔧 Execution: {report.get('execution')}\n"
            result += f"   📅 Created: {report.get('created_at', 'Unknown')}\n"
            result += f"   📊 Type: {report.get('report_type', 'performance')}\n"
            result += f"   🎯 Threshold: {report.get('threshold', 'N/A')}\n"
            result += f"   📄 Status: {status}\n"
            if report.get("generated_file"):
                result += f"   📁 File: {report.get('generated_file').split('/')[-1]}\n"
            result += "\n"

        result += f"**Total:** {len(reports)} reports (limit: {limit})"

        return [TextContent(type="text", text=result)]

    elif name == "get_report_status":
        report_id = arguments.get("report_id")

        report_data = await get_report_by_id(report_id)
        if not report_data:
            return [TextContent(
                type="text",
                text=f"❌ Report not found: ID {report_id}"
            )]

        status = "✅ Generated" if report_data.get("generated_file") else "⏳ Processing"
        ended_at = report_data.get("ended_at", 0)

        if ended_at == -1:
            status = "❌ Failed"
        elif ended_at == 0:
            status = "⏳ In Progress"

        return [TextContent(
            type="text",
            text=f"""📊 **Report Status**

**ID:** {report_id}
**Status:** {status}
**Type:** {report_data.get('report_type', 'performance')}
**Execution:** {report_data.get('execution')}
**Created:** {report_data.get('created_at', 'Unknown')}
**Threshold:** {report_data.get('threshold', 'N/A')}
**File:** {report_data.get('generated_file', 'Not generated')}
"""
        )]

    elif name == "generate_report":
        execution_id = arguments.get("execution_id")
        threshold = arguments.get("threshold", 95)
        report_type = arguments.get("report_type", "performance")

        result = await generate_report_api(execution_id, threshold, report_type)
        if not result:
            return [TextContent(
                type="text",
                text=f"❌ Failed to generate report for execution {execution_id}. Check Django API logs."
            )]

        return [TextContent(
            type="text",
            text=f"""✅ **Report Generation Started**

**Report ID:** {result.get('id')}
**Execution:** {execution_id}
**Threshold:** {threshold}%
**Type:** {report_type}

The report is being generated asynchronously. Use `get_report_status` with ID {result.get('id')} to check progress.
Once complete, use `get_report_link` to get the download link for the DOCX file."""
        )]

    return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

async def main():
    """Main function to run the MCP server."""
    logger.info("Starting QACDCO Performance Reporter MCP Server")
    logger.info(f"Django API base: {DJANGO_API_BASE}")
    logger.info(f"API timeout: {API_TIMEOUT}s")

    # Test API connectivity
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get(f"{DJANGO_API_BASE}/performance/reporter/api/1.0/reports/") as response:
                if response.status == 200:
                    logger.info("✅ Django API connectivity verified")
                else:
                    logger.warning(f"⚠️ Django API returned status {response.status}")
    except Exception as e:
        logger.warning(f"⚠️ Could not verify Django API connectivity: {e}")
        logger.warning("Server will start but API calls may fail")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="qacdco-performance-reporter-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())