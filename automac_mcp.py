#!/usr/bin/env python3

import subprocess
import json
import time
from typing import Any, Dict, List, Optional
import pyautogui
import easyocr
import numpy as np
from mcp.server.fastmcp import FastMCP
try:
    from Cocoa import NSWorkspace
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID, CGEventCreateScrollWheelEvent, CGEventPost, kCGScrollEventUnitPixel, kCGHIDEventTap
    from ApplicationServices import AXUIElementCreateApplication, AXUIElementCopyAttributeValue, kAXWindowsAttribute, kAXTitleAttribute, kAXPositionAttribute, kAXSizeAttribute, kAXRoleAttribute
    ACCESSIBILITY_AVAILABLE = True
except ImportError:
    ACCESSIBILITY_AVAILABLE = False

# Initialize the MCP server
mcp = FastMCP("AutoMac MCP - macOS UI Automation")

# Initialize OCR reader and pyautogui settings
reader = easyocr.Reader(['en'])
pyautogui.FAILSAFE = True


def _scale_coordinates_for_display(x: int, y: int) -> tuple[int, int]:
    """Scale coordinates for retina/high-DPI displays."""
    try:
        # Get the actual screen size from pyautogui
        screen_width, screen_height = pyautogui.size()
        
        # Take a screenshot to get the logical size
        screenshot = pyautogui.screenshot()
        logical_width, logical_height = screenshot.size
        
        # Calculate scaling factors
        scale_x = screen_width / logical_width
        scale_y = screen_height / logical_height
        
        # Scale the coordinates
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        
        return scaled_x, scaled_y
    except Exception:
        # If scaling fails, return original coordinates
        return x, y

@mcp.tool()
def get_screen_size() -> Dict[str, Any]:
    screen_width, screen_height = pyautogui.size()
    return {"success": True, "message": f"Screen size = ({screen_width}, {screen_height})"}


@mcp.tool()
def mouse_move(x: int, y: int) -> Dict[str, Any]:
    """Single click at the specified screen coordinates."""
    if x is None or y is None:
        raise ValueError("x and y coordinates are required")
    
    # Scale coordinates for retina displays
    scaled_x, scaled_y = _scale_coordinates_for_display(x, y)
    pyautogui.moveTo(x=scaled_x, y=scaled_y, clicks=1)
    return {"success": True, "message": f"Moved mouse pointer to ({x}, {y})"}


@mcp.tool()
def mouse_single_click(x: int, y: int) -> Dict[str, Any]:
    """Single click at the specified screen coordinates."""
    if x is None or y is None:
        raise ValueError("x and y coordinates are required")
    
    # Scale coordinates for retina displays
    scaled_x, scaled_y = _scale_coordinates_for_display(x, y)
    pyautogui.click(x=scaled_x, y=scaled_y, clicks=1)
    return {"success": True, "message": f"Single clicked at ({x}, {y})"}


@mcp.tool()
def mouse_double_click(x: int, y: int) -> Dict[str, Any]:
    """Double click at the specified screen coordinates."""
    if x is None or y is None:
        raise ValueError("x and y coordinates are required")
    
    # Scale coordinates for retina displays
    scaled_x, scaled_y = _scale_coordinates_for_display(x, y)
    pyautogui.click(x=scaled_x, y=scaled_y, clicks=2)
    return {"success": True, "message": f"Double clicked at ({x}, {y})"}


@mcp.tool()
def type_text(text: str) -> Dict[str, Any]:
    """Type the specified text."""
    if not text:
        raise ValueError("text is required")
    
    pyautogui.write(text)
    return {"success": True, "message": f"Typed: {text}"}


