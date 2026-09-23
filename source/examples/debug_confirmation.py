#!/usr/bin/env python3
from ccai.uia.factory import AutomationFactory
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement

def dump_tree(element, depth=0, max_depth=5):
    indent = "  " * depth
    try:
        role = element.role
        role_name = element.role_name
        name = element.name or ""
        
        print(f"{indent}{role_name}: '{name}' (Role: {role})")
        
        if depth >= max_depth:
            return

        children = element.access_agent.get_children(element.native_obj)
        for child in children:
            try:
                child_el = LinuxElement(child, element.access_agent, element.wm_agent)
                dump_tree(child_el, depth + 1, max_depth)
            except Exception:
                # Best-effort dump; a child that disappears or cannot be wrapped is skipped.
                pass
    except Exception as e:
        print(f"{indent}Error: {e}")

def main():
    automation = AutomationFactory.get_automation_engine()
    
    # Ensure LibreOffice Calc is running
    app = automation.get_application_by_name("soffice")
    if not app:
        app = automation.get_application_by_name("Calc")
    
    if not app:
        print("LibreOffice Calc not found.")
        return

    print(f"Found App: {app}")
    
    windows = app.get_windows()
    print(f"get_windows() returned {len(windows)} windows")
    for w in windows:
        print(f"  Window: '{w.title}'")
        
        # If it's a dialog (Save or Confirm), dump it
        if "Save" in w.title or "Confirm" in w.title or "Replace" in w.title or "Exists" in w.title:
            print(f"Dumping Dialog: {w.title}")
            dump_tree(w, 0, 5)

    print("Dumping App Children (to find nested dialogs):")
    children = app.access_agent.get_children(app.native_obj)
    for child in children:
        try:
            dump_tree(LinuxElement(child, app.access_agent, app.wm_agent), 0, 3)
        except Exception:
             # Best-effort dump; an application child that disappears or cannot be wrapped is skipped.
             pass

if __name__ == "__main__":
    main()
