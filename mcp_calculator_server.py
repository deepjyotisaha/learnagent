#!/usr/bin/env python3
"""
Sample MCP Calculator Server implementation in Python.

This module demonstrates how to create a simple MCP server with calculator tools
that can perform basic arithmetic operations (add, subtract, multiply, divide).
"""

# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32api  # Add this import
import win32con
import time
from win32api import GetSystemMetrics
import logging
#from config import Config

# Create a FastMCP server
mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together and return the result."""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a and return the result."""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together and return the result."""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divide a by b and return the result.
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def list_tools() -> list:
    """
    List all available tools with their descriptions and parameters.
    """
    tools = []
    for name, func in mcp.tools.items():
        if name == "list_tools":
            continue  # Don't include itself
        doc = func.__doc__ or ""
        params = list(func.__annotations__.keys())
        if "return" in params:
            params.remove("return")
        tools.append({
            "name": name,
            "description": doc.strip(),
            "parameters": params
        })
    return tools

if __name__ == "__main__":
    print("Starting MCP Calculator server...")
    # Check if running with mcp dev command
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