@mcp.tool()
def scroll(dx: int = 0, dy: int = 0) -> Dict[str, Any]:
    
    """Scroll with the specified pixel delta values.
    Args:
        dx: Horizontal scroll pixel delta (positive = right, negative = left)
        dy: Vertical scroll pixel delta (positive = down, negative = up)
    """
    # pyautogui.scroll: positive = up, negative = down
    # We want intuitive behavior: positive dy = scroll down, negative dy = scroll up
    if dy != 0:
        CGEventPost(kCGHIDEventTap, CGEventCreateScrollWheelEvent(None, kCGScrollEventUnitPixel, 1, -dy))
    if dx != 0:
        # pyautogui.hscroll: positive = right, negative = left (already correct)
        pyautogui.hscroll(clicks=dx)
    return {"success": True, "message": f"Scrolled dx={dx}, dy={dy}"}


@mcp.tool()
def play_sound_for_user_prompt() -> Dict[str, Any]:
    """Play the system bell sound to alert the user."""
    result = subprocess.run(
        ["osascript", "-e", "beep"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return {
            "success": False, 
            "message": f"Failed to play system bell: {result.stderr.strip()}"
        }
    
    return {"success": True, "message": "System bell played"}


def _execute_applescript_keystroke(keystroke_command: str, description: str) -> Dict[str, Any]:
    """Helper function to execute AppleScript keystrokes."""
    script = f'''
    tell application "System Events"
        {keystroke_command}
    end tell
    '''
    
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr}")
    
    return {"success": True, "message": f"Executed: {description}"}


@mcp.tool()
def keyboard_shortcut_return_key() -> Dict[str, Any]:
    """Press the Return/Enter key."""
    return _execute_applescript_keystroke('keystroke return', "Return key")


@mcp.tool()
def keyboard_shortcut_escape_key() -> Dict[str, Any]:
    """Press the Escape key."""
    return _execute_applescript_keystroke('key code 53', "Escape key")


@mcp.tool()
def keyboard_shortcut_tab_key() -> Dict[str, Any]:
    """Press the Tab key."""
    return _execute_applescript_keystroke('keystroke tab', "Tab key")


@mcp.tool()
def keyboard_shortcut_space_key() -> Dict[str, Any]:
    """Press the Space key."""
    return _execute_applescript_keystroke('keystroke " "', "Space key")


@mcp.tool()
def keyboard_shortcut_delete_key() -> Dict[str, Any]:
    """Press the Delete key (backspace)."""
    return _execute_applescript_keystroke('key code 51', "Delete key")


@mcp.tool()
def keyboard_shortcut_forward_delete_key() -> Dict[str, Any]:
    """Press the Forward Delete key."""
    return _execute_applescript_keystroke('key code 117', "Forward Delete key")


@mcp.tool()
def keyboard_shortcut_arrow_up() -> Dict[str, Any]:
    """Press the Up Arrow key."""
    return _execute_applescript_keystroke('key code 126', "Up Arrow key")


@mcp.tool()
def keyboard_shortcut_arrow_down() -> Dict[str, Any]:
    """Press the Down Arrow key."""
    return _execute_applescript_keystroke('key code 125', "Down Arrow key")


@mcp.tool()
def keyboard_shortcut_arrow_left() -> Dict[str, Any]:
    """Press the Left Arrow key."""
    return _execute_applescript_keystroke('key code 123', "Left Arrow key")


@mcp.tool()
def keyboard_shortcut_arrow_right() -> Dict[str, Any]:
    """Press the Right Arrow key."""
    return _execute_applescript_keystroke('key code 124', "Right Arrow key")


@mcp.tool()
def keyboard_shortcut_select_all() -> Dict[str, Any]:
    """Select all text (Cmd+A)."""
    return _execute_applescript_keystroke('keystroke "a" using {command down}', "Select All (Cmd+A)")


@mcp.tool()
def keyboard_shortcut_copy() -> Dict[str, Any]:
    """Copy selected content (Cmd+C)."""
    return _execute_applescript_keystroke('keystroke "c" using {command down}', "Copy (Cmd+C)")


@mcp.tool()
def keyboard_shortcut_paste() -> Dict[str, Any]:
    """Paste from clipboard (Cmd+V)."""
    return _execute_applescript_keystroke('keystroke "v" using {command down}', "Paste (Cmd+V)")


@mcp.tool()
def keyboard_shortcut_cut() -> Dict[str, Any]:
    """Cut selected content (Cmd+X)."""
    return _execute_applescript_keystroke('keystroke "x" using {command down}', "Cut (Cmd+X)")


@mcp.tool()
def keyboard_shortcut_undo() -> Dict[str, Any]:
    """Undo last action (Cmd+Z)."""
    return _execute_applescript_keystroke('keystroke "z" using {command down}', "Undo (Cmd+Z)")


@mcp.tool()
def keyboard_shortcut_redo() -> Dict[str, Any]:
    """Redo last undone action (Cmd+Shift+Z)."""
    return _execute_applescript_keystroke('keystroke "z" using {command down, shift down}', "Redo (Cmd+Shift+Z)")


@mcp.tool()
def keyboard_shortcut_save() -> Dict[str, Any]:
    """Save current document (Cmd+S)."""
    return _execute_applescript_keystroke('keystroke "s" using {command down}', "Save (Cmd+S)")


@mcp.tool()
def keyboard_shortcut_new() -> Dict[str, Any]:
    """Create new document (Cmd+N)."""
    return _execute_applescript_keystroke('keystroke "n" using {command down}', "New (Cmd+N)")


@mcp.tool()
def keyboard_shortcut_open() -> Dict[str, Any]:
    """Open document (Cmd+O)."""
    return _execute_applescript_keystroke('keystroke "o" using {command down}', "Open (Cmd+O)")


@mcp.tool()
def keyboard_shortcut_find() -> Dict[str, Any]:
    """Find in document (Cmd+F)."""
    return _execute_applescript_keystroke('keystroke "f" using {command down}', "Find (Cmd+F)")


@mcp.tool()
def keyboard_shortcut_close_window() -> Dict[str, Any]:
    """Close current window (Cmd+W)."""
    return _execute_applescript_keystroke('keystroke "w" using {command down}', "Close Window (Cmd+W)")


@mcp.tool()
def keyboard_shortcut_quit_app() -> Dict[str, Any]:
    """Quit current application (Cmd+Q)."""
    return _execute_applescript_keystroke('keystroke "q" using {command down}', "Quit App (Cmd+Q)")


@mcp.tool()
def keyboard_shortcut_minimize_window() -> Dict[str, Any]:
    """Minimize current window (Cmd+M)."""
    return _execute_applescript_keystroke('keystroke "m" using {command down}', "Minimize Window (Cmd+M)")


@mcp.tool()
def keyboard_shortcut_hide_app() -> Dict[str, Any]:
    """Hide current application (Cmd+H)."""
    return _execute_applescript_keystroke('keystroke "h" using {command down}', "Hide App (Cmd+H)")


@mcp.tool()
def keyboard_shortcut_switch_app_forward() -> Dict[str, Any]:
    """Switch to next application (Cmd+Tab)."""
    return _execute_applescript_keystroke('keystroke tab using {command down}', "Switch App Forward (Cmd+Tab)")


@mcp.tool()
def keyboard_shortcut_switch_app_backward() -> Dict[str, Any]:
    """Switch to previous application (Cmd+Shift+Tab)."""
    return _execute_applescript_keystroke('keystroke tab using {command down, shift down}', "Switch App Backward (Cmd+Shift+Tab)")


@mcp.tool()
def keyboard_shortcut_spotlight_search() -> Dict[str, Any]:
    """Open Spotlight search (Cmd+Space)."""
    return _execute_applescript_keystroke('keystroke " " using {command down}', "Spotlight Search (Cmd+Space)")


@mcp.tool()
def keyboard_shortcut_force_quit() -> Dict[str, Any]:
    """Open Force Quit dialog (Cmd+Option+Esc)."""
    return _execute_applescript_keystroke('key code 53 using {command down, option down}', "Force Quit (Cmd+Option+Esc)")


@mcp.tool()
def keyboard_shortcut_refresh() -> Dict[str, Any]:
    """Refresh/Reload (Cmd+R)."""
    return _execute_applescript_keystroke('keystroke "r" using {command down}', "Refresh (Cmd+R)")


@mcp.tool()
def focus_app(app_name: str, timeout: int = 30) -> Dict[str, Any]:
    """Bring the specified application to the foreground and wait for it to become active.
    
    Args:
        app_name: Name of the application to focus
        timeout: Maximum time to wait for app to become active (default: 30 seconds)
    """
    if not app_name:
        raise ValueError("app_name is required")
    
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    
    # First, try to activate the app
    script = f'tell application "{app_name}" to activate'
    
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return {
            "success": False, 
            "message": f"Failed to activate app '{app_name}': {result.stderr.strip()}"
        }
    
    # Wait for the app to become the active application
    start_time = time.time()
    last_active_app = None
    
    while time.time() - start_time < timeout:
        try:
            if ACCESSIBILITY_AVAILABLE:
                # Use Cocoa NSWorkspace to check active app
                workspace = NSWorkspace.sharedWorkspace()
                active_app = workspace.activeApplication()
                if active_app:
                    active_app_name = active_app.get("NSApplicationName", "")
                    if active_app_name.lower() == app_name.lower():
                        elapsed_time = round(time.time() - start_time, 2)
                        return {
                            "success": True, 
                            "message": f"Successfully focused '{app_name}' (took {elapsed_time}s)",
                            "elapsed_time": elapsed_time,
                            "active_app": {
                                "name": active_app_name,
                                "bundle_id": active_app.get("NSApplicationBundleIdentifier", "Unknown"),
                                "pid": active_app.get("NSApplicationProcessIdentifier", -1)
                            }
                        }
                    last_active_app = active_app_name
            else:
                # Fallback: use AppleScript to check frontmost app
                check_script = 'tell application "System Events" to get name of first application process whose frontmost is true'
                check_result = subprocess.run(
                    ["osascript", "-e", check_script],
                    capture_output=True,
                    text=True
                )
                
                if check_result.returncode == 0:
                    frontmost_app = check_result.stdout.strip()
                    if frontmost_app.lower() == app_name.lower():
                        elapsed_time = round(time.time() - start_time, 2)
                        return {
                            "success": True, 
                            "message": f"Successfully focused '{app_name}' (took {elapsed_time}s)",
                            "elapsed_time": elapsed_time,
                            "active_app": {"name": frontmost_app}
                        }
                    last_active_app = frontmost_app
        
        except Exception as e:
            # Continue waiting even if we can't check the active app
            pass
        
        # Wait a bit before checking again
        time.sleep(0.5)
    
    # Timeout reached
    return {
        "success": False,
        "message": f"Timeout waiting for '{app_name}' to become active after {timeout}s",
        "timeout": timeout,
        "last_active_app": last_active_app,
        "elapsed_time": timeout
    }


@mcp.tool()
def get_screen_layout() -> str:
    """Get information about windows and applications currently visible on the screen."""
    return _get_screen_content_accessibility()


@mcp.tool()
def get_screen_text() -> str:
    """Get all text currently visible on the screen using OCR."""
    return _get_screen_content_ocr()


def _get_screen_content_accessibility() -> str:
    """Get screen content using macOS accessibility APIs."""
    if not ACCESSIBILITY_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "macOS accessibility frameworks not available",
            "message": "Install pyobjc-framework-Cocoa and pyobjc-framework-Quartz"
        }, indent=2)
    
    try:
        screen_info = {
            "mode": "accessibility",
            "timestamp": str(subprocess.run(["date"], capture_output=True, text=True).stdout.strip()),
            "windows": [],
            "active_app": None
        }
        
        # Get active application
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            if active_app:
                screen_info["active_app"] = {
                    "name": active_app.get("NSApplicationName", "Unknown"),
                    "bundle_id": active_app.get("NSApplicationBundleIdentifier", "Unknown"),
                    "pid": active_app.get("NSApplicationProcessIdentifier", -1)
                }
        except Exception as e:
            screen_info["active_app_error"] = str(e)
        
        # Get window information using Quartz
        try:
            window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
            
            for window in window_list:
                # Skip windows without titles or that are too small
                window_name = window.get('kCGWindowName', '')
                window_bounds = window.get('kCGWindowBounds', {})
                
                if (window_name and 
                    window_bounds.get('Width', 0) > 50 and 
                    window_bounds.get('Height', 0) > 50):
                    
                    window_info = {
                        "title": window_name,
                        "app": window.get('kCGWindowOwnerName', 'Unknown'),
                        "bounds": {
                            "x": int(window_bounds.get('X', 0)),
                            "y": int(window_bounds.get('Y', 0)),
                            "width": int(window_bounds.get('Width', 0)),
                            "height": int(window_bounds.get('Height', 0))
                        },
                        "layer": window.get('kCGWindowLayer', 0),
                        "pid": window.get('kCGWindowOwnerPID', -1)
                    }
                    screen_info["windows"].append(window_info)
        
        except Exception as e:
            screen_info["windows_error"] = str(e)
        
        # Sort windows by layer (front to back)
        screen_info["windows"].sort(key=lambda w: w.get("layer", 0))
        
        # Get screen size
        try:
            screenshot = pyautogui.screenshot()
            screen_info["screen_size"] = {
                "width": screenshot.width,
                "height": screenshot.height
            }
        except Exception as e:
            screen_info["screen_size_error"] = str(e)
        
        return json.dumps({
            "success": True,
            "screen_info": screen_info,
            "message": f"Found {len(screen_info['windows'])} visible windows"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to get screen content using accessibility"
        }, indent=2)


