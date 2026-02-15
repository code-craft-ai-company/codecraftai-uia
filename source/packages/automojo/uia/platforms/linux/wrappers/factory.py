
from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
    from automojo.uia.platforms.linux.agents.linuxbaseagents import AccessibilityAgent, WindowManagerAgent

class LinuxWrapperFactory:
    """
        Factory for creating specialized Linux wrappers based on AT-SPI roles.
    """
    
    @staticmethod
    def create_wrapper(native_obj: Any, access_agent: 'AccessibilityAgent', wm_agent: Optional['WindowManagerAgent'], parent: Optional['LinuxElement'] = None) -> 'LinuxElement':
        """
            Creates the appropriate wrapper for the given native object.
        """
        # Determine Role
        role_name = access_agent.get_role_name(native_obj)
        
        # Import wrappers here to avoid circular dependencies at module level
        # Core
        from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
        # Windows
        from automojo.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
        # Tables
        from automojo.uia.platforms.linux.wrappers.tableelement import TableElement
        # Controls
        from automojo.uia.platforms.linux.wrappers.controls import (
            LinuxCheckBox, LinuxRadioButton, LinuxComboBox, 
            LinuxHyperlink, LinuxTab, LinuxTabItem, 
            LinuxTree, LinuxTreeItem, LinuxProgressBar, LinuxSlider,
            LinuxButton
        )
        # Menus
        from automojo.uia.platforms.linux.wrappers.menuelement import (
            LinuxMenuBar, LinuxMenu, LinuxMenuItem
        )
        
        # Mapping
        if role_name in ['frame', 'window', 'dialog']:
            return LinuxWindow(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'table':
            return TableElement(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'push button':
            return LinuxButton(native_obj, access_agent, wm_agent, parent=parent)

        elif role_name == 'check box':
            return LinuxCheckBox(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'radio button':
            return LinuxRadioButton(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'combo box':
            return LinuxComboBox(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'link':
            return LinuxHyperlink(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'page tab list':
            return LinuxTab(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'page tab':
            return LinuxTabItem(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'tree':
            return LinuxTree(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'tree item': 
            # Often tree items are table cells or specialized.
            pass 
            
        elif role_name == 'progress bar':
            return LinuxProgressBar(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'slider':
            return LinuxSlider(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'menu bar':
            return LinuxMenuBar(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'menu':
            # Note: A 'menu' role might be a top-level menu or sub-menu
            return LinuxMenu(native_obj, access_agent, wm_agent, parent=parent)
            
        elif role_name == 'menu item':
            return LinuxMenuItem(native_obj, access_agent, wm_agent, parent=parent)
            
        # Default
        return LinuxElement(native_obj, access_agent, wm_agent, parent=parent)
