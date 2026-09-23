
from typing import Optional, List
from ccai.uia.platforms.base import (
    UIButton,
    UIText,
    UIList,
    UIMenu,
    UIMenuItem,
    UIMenuBar,
    UIElement,
)
from ccai.uia.platforms.macos.wrappers.uiaaccessibility import (
    UiaAccessibilityElement,
    kAXValueAttribute,
)
from ccai.uia.exceptions import InteractionError

class MacUIButton(UiaAccessibilityElement, UIButton):
    """
    MacOS implementation of a Button.
    """
    @property
    def label(self) -> str:
        return self.name

    def double_click(self) -> None:
        self.click()
        self.click()

class MacUIText(UiaAccessibilityElement, UIText):
    """
    MacOS implementation of Text controls.
    """
    @property
    def text(self) -> str:
        return self.get_text()

    @property
    def is_editable(self) -> bool:
        # Simple heuristic based on role
        role = self.role
        return role in ["AXTextField", "AXTextArea"]

    def get_text(self) -> str:
        val = self._get_value_text()
        if val is None:
            return self.name
        return val

    def set_text(self, text: str) -> None:
        if kAXValueAttribute and self._set_attribute(kAXValueAttribute, text):
            return
            
        # Fallback to typing
        self.max_focus_attempts = 3
        try:
            self.click()
            # self.clear() ?
            self.type_keys(text)
        except Exception:
            raise InteractionError("Failed to set text via attribute or typing.")

    def clear(self) -> None:
        if kAXValueAttribute:
             self._set_attribute(kAXValueAttribute, "")

class MacUIList(UiaAccessibilityElement, UIList):
    """
    MacOS implementation of a List.
    """
    @property
    def item_count(self) -> int:
        return len(self.children())

    def get_item(self, index: int) -> Optional[UIElement]:
        children = self.children()
        if 0 <= index < len(children):
            return children[index]
        return None

    def select_item(self, index: int) -> None:
        item = self.get_item(index)
        if item:
            item.click()
    
    def scroll_to_item(self, index: int) -> None:
        pass

class MacUIMenuItem(UiaAccessibilityElement, UIMenuItem):
    """
    MacOS implementation of a Menu Item.
    """
    @property
    def is_checked(self) -> bool:
        found, val = self._copy_attribute("AXMenuItemMarkChar")
        return bool(val)

    @property
    def is_separator(self) -> bool:
        # Check title or role
        return self.name == "" and self.role == "AXMenuItem" # Loose check

    def invoke(self) -> None:
        self.click()

class MacUIMenu(UiaAccessibilityElement, UIMenu):
    """
    MacOS implementation of a Menu.
    """
    @property
    def is_open(self) -> bool:
        return True 

    def open(self) -> None:
        self.click()

    def close(self) -> None:
        pass

    def get_item(self, name: str) -> Optional[UIMenuItem]:
        child = self.find_element(name=name, recursive=False)
        if child:
            return MacUIMenuItem(self.controller, child._native_obj)
        return None

    def get_items(self) -> List[UIMenuItem]:
        items = []
        for child in self.children():
            # child is UiaAccessibilityElement
            items.append(MacUIMenuItem(self.controller, child._native_obj))
        return items

class MacUIMenuBar(UiaAccessibilityElement, UIMenuBar):
    """
    MacOS implementation of a Menu Bar.
    """
    def get_menus(self) -> List[UIMenu]:
        menus = []
        for child in self.children():
            menus.append(MacUIMenu(self.controller, child._native_obj))
        return menus

    def get_menu(self, name: str) -> Optional[UIMenu]:
        child = self.find_element(name=name, recursive=False)
        if child:
            return MacUIMenu(self.controller, child._native_obj)
        return None
