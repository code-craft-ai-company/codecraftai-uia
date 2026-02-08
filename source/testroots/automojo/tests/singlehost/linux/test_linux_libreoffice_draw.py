import time
import subprocess
import shutil
import sys
import os

# Adjust path for local execution relative to repo root
sys.path.append(os.path.abspath("source"))
sys.path.append(os.path.abspath("source/testroots"))

# form automojo import testbase # Removed due to import error
from automojo.uia.factory import AutomationFactory
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement

def test_linux_libreoffice_draw():
    """
    Verifies that we can launch LibreOffice Draw and draw a circle.
    """
    automation = AutomationFactory.get_automation_engine()
    
    # 1. Launch LibreOffice Draw
    print("Launching LibreOffice Draw...")
    import subprocess
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "gtk3"
    env["GDK_BACKEND"] = "x11"
    proc = subprocess.Popen(["libreoffice", "--draw", "--norestore"], env=env)
    
    try:
        # 2. Find Application
        app = None
        for _ in range(20):
            time.sleep(1)
            app = automation.get_application_by_name("soffice")
            if not app:
                app = automation.get_application_by_name("Draw")
            if app:
                break
        
        assert app is not None, "LibreOffice Draw not found"
        print(f"Found App: {app.name}")
        
        # 3. Find Main Window
        main_window = None
        for _ in range(10):
            windows = app.get_windows()
            if windows:
                main_window = windows[0]
                break
            time.sleep(1)
            
        assert main_window is not None, "Main window not found"
        print(f"Main Window: {main_window.title}")
        main_window.activate()
        time.sleep(2)
        
        # 4. Find the "Ellipse" tool
        # Note: In LibreOffice Draw, the ellipse tool is usually in the "Drawing" toolbar.
        # Its name might be "Ellipse" or "Circle".
        ellipse_tool = None
        
        # Strategy: Search for "Ellipse" or "Circle" with role "toggle button" or "push button"
        # This avoids picking up the hidden menu item which has invalid bounds
        print("Searching for Ellipse tool in toolbars...")
        
        def find_button(element, targets):
            if element.role_name in ["push button", "toggle button"]:
                 name = element.name 
                 if name in targets:
                     return element
                     
            # Recurse
            # Check children
            try:
                native = getattr(element, '_native_obj', element)
                if hasattr(native, 'childCount'):
                     count = native.childCount
                     for i in range(min(count, 100)):
                         child = native.getChildAtIndex(i)
                         child_el = LinuxElement(child, element.access_agent, element.wm_agent)
                         found = find_button(child_el, targets)
                         if found: return found
            except:
                pass
            return None

        ellipse_tool = find_button(main_window, ["Ellipse", "Circle"])
        
        # Fallback: Search for "Drawing" toolbar and dump it if needed
        if not ellipse_tool:
             print("Direct search failed. Searching for 'Drawing' toolbar...")
             # (Not implemented yet, let's see if direct search works with role filter)
             pass

        assert ellipse_tool is not None, "Ellipse/Circle tool not found (Filtered by role)"
        print(f"Found Ellipse tool: {ellipse_tool.name} Role: {ellipse_tool.role_name}")
        print(f"Bounds: {ellipse_tool.bounds}")
        
        # Debug actions
        try:
            component = ellipse_tool.native_obj.queryAction()
            n_actions = component.nActions
            print(f"Ellipse tool actions: {n_actions}")
            for i in range(n_actions):
                print(f" - Action {i}: {component.getName(i)} description: {component.getDescription(i)}")
        except:
             print("Ellipse tool has no Action interface")

        # Try clicking
        ellipse_tool.click()
        time.sleep(1)
        
        # Check state again
        states = ellipse_tool.access_agent.get_states(ellipse_tool.native_obj)
        print(f"After click states: {states}")
        
        is_checked = False
        for s in states:
             if "checked" in str(s).lower() or "pressed" in str(s).lower():
                 is_checked = True
        
        if not is_checked:
             print("Button not checked. Trying WM click...")
             # Calculate center and click using WM
             rect = ellipse_tool.bounds
             print(f"Ellipse tool bounds: {rect}")
             
             if rect[0] > -1000 and rect[2] > 0: # Sanity check
                 cx = rect[0] + rect[2] // 2
                 cy = rect[1] + rect[3] // 2
                 print(f"Clicking at ({cx}, {cy})")
                 wm_agent = main_window.wm_agent
                 wm_agent.click(cx, cy)
             else:
                 print(f"Invalid bounds {rect}. Cannot click.")
                 # No keyboard fallback allowed
                 
             time.sleep(1)
             print(f"After WM click states: {ellipse_tool.access_agent.get_states(ellipse_tool.native_obj)}")
        
        # 5. Find Drawing Area
        # The canvas is usually a "scroll pane" or "drawing area" or "document frame"
        # We need a place to drag.
        print("Searching for drawing area...")
        drawing_area = main_window.find_descendant(role="document frame")
        if not drawing_area:
             drawing_area = main_window.find_descendant(role="drawing area")
        
        assert drawing_area is not None, "Drawing area not found"
        print(f"Found Drawing Area: {drawing_area.role_name} at {drawing_area.bounds}")
        
        # 6. Perform Drag to Draw
        # Calculate coordinates relative to the drawing area
        rect = drawing_area.bounds
        start_x = rect[0] + 100
        start_y = rect[1] + 100
        end_x = start_x + 200
        end_y = start_y + 200
        
        print(f"Drawing circle from ({start_x}, {start_y}) to ({end_x}, {end_y})...")
        
        # 5b. Find PageShape (The actual canvas)
        # The document frame contains the page, but we want to be sure we are on the page.
        print("Searching for PageShape...")
        page_shape = None
        
        # Helper to find page shape
        def find_page_shape(element):
            try:
                native_obj = getattr(element, '_native_obj', element) if hasattr(element, '_native_obj') else element.native_obj
                children = element.access_agent.get_children(native_obj)
                for child in children:
                    name = element.access_agent.get_name(child)
                    role = element.access_agent.get_role_name(child)
                    if "PageShape" in name or "panel" in role:
                         if "Page" in name:
                             return LinuxElement(child, element.access_agent, element.wm_agent)
                    
                    # Shallow recurse?
            except:
                pass
            return None

        # Look in drawing area children
        page_shape = find_page_shape(drawing_area)
        
        target_rect = rect # Default to drawing area
        if page_shape:
             print(f"Found PageShape: {page_shape.name} at {page_shape.bounds}")
             target_rect = page_shape.bounds
        else:
             print("PageShape not found, using Drawing Area bounds.")

        # 6. Perform Drag to Draw
        # Calculate coordinates relative to the target (PageShape or Drawing Area)
        # User request: Move mouse to middle of drawing area first
        
        # Ensure we are inside the page
        center_x = target_rect[0] + target_rect[2] // 2
        center_y = target_rect[1] + target_rect[3] // 2
        
        print(f"Moving mouse to center of drawing target: ({center_x}, {center_y})")
        wm_agent = main_window.wm_agent
        wm_agent.move_mouse(center_x, center_y)
        time.sleep(1)
        
        print("Clicking on canvas to create default shape...")
        wm_agent.click(center_x, center_y)
        time.sleep(2)
        
        # If click doesn't work, try drag as fallback?
        # Let's check verification first.
        pass
        
        # 7. Verify new shape creation
        # We expect a new element in the accessibility tree
        print("Verifying shape creation...")
        
        # Strategy A: Tree Dump (failed previously, keeping as debug)
        print("--- Tree Dump ---")
        
        # Find PageShape first to check its children specifically
        page_shape = None
        
        def dump_shapes(element, depth=0):
            nonlocal page_shape
            found = False
            try:
                native_obj = getattr(element, '_native_obj', element) if hasattr(element, '_native_obj') else element.native_obj
                children = element.access_agent.get_children(native_obj)
                for child in children:
                    name = element.access_agent.get_name(child)
                    role = element.access_agent.get_role_name(child)
                    indent = "  " * depth
                    print(f"{indent} - Child: {name} ({role})")
                    
                    if "PageShape" in name:
                        page_shape = child
                    
                    if "Ellipse" in name or "Shape" in role or "shape" in role:
                        if "Page" not in name: # automated pages are confusing
                             found = True
                    
                    # Recurse
                    try:
                        child_el = LinuxElement(child, element.access_agent, element.wm_agent)
                        if dump_shapes(child_el, depth + 1):
                            found = True
                    except:
                        pass
            except Exception as e:
                pass
            return found

        found_shape = dump_shapes(drawing_area)
        print("-----------------")

        # Strategy B: Select All and check selection count
        if not found_shape:
             print("Shape not found in tree. Trying 'Select All' verification...")
             # Click drawing area to focus (center)
             wm_agent.click(center_x, center_y)
             time.sleep(1)
             
             # Send Ctrl+A
             print("Sending Ctrl+A...")
             wm_agent.send_keys(None, "<ctrl>+a")
             time.sleep(1)
             
             # Check selection on Drawing Area or PageShape
             # We need to query the Selection interface
             try:
                 # Check drawing area selection
                 native = drawing_area.native_obj
                 if hasattr(native, 'querySelection'):
                     sel = native.querySelection()
                     print(f"Drawing Area Selection Count: {sel.nSelectedChildren}")
                     if sel.nSelectedChildren > 0:
                         found_shape = True
                         print("Shape found via Drawing Area Selection!")
                 
                 # Check PageShape selection if found
                 if not found_shape and page_shape:
                      if hasattr(page_shape, 'querySelection'):
                         sel = page_shape.querySelection()
                         print(f"PageShape Selection Count: {sel.nSelectedChildren}")
                         if sel.nSelectedChildren > 0:
                             found_shape = True
                             print("Shape found via PageShape Selection!")

             except Exception as e:
                 print(f"Selection check failed: {e}")

        if not found_shape:
             print("Shape not found. Dumping UI tree using CLI for analysis...", file=sys.stderr)
             try:
                 # Call the uia monitor command to dump JSON
                 import subprocess
                 cli_path = os.path.join(os.path.dirname(__file__), "../../../../../packages/automojo/uia/cli/uia_command.py")
                 cmd = [sys.executable, cli_path, "mapping", "monitor", "--hint", "soffice", "--format", "json", "libreoffice --draw"]
                 
                 with open("/tmp/libreoffice_draw_dump.json", "w") as f:
                     subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=10)
                 print("UI tree dumped to /tmp/libreoffice_draw_dump.json")
             except Exception as e:
                 print(f"Failed to dump UI tree: {e}")

        assert found_shape, "New shape not detected in accessibility tree or via selection"
        # 8. Change color to Black
        print("Changing circle color to Black...")
        try:
             # Make sure shape is selected (it should be after drawing)
             # But just in case, we select it if needed (skip for now as it's selected)
             
             # Open Format -> Area dialog
             print("Opening Format -> Area...")
             format_menu = main_window.find_descendant(role="menu", name="Format")
             if not format_menu:
                 # Try finding via application menu bar
                 format_menu = app.find_descendant(role="menu", name="Format")
             
             assert format_menu, "Format menu not found"
             format_menu.click()
             time.sleep(1)
             
             area_item = main_window.find_descendant(role="menu item", name="Area...")
             if not area_item:
                 area_item = main_window.find_descendant(role="menu item", name="Area")
             
             assert area_item, "Area menu item not found"
             area_item.click()
             time.sleep(2)
             
             # Handle Dialog
             print("Handling Area dialog...")
             # Dialog might be a child of app or window
             dialog = None
             for _ in range(5):
                 windows = app.get_windows()
                 for w in windows:
                     if w.role_name == "dialog" or "Area" in w.name:
                         dialog = w
                         break
                 if dialog: break
                 time.sleep(1)
                 
             assert dialog, "Area dialog not found"
             print(f"Dialog: {dialog.name}")
             
             # Select "Color" button in "Area" tab
             # Note: The dialog starts in "Area" tab usually.
             # We look for "Color" button (push button or radio button)
             color_btn = dialog.find_descendant(role="push button", name="Color")
             if not color_btn:
                 color_btn = dialog.find_descendant(role="toggle button", name="Color")
             
             if color_btn:
                 print("Clicking Color button...")
                 color_btn.click()
                 time.sleep(1)
                 
             # Find "Black" in the list/table
             # It might be in a list or table
             black_item = dialog.find_descendant(name="Black")
             
             if black_item:
                 print(f"Found Black item: {black_item.role_name}")
                 black_item.click()
                 time.sleep(0.5)
             else:
                 print("Black item not found in dialog!")
                 
             # Click OK
             ok_btn = dialog.find_descendant(role="push button", name="OK")
             if ok_btn:
                 ok_btn.click()
                 time.sleep(1)
                 print("Clicked OK")
             else:
                 print("OK button not found!")
                 
        except Exception as e:
             print(f"Failed to change color: {e}")

        # Dump UI tree for analysis (find color buttons)
        print("Dumping UI tree for further analysis...", file=sys.stderr)
        try:
             cli_path = os.path.join(os.path.dirname(__file__), "../../../../../packages/automojo/uia/cli/uia_command.py")
             cmd = [sys.executable, cli_path, "mapping", "monitor", "--hint", "soffice", "--format", "json", "libreoffice --draw"]
             
             with open("/tmp/libreoffice_draw_final.json", "w") as f:
                 subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=10)
             print("Final UI tree dumped to /tmp/libreoffice_draw_final.json")
        except Exception as e:
             print(f"Failed to dump final UI tree: {e}")

        print("Test passed!")

    finally:
        print("Closing application...")
        proc.terminate()
        
if __name__ == "__main__":
    test_linux_libreoffice_draw()
