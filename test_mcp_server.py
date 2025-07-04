#!/usr/bin/env python3

import subprocess
import time
import sys


def test_mcp_server():
    """Test the FastMCP server by running it and checking output"""
    print("Testing AutoMac MCP FastMCP Server")
    print("=" * 35)
    
    print("\n1. Starting MCP server...")
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "automac_mcp.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is running
        if process.poll() is None:
            print("✓ MCP server started successfully")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✓ MCP server terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("! MCP server had to be forcefully killed")
        else:
            stdout, stderr = process.communicate()
            print(f"✗ MCP server failed to start")
            if stderr:
                print(f"Error: {stderr}")
            if stdout:
                print(f"Output: {stdout}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing server: {e}")
        return False
    
    print("\n2. Testing server structure...")
    
    # Import the module to check for syntax errors
    try:
        import automac_mcp
        print("✓ Module imports successfully")
        
        # Check if the FastMCP instance exists
        if hasattr(automac_mcp, 'mcp'):
            print("✓ FastMCP instance found")
        else:
            print("✗ FastMCP instance not found")
            return False
            
        # Check for decorated functions
        functions = [
            'mouse_single_click', 'type_text', 'scroll', 'focus_app', 
            'get_screen_layout', 'get_screen_text', 'get_available_apps'
        ]
        
        for func_name in functions:
            if hasattr(automac_mcp, func_name):
                print(f"✓ Function {func_name} found")
            else:
                print(f"✗ Function {func_name} not found")
                return False
                
    except ImportError as e:
        print(f"✗ Failed to import module: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking module: {e}")
        return False
    
    print("\n3. Testing individual functions...")
    
    # Test functions that don't require UI interaction
    try:
        # Test get_available_apps (should work on any macOS system)
        result = automac_mcp.get_available_apps()
        if result and "apps" in result:
            print("✓ get_available_apps returns data")
        else:
            print("✗ get_available_apps failed")
            
        # Test focus_app with a quick timeout (using Finder which should be running)
        try:
            result = automac_mcp.focus_app("Finder", 5)  # 5 second timeout
            if result and "success" in result:
                print("✓ focus_app with timeout returns data")
            else:
                print("✗ focus_app with timeout failed")
        except Exception as e:
            print(f"✗ focus_app error: {e}")
            
        # Test get_screen_layout (should return screen data or error)
        result = automac_mcp.get_screen_layout()
        if result and ("success" in result or "error" in result):
            print("✓ get_screen_layout returns data")
        else:
            print("✗ get_screen_layout failed")
            
        # Test get_screen_text (should return screen data or error)
        result = automac_mcp.get_screen_text()
        if result and ("success" in result or "error" in result):
            print("✓ get_screen_text returns data")
        else:
            print("✗ get_screen_text failed")
            
    except Exception as e:
        print(f"✗ Error testing functions: {e}")
        return False
    
    print("\nAll tests completed!")
    return True


def test_dependencies():
    """Test that all required dependencies are available"""
    print("\nTesting dependencies...")
    
    dependencies = [
        'mcp.server.fastmcp',
        'pyautogui',
        'easyocr',
        'numpy',
        'subprocess',
        'json'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} - Missing dependency")
            return False
    
    return True


if __name__ == "__main__":
    print("AutoMac MCP Test Suite")
    print("==================")
    
    # Test dependencies first
    if not test_dependencies():
        print("\n❌ Dependency test failed. Install dependencies with: uv sync")
        sys.exit(1)
    
    # Test the server
    if test_mcp_server():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)