def _get_screen_content_ocr() -> str:
    """Get screen content using OCR to read all text on screen."""
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert PIL Image to numpy array for easyocr
        screenshot_array = np.array(screenshot)
        
        # Use OCR to extract all text
        results = reader.readtext(screenshot_array)
        
        screen_info = {
            "mode": "ocr",
            "timestamp": str(subprocess.run(["date"], capture_output=True, text=True).stdout.strip()),
            "screen_size": {
                "width": screenshot.width,
                "height": screenshot.height
            },
            "text_elements": [],
            "full_text": ""
        }
        
        all_text_lines = []
        
        for (bbox, detected_text, confidence) in results:
            if confidence > 0.3:  # Lower threshold for general screen reading
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                
                text_element = {
                    "text": detected_text.strip(),
                    "confidence": round(confidence, 3),
                    "position": {
                        "center_x": center_x,
                        "center_y": center_y,
                        "bbox": [[int(point[0]), int(point[1])] for point in bbox]
                    }
                }
                
                screen_info["text_elements"].append(text_element)
                all_text_lines.append(detected_text.strip())
        
        # Sort text elements by vertical position (top to bottom, then left to right)
        screen_info["text_elements"].sort(key=lambda x: (x["position"]["center_y"], x["position"]["center_x"]))
        
        # Create full text representation
        screen_info["full_text"] = "\n".join([elem["text"] for elem in screen_info["text_elements"]])
        
        return json.dumps({
            "success": True,
            "screen_info": screen_info,
            "message": f"Found {len(screen_info['text_elements'])} text elements on screen"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to get screen content using OCR"
        }, indent=2)



@mcp.tool()
def get_available_apps() -> str:
    """Get a list of all running applications."""
    script = '''
    tell application "System Events"
        get name of (processes where background only is false)
    end tell
    '''
    
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get apps: {result.stderr}")
    
    apps = [app.strip() for app in result.stdout.split(", ")]
    return json.dumps({"success": True, "apps": apps}, indent=2)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()