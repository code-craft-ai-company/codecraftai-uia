
import unittest
from typing import List, Optional
from ccai.uia.platforms.base import UIElement
from ccai.uia.model.declarative import ElementHint

class MockElement(UIElement):
    def __init__(self, name: str, role: str, parent: Optional['UIElement'] = None):
        super().__init__(parent)
        self._name = name
        self._role = role
        self._children = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return self._role
        
    @property
    def is_visible(self) -> bool: return True
    @property
    def is_enabled(self) -> bool: return True
    @property
    def bounds(self): return (0,0,0,0)
    @property
    def position(self): return (0,0)
    @property
    def size(self): return (0,0)
    
    def add_child(self, child: 'MockElement'):
        self._children.append(child)
        
    def find_elements(self, **kwargs) -> List['UIElement']:
        return self._children
        
    def click(self): pass
    def type_keys(self, keys): pass
    def find_element(self, **kwargs): pass
    def __repr__(self): return f"Mock({self.name}, {self.role})"

class TestXPathResolution(unittest.TestCase):
    def setUp(self):
        # Tree Structure:
        # Root
        #  - A1 (role:button)
        #    - B1 (role:text, name:Inside)
        #  - A2 (role:panel)
        #    - B2 (role:button, name:OK)
        #    - B3 (role:button, name:Cancel)
        #      - C1 (role:icon)
        
        self.root = MockElement("Root", "root")
        
        self.a1 = MockElement("A1", "button", self.root)
        self.root.add_child(self.a1)
        
        self.b1 = MockElement("Inside", "text", self.a1)
        self.a1.add_child(self.b1)
        
        self.a2 = MockElement("A2", "panel", self.root)
        self.root.add_child(self.a2)
        
        self.b2 = MockElement("OK", "button", self.a2)
        self.a2.add_child(self.b2)
        
        self.b3 = MockElement("Cancel", "button", self.a2)
        self.a2.add_child(self.b3)
        
        self.c1 = MockElement("Icon", "icon", self.b3)
        self.b3.add_child(self.c1)

    def test_direct_child(self):
        hint = ElementHint(path="/{name:A1}")
        result = hint.resolve(self.root)
        self.assertEqual(result, self.a1)

    def test_descendant_search(self):
        hint = ElementHint(path="//{name:OK}")
        result = hint.resolve(self.root)
        self.assertEqual(result, self.b2)

    def test_nested_path(self):
        hint = ElementHint(path="/{role:panel}/{name:Cancel}")
        result = hint.resolve(self.root)
        self.assertEqual(result, self.b3)

    def test_wildcard_property(self):
        hint = ElementHint(path="//{name:Can*}")
        result = hint.resolve(self.root)
        self.assertEqual(result, self.b3)

    def test_contains_property(self):
        hint = ElementHint(path="//{name:~nsid}") # Inside
        result = hint.resolve(self.root)
        self.assertEqual(result, self.b1)
        
    def test_wildcard_node(self):
        # Root -> * -> B2(OK)
        hint = ElementHint(path="/*/{name:OK}")
        result = hint.resolve(self.root)
        self.assertEqual(result, self.b2)

    def test_relative_self(self):
        # Root -> A2 --(relative)--> ./{name:OK}
        hint = ElementHint(path="./{name:OK}")
        result = hint.resolve(self.a2)
        self.assertEqual(result, self.b2)
    
    def test_complex_chain(self):
        # Root // A2 / Cancel / .
        hint = ElementHint(path="//{name:A2}/{name:Cancel}/.")
        result = hint.resolve(self.root)
        self.assertEqual(result, self.b3)

    def test_not_found(self):
        hint = ElementHint(path="//{name:NonExistent}")
        result = hint.resolve(self.root)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
