
from typing import Optional, List, Any
from ccai.uia.platforms.base import (
    UICheckBox, UIRadioButton, UIComboBox, UIHyperlink, 
    UITab, UITabItem, UITree, UITreeItem, 
    UIProgressBar, UISlider, UIElement, UIButton
)
from ccai.uia.platforms.linux.wrappers.uiaelement import LinuxElement
from ccai.uia.exceptions import InteractionError


def _states_include_selected(states: List[Any]) -> bool:
    """
        Checks a state list returned by :meth:`AccessibilityAgent.get_states` for the selected state.
        pyatspi reports states as ``StateType`` values whose string form is ``STATE_SELECTED``, while
        other agents report the plain name ``selected``; both forms are accepted, the same way
        :class:`LinuxElement` checks the visible and enabled states.

        :param states: The states of an accessible element.

        :returns: True when the selected state is present.
    """
    rtnval = False
    for state in states:
        state_name = str(state)
        if state_name == "selected" or state_name.endswith("SELECTED"):
            rtnval = True
            break
    return rtnval

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
        """
            Returns the combo box item that carries the selected state, or None when no item is selected.

            The accessibility agent does not expose the AT-SPI Selection interface, so the items of the
            combo box (the 'menu item' and 'list item' descendants that :meth:`select` searches, which
            toolkits place inside a 'menu' or 'list' child) are checked for the selected state.
        """
        rtnval = None
        descendants = self.find_elements()
        for candidate in descendants:
            if candidate.role_name in ('menu item', 'list item'):
                candidate_states = self.access_agent.get_states(candidate.native_obj)
                if _states_include_selected(candidate_states):
                    rtnval = candidate
                    break
        return rtnval


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
        """
            Returns the page tab that carries the selected state, or None when no tab is selected.

            AT-SPI places the page tabs directly under the page tab list, so the direct children are
            checked first; searching the whole subtree first could return a selected tab of a tab list
            nested inside one of the tab pages.  When the list has no direct page tab children, the
            whole subtree is searched, which is where :meth:`select_tab` looks.
        """
        rtnval = None
        tabs = self.find_elements(role='page tab', recursive=False)
        if len(tabs) == 0:
            tabs = self.find_elements(role='page tab')
        for tab in tabs:
            if isinstance(tab, LinuxTabItem) and tab.is_selected:
                rtnval = tab
                break
        return rtnval

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
        """
            True when the tab carries the selected state (``STATE_SELECTED`` from pyatspi).
        """
        states = self.access_agent.get_states(self._native_obj)
        rtnval = _states_include_selected(states)
        return rtnval

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
