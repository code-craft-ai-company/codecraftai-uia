
import platform
import time
import shutil
import sys
import os

# Adjust path for local execution relative to repo root
sys.path.append(os.path.abspath("source"))
sys.path.append(os.path.abspath("source/testroots"))

from ccai.errors.exceptions import SkipError
from ccai.uia.factory import AutomationFactory

def test_linux_libreoffice_draw():
    """
    Verifies that we can launch LibreOffice Draw and draw a circle.
    """
    if platform.system() != "Linux":
        raise SkipError("the Linux desktop tests need a Linux host")

    if shutil.which("libreoffice") is None:
        raise SkipError("libreoffice is not installed on this host")

    automation = AutomationFactory.get_automation_engine()
    
    # 1. Launch LibreOffice Draw
    print("Launching LibreOffice Draw...")
    import subprocess
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "gtk3"
    env["GDK_BACKEND"] = "x11"
    proc = subprocess.Popen(["libreoffice", "--draw", "--norestore"], env=env)
    
    try:
        # Declarative Usage
        from ccai.uia.platforms.linux.mappings.libreoffice_draw import LibreOfficeDraw
        
        # 2. Find Application using Declarative Mapping
        app = None
        for _ in range(20):
            time.sleep(1)
            app = LibreOfficeDraw.attach(automation)
            if not app:
                # Fallback purely on name "Draw" if soffice fails (though attach uses soffice)
                app = automation.get_application_by_name("Draw")
            if app:
                break
        
        assert app is not None, "LibreOffice Draw not found"
        print(f"Found App: {app.name}")
        
        # 3. Find Main Window using Hint
        main_window = None
        for _ in range(10):
            windows = app.get_windows()
            if windows:
                # manual match against hint if needed, or just take first non-recovery
                # assuming first is main for draw usually
                main_window = windows[0]
                break
            time.sleep(1)
            
        assert main_window is not None, "Main window not found"
        print(f"Main Window: {main_window.title}")
        main_window.activate()
        time.sleep(2)
        
        # 4. Find the "Ellipse" tool
        # Using Declarative Hints
        print("Searching for Ellipse tool in toolbars...")
        
        ellipse_tool = LibreOfficeDraw.EllipseTool.resolve(main_window)
        if not ellipse_tool:
             # Try Circle hint if Ellipse not found
             ellipse_tool = LibreOfficeDraw.CircleTool.resolve(main_window)
        
        assert ellipse_tool is not None, "Ellipse/Circle tool not found (via Declarative Hint)"
        print(f"Found Ellipse tool: {ellipse_tool.name} Role: {ellipse_tool.role_name}")
        print(f"Bounds: {ellipse_tool.bounds}")
        
        # Debug actions
        try:
            component = ellipse_tool.native_obj.queryAction()
            n_actions = component.nActions
            print(f"Ellipse tool actions: {n_actions}")
            for i in range(n_actions):
                print(f" - Action {i}: {component.getName(i)} description: {component.getDescription(i)}")
        except Exception:
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
                 
             time.sleep(1)
             print(f"After WM click states: {ellipse_tool.access_agent.get_states(ellipse_tool.native_obj)}")
        
        # 5. Find Drawing Area using Hints
        print("Searching for drawing area...")
        drawing_area = LibreOfficeDraw.DrawingArea.resolve(main_window)
        
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
        print("Searching for PageShape...")
        # Using Hint
        page_shape = LibreOfficeDraw.PageShape.resolve(main_window)
        if not page_shape and drawing_area:
             page_shape = LibreOfficeDraw.PageShape.resolve(drawing_area)
        
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
        
        # 7. Verify new shape creation
        # We expect a new element in the accessibility tree
        print("Verifying shape creation...")
        
        # Strategy B: Select All and check selection count
        found_shape = False
        print("Shape verification... Trying 'Select All' verification...")
        # Click drawing area to focus (center)
        wm_agent.click(center_x, center_y)
        time.sleep(1)
        
        # Send Ctrl+A
        print("Sending Ctrl+A...")
        wm_agent.send_keys(None, "<ctrl>+a")
        time.sleep(1)
        
        # Check selection on Drawing Area or PageShape
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
             # Simplified dump
             print("Shape not found via selection.")

        assert found_shape, "New shape not detected in accessibility tree or via selection"
        
        # 8. Change color to Black
        print("Changing circle color to Black...")
        try:
             # Open Format -> Area dialog
             print("Opening Format -> Area...")
             
             # Use Declarative Hints
             format_menu = LibreOfficeDraw.MenuBar.Format.resolve(main_window)
             if not format_menu:
                 # Try finding via application menu bar
                 format_menu = LibreOfficeDraw.MenuBar.Format.resolve(app)
             
             assert format_menu, "Format menu not found"
             format_menu.click()
             time.sleep(1)
             
             area_item = LibreOfficeDraw.FormatAreaItem.resolve(main_window)
             if not area_item:
                 # Standard find fallback
                 area_item = main_window.find_descendant(name="Area...")
                 if not area_item: area_item = main_window.find_descendant(name="Area")
             
             assert area_item, "Area menu item not found"
             area_item.click()
             time.sleep(2)
             
             # Handle Dialog
             print("Handling Area dialog...")
             # Dialog might be a child of app or window
             dialog = None
             area_dialog_hint = LibreOfficeDraw.AreaDialog
             
             for _ in range(5):
                 windows = app.get_windows()
                 for w in windows:
                     if area_dialog_hint.name in w.name or "Area" in w.name or "Area" in w.title:
                         dialog = w
                         break
                 if dialog: break
                 time.sleep(1)
                 
             assert dialog, "Area dialog not found"
             print(f"Dialog: {dialog.name}")
             
             # Select "Color" button in "Area" tab
             color_btn = LibreOfficeDraw.AreaDialog.ColorButton.resolve(dialog)
             
             if color_btn:
                 print("Clicking Color button...")
                 color_btn.click()
                 time.sleep(1)
                 
             # Find "Black" in the list/table
             black_item = LibreOfficeDraw.AreaDialog.BlackItem.resolve(dialog)
             
             if black_item:
                 print(f"Found Black item: {black_item.role_name}")
                 black_item.click()
                 time.sleep(0.5)
             else:
                 print("Black item not found in dialog!")
                 # Fallback find
                 black_item = dialog.find_descendant(name="Black")
                 if black_item: black_item.click()
                 
             # Click OK
             ok_btn = LibreOfficeDraw.AreaDialog.OKButton.resolve(dialog)
             if ok_btn:
                 ok_btn.click()
                 time.sleep(1)
                 print("Clicked OK")
             else:
                 print("OK button not found!")
                 # Fallback
                 dialog.type_keys("\n")
                 
        except Exception as e:
             print(f"Failed to change color: {e}")
             raise

        print("Test passed!")
    finally:
        print("Closing application...")
        proc.terminate()
        
if __name__ == "__main__":
    test_linux_libreoffice_draw()
