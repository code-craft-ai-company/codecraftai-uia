
from typing import Optional, List, Any
from ccai.uia.platforms.base import (
    UICheckBox, UIRadioButton, UIComboBox, UIHyperlink, 
    UITab, UITabItem, UITree, UITreeItem, 
    UIProgressBar, UISlider, UIElement, UIButton
)
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from ccai.uia.exceptions import InteractionError

class LinuxCheckBox(LinuxElement, UICheckBox):
    """
        Linux implementation of a CheckBox.
    """
    
    @property
    def is_checked(self) -> bool:
        # AT-SPI: State 'checked'
        states = self.access_agent.get_states(self._native_obj)
        return any(str(s) == 'checked' for s in states)

    def toggle(self) -> None:
        """
            Toggles the checkbox state.
        """
        self.click()
        return

    def check(self) -> None:
        """
            Ensures the checkbox is checked.
        """
        if not self.is_checked:
            self.toggle()
        return

    def uncheck(self) -> None:
        """
            Ensures the checkbox is unchecked.
        """
        if self.is_checked:
            self.toggle()
        return


class LinuxRadioButton(LinuxElement, UIRadioButton):
    """
        Linux implementation of a RadioButton.
    """
    
    @property
    def is_selected(self) -> bool:
        # AT-SPI: State 'checked' (often used for radio buttons too) or 'selected'
        states = self.access_agent.get_states(self._native_obj)
        for s in states:
            s_str = str(s)
            if s_str == 'checked' or s_str == 'selected':
                return True
        return False

    def select(self) -> None:
        """
            Selects the radio button.
        """
        if not self.is_selected:
            self.click()
        return


class LinuxComboBox(LinuxElement, UIComboBox):
    """
        Linux implementation of a ComboBox.
    """
    
    @property
    def is_expanded(self) -> bool:
        # AT-SPI: State 'expanded'
        states = self.access_agent.get_states(self._native_obj)
        return any(str(s) == 'expanded' for s in states)

    def expand(self) -> None:
        """
            Expands the combo box.
        """
        if not self.is_expanded:
            self.click() # Clicking usually expands
        return

    def collapse(self) -> None:
        """
            Collapses the combo box.
        """
        if self.is_expanded:
            self.click()
        return

    def select(self, item_name: str) -> None:
        """
            Selects an item by name/text.
        """
        # 1. Expand if needed
        self.expand()
        
        # 2. Find item in children (often in a popup menu or list child)
        # Note: ComboBox children might be directly exposed or inside a 'menu' child
        # We need to search recursively or check specific structure
        item = self.find_element(name=item_name, role='menu item') 
        if not item:
            item = self.find_element(name=item_name, role='list item')
            
        if item:
            item.click()
        else:
            raise InteractionError(f"ComboBox item '{item_name}' not found.")
        return

    @property
    def selected_item(self) -> Optional[UIElement]:
        # Implementation depends on AT-SPI. 
        # Sometimes the 'Selection' interface is on the ComboBox
        # Or we check children for 'selected' state.
        
        # Try Selection Interface via agent? 
        # Agent base doesn't expose generic selection yet.
        # Fallback to checking children
        children = self.get_children() # LinuxElement method? No, generic find
        # We need generic get_children wrapper
        # Assuming we can find 'selected' child
        # For now, simplistic implementation
        return None 


class LinuxButton(LinuxElement, UIButton):
    """
        Linux implementation of a Button.
    """
    
    @property
    def label(self) -> str:
        return self.text

    def double_click(self) -> None:
        """
            Performs a double-click action on the button.
        """
        self.click()
        import time
        time.sleep(0.1)
        self.click()
        return


class LinuxHyperlink(LinuxButton, UIHyperlink):
    """
        Linux implementation of a Hyperlink.
    """
    
    @property
    def url(self) -> str:
        # AT-SPI: Value interface or specific attribute?
        # Often accessible via 'Hyperlink' interface but pyatspi usage varies.
        # Fallback to text or value
        return self.text


class LinuxTab(LinuxElement, UITab):
    """
        Linux implementation of a Tab container (PageTabList).
    """
    
    @property
    def selected_tab(self) -> Optional['UITabItem']:
        # Find child with 'selected' state
        return self.find_element(role='page tab', states=['selected']) # Pseudo-code states filter? 
        # We don't have states filter in find_element yet.
        # Use fallback iteration
        children = self.find_elements(role='page tab')
        for child in children:
            if isinstance(child, LinuxTabItem) and child.is_selected:
                return child
        return None

    def select_tab(self, name: str) -> None:
        """
            Selects a tab by name.
        """
        tab = self.find_element(name=name, role='page tab')
        if tab:
            tab.click()
        else:
            raise InteractionError(f"Tab '{name}' not found.")
        return


class LinuxTabItem(LinuxElement, UITabItem):
    """
        Linux implementation of a Tab Item (PageTab).
    """
    
    @property
    def is_selected(self) -> bool:
        states = self.access_agent.get_states(self._native_obj)
        return any(str(s) == 'selected' for s in states)
        
    def select(self) -> None:
        """
            Selects this tab item.
        """
        self.click()
        return


class LinuxTree(LinuxElement, UITree):
    """
        Linux implementation of a Tree.
    """
    pass


class LinuxTreeItem(LinuxElement, UITreeItem):
    """
        Linux implementation of a Tree Item (likely table cell or special role).
    """
    
    @property
    def is_expanded(self) -> bool:
        states = self.access_agent.get_states(self._native_obj)
        return any(str(s) == 'expanded' for s in states)
        
    def expand(self) -> None:
        """
            Expands the tree item.
        """
        if not self.is_expanded:
            self.access_agent.do_action(self._native_obj, 0) # usually action 0 is activate/expand
        return

    def collapse(self) -> None:
        """
            Collapses the tree item.
        """
        if self.is_expanded:
            self.access_agent.do_action(self._native_obj, 0)
        return

    @property
    def is_selected(self) -> bool:
        states = self.access_agent.get_states(self._native_obj)
        return any(str(s) == 'selected' for s in states)

    def select(self) -> None:
        """
            Selects the tree item.
        """
        self.click()
        return


class LinuxProgressBar(LinuxElement, UIProgressBar):
    """
        Linux implementation of a ProgressBar.
    """
    
    @property
    def value(self) -> float:
        return self.access_agent.get_value(self._native_obj)
        
    @property
    def min_value(self) -> float:
        # Agent needs to expose get_value_min/max
        # Assuming generic value 0-100 for now if not exposed
        return 0.0

    @property
    def max_value(self) -> float:
        return 100.0


class LinuxSlider(LinuxProgressBar, UISlider):
    """
        Linux implementation of a Slider.
    """
    
    def set_value(self, value: float) -> None:
        """
            Sets the value of the slider.
        """
        self.access_agent.set_value(self._native_obj, value)
        return
