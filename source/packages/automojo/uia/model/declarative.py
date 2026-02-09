
from typing import Optional, Type, Any, List, TypeVar, Generic
from automojo.uia.platforms.base import (
    UIElement, UIApplication, UIWindow, AutomationEngine,
    UIButton, UIText, UIList, UIMenu, UIMenuItem, UIMenuBar, UITable,
    UIDialog, UIModalDialog, UISaveDialog, UIModalDialogFileAlreadyExists
)
from automojo.uia.factory import AutomationFactory

T = TypeVar('T', bound=UIElement)

class ElementHint(Generic[T]):
    """
    Declarative hint to locate a UI element of type T.
    
    :param type_class: The expected class of the element (e.g. UIButton). 
                       Used for return type inference and optional runtime validation.
    :param name: The name of the element to match.
    :param role: The role of the element to match.
    :param access_name: Alternate accessibility name.
    """
    def __init__(self, type_class: Type[T] = UIElement, name: str = None, role: str = None, access_name: str = None, path: str = None):
        self.type_class = type_class
        self.name = name
        self.role = role
        self.access_name = access_name
        self.path = path

    def resolve(self, parent: UIElement) -> Optional[T]:
        """
        Resolves the hint to a concrete UI element within the parent context.
        
        :param parent: The parent UI element to search within.
        :return: The found element as type T, or None.
        """
        if self.path:
            return self._resolve_path(parent, self.path)

        # Strategy: Use parent's find capability
        found = None
        
        # Check if parent supports find_descendant (Linux style)
        if hasattr(parent, 'find_descendant'):
            found = parent.find_descendant(name=self.name, role=self.role)
            
        # Check if parent supports find_first_by_role (MacOS style)
        elif hasattr(parent, 'find_first_by_role') and self.role:
            found = parent.find_first_by_role(role=self.role)
            
        elif hasattr(parent, 'find_by_title') and self.name:
            matches = parent.find_by_title(title=self.name)
            if matches:
                found = matches[0]
                
        if found:
            return found # type: ignore
            
        return None

    def _resolve_path(self, parent: UIElement, path: str) -> Optional[T]:
        """
        Resolves an XPath-style path.
        Syntax:
          // : recursive descendant
          /  : direct child
          .  : current element (start)
          *  : wildcard node (any)
          {key:value} : filter properties
             value can contain * (wildcard) or ~ (contains)
        Example: //{name:Calc*}/*/{role:~OK}
        """
        # Parsing tokens
        # Simple parser: split by / but keep empty strings to detect // 
        # Actually regex might be safer or manual scan.
        # Let's do a manual scan for simplicity and control.
        
        segments = self._parse_path(path)
        current_context = [parent]
        
        for segment in segments:
            op, filters = segment
            next_context = []
            
            for el in current_context:
                if op == 'descendant': # //
                    # Find all descendants matching filters
                    # We need a recursive find all. 
                    # Assuming find_elements supports recursion or we iterate.
                    # Base find_elements usually is shallow or deep depending on impl.
                    # Standardizing: find_descendants implies deep.
                    
                    if hasattr(el, 'find_elements'):
                        # If filters is empty/wildcard, we need everything? 
                        # usually //* means all descendants.
                        
                        # Optimization: if underlying engine supports XPath or deep search with criteria, use it.
                        # For now, generic fallback:
                        candidates = []
                        if hasattr(el, 'get_sub_elements'): # internal API?
                             # Fallback to walk
                             candidates = self._walk_tree(el)
                        elif hasattr(el, 'find_elements'):
                             # Try passing criteria directly if supported
                             # Logic: find_elements(depth=-1, **filters)
                             try:
                                 matches = el.find_elements(**self._convert_filters(filters))
                                 # This might generic find direct children only on some platforms?
                                 # We assume find_elements is direct children usually.
                                 # So we need deep walk.
                                 pass
                             except:
                                 pass
                        
                        # Doing a manual walk for generic support
                        matches = self._find_descendants_generic(el, filters)
                        next_context.extend(matches)
                        
                elif op == 'child': # /
                    # Direct children
                    if hasattr(el, 'find_elements'):
                         # Get children and filter
                         # Assuming find_elements returns children
                         children = []
                         try:
                             children = el.find_elements()
                         except:
                             # Try get_children internal
                             access = getattr(el, 'access_agent', None)
                             native = getattr(el, 'native_obj', None) # Linux
                             if access and native:
                                 # Linux specific bypass
                                 try:
                                    child_natives = access.get_children(native)
                                    # Convert back? Complexity high.
                                    # Let's rely on standard find_elements returning list of wrappers
                                    pass
                                 except: pass
                         
                         # Filter manually
                         for child in children:
                             if self._match_filters(child, filters):
                                 next_context.append(child)
                                 
                elif op == 'self': # .
                    if self._match_filters(el, filters):
                        next_context.append(el)
            
            current_context = next_context
            if not current_context:
                return None
        
        return current_context[0] if current_context else None

    def _parse_path(self, path: str) -> List[tuple]:
        """
        Parses path into list of (operation, filters).
        Operations: 'descendant' (//), 'child' (/), 'self' (.)
        """
        segments = []
        # Normalize: replace // with /descendant/ ? 
        # Custom logic:
        # Split by '/' 
        parts = path.split('/')
        # Logic:
        # '' means root or following a / (making it //)
        # 'descendant' marker
        
        # Example: //a/b -> ['', '', 'a', 'b'] -> op:descendant 'a', op:child 'b'
        # Example: /a/b -> ['', 'a', 'b'] -> op:child 'a', op:child 'b' (relative to root? No, hints are relative to parent)
        # Actually / usually means root in xpath. Here relative to parent.
        # But user wants // to be recursive.
        # Let's assume leading / implies direct child of parent.
        # Leading // implies any descendant.
        
        i = 0
        if path.startswith('//'):
            # //{filter}
            parts = path[2:].split('/')
            first_op = 'descendant'
            i = 0
        elif path.startswith('./'):
            parts = path[2:].split('/')
            first_op = 'child' # . is self, / is child. Wait. ./foo means child foo of self.
            # ./{filter} -> child matching filter
            # actually . means self. 
            # if path is just "." -> self.
            # if path starts with ./ -> first segment is child
            i = 0 
        elif path.startswith('.'):
             # just . or .{filter}
             # treated as self
             parts = path.split('/') # . or .{filter} / ...
             # Handle first part specially
             if parts[0].startswith('.'):
                 # self matching filter
                 # parse filter from parts[0][1:]
                 f = self._parse_filters(parts[0][1:])
                 segments.append(('self', f))
                 parts = parts[1:]
                 first_op = 'child' # subsequent match /
             else:
                 first_op = 'child' # fallback
        elif path.startswith('/'):
            # /{filter} -> child
            parts = path[1:].split('/')
            first_op = 'child'
        else:
            # {filter} -> implies child? or descendant?
            # Standard xpath relative path `div/span` implies child.
            parts = path.split('/')
            first_op = 'child'

        # Now processing parts
        current_op = first_op
        
        # Handling double empty for // inside path: a//b -> ['a', '', 'b']
        
        for part in parts:
            if part == '':
                current_op = 'descendant'
                continue
            
            if part == '.':
                # ignore ? a/./b == a/b
                continue
                
            filters = self._parse_filters(part)
            segments.append((current_op, filters))
            current_op = 'child' # Reset to child for next segment unless // seen
            
        return segments

    def _parse_filters(self, token: str) -> dict:
        """
        Parses string like {name:Cal*, role:button} or *
        """
        if token == '*':
            return {}
            
        if not (token.startswith('{') and token.endswith('}')):
            # Assume it's a tag name or role? 
            # In HTML xpath it's tag. Here?
            # Maybe assume check against 'name'?
            return {'name': token}
            
        content = token[1:-1]
        filters = {}
        # naive split by comma
        pairs = content.split(',')
        for pair in pairs:
            if ':' in pair:
                k, v = pair.split(':', 1)
                filters[k.strip()] = v.strip()
        return filters

    def _match_filters(self, element: UIElement, filters: dict) -> bool:
        """
        Checks if element matches filters.
        """
        for k, v in filters.items():
            # map keys to attributes
            # role -> role_name? or role?
            val = None
            if k == 'role':
                 # Try role_name first (human readable)
                 if hasattr(element, 'role_name'):
                     val = element.role_name
                 elif hasattr(element, 'role'):
                     val = str(element.role)
            elif hasattr(element, k):
                val = getattr(element, k)
            
            if val is None:
                return False
                
            val_str = str(val)
            
            # Check match
            if v == '*':
                continue
            elif v.startswith('~'):
                # contains
                target = v[1:]
                if target not in val_str:
                    return False
            elif '*' in v:
                # wildcard pattern - simplified
                # only support * at end for now e.g. Calc*
                if v.endswith('*'):
                    prefix = v[:-1]
                    if not val_str.startswith(prefix):
                        return False
                elif v.startswith('*'):
                    suffix = v[1:]
                    if not val_str.endswith(suffix):
                        return False
                else: 
                     # complex regex? fallback to equality
                     if v != val_str: return False
            else:
                if v != val_str:
                    return False
                    
        return True

    def _find_descendants_generic(self, parent: UIElement, filters: dict) -> List[UIElement]:
        """
        Recursive walk to find descendants matching filters.
        """
        results = []
        # BFS or DFS? DFS easier
        # Try finding children
        children = []
        if hasattr(parent, 'find_elements'):
            children = parent.find_elements()
        elif hasattr(parent, 'get_children'): # Internal
            children = parent.get_children()
            
        for child in children:
            if self._match_filters(child, filters):
                results.append(child)
            
            # Recurse
            results.extend(self._find_descendants_generic(child, filters))
            
        return results

    def _convert_filters(self, filters: dict) -> dict:
        """Helper to convert path filters to kwargs for find_elements if needed"""
        return filters # simplified

# Specialized Hints for common controls
class WindowHint(ElementHint[UIWindow]):
    """Hint for locating a Window."""
    def __init__(self, name: str = None, role: str = "window", access_name: str = None, path: str = None):
        super().__init__(UIWindow, name, role, access_name, path)

class DialogHint(ElementHint[UIDialog]):
    """Hint for locating a Dialog."""
    def __init__(self, name: str = None, role: str = "dialog", access_name: str = None, path: str = None):
        super().__init__(UIDialog, name, role, access_name, path)

class ButtonHint(ElementHint[UIButton]):
    """Hint for locating a Button."""
    def __init__(self, name: str = None, role: str = "push button", access_name: str = None, path: str = None):
        super().__init__(UIButton, name, role, access_name, path)

class TextHint(ElementHint[UIText]):
    """Hint for locating a Text control."""
    def __init__(self, name: str = None, role: str = "text", access_name: str = None, path: str = None):
        super().__init__(UIText, name, role, access_name, path)

class MenuBarHint(ElementHint[UIMenuBar]):
    """Hint for locating a Menu Bar."""
    def __init__(self, name: str = None, role: str = "menu bar", access_name: str = None, path: str = None):
        super().__init__(UIMenuBar, name, role, access_name, path)

class MenuHint(ElementHint[UIMenu]):
    """Hint for locating a Menu."""
    def __init__(self, name: str = None, role: str = "menu", access_name: str = None, path: str = None):
        super().__init__(UIMenu, name, role, access_name, path)

class MenuItemHint(ElementHint[UIMenuItem]):
    """Hint for locating a Menu Item."""
    def __init__(self, name: str = None, role: str = "menu item", access_name: str = None, path: str = None):
        super().__init__(UIMenuItem, name, role, access_name, path)

class TableHint(ElementHint[UITable]):
    """Hint for locating a Table control."""
    def __init__(self, name: str = None, role: str = "table", access_name: str = None, path: str = None):
        super().__init__(UITable, name, role, access_name, path)


class DeclarativeApplication:
    """
    Base class for declarative application models.
    Note: This is a factory/proxy, not the actual application instance.
    It returns a concrete UIApplication when valid.
    """
    
    APPLICATION_COMMAND: str = None

    @classmethod
    def attach(cls, automation_engine: Optional[AutomationEngine] = None) -> Optional[UIApplication]:
        """
        Attaches to the running application matching the hint.
        """
        if not automation_engine:
             automation_engine = AutomationFactory.get_automation_engine()
             
        if cls.APPLICATION_NAME:
            return automation_engine.get_application_by_name(cls.APPLICATION_NAME)
        
        # Future: Implement more complex matching logic using APPLICATION_HINT
        return None

    @classmethod
    def launch_or_attach(cls, automation_engine: Optional[AutomationEngine] = None) -> Optional[UIApplication]:
        """
        Launches the application if not running, or attaches to it.
        """
        app = cls.attach(automation_engine)
        if app:
            return app
            
        if cls.APPLICATION_COMMAND:
            import subprocess
            import shlex
            import time
            
            print(f"Launching application: {cls.APPLICATION_COMMAND}")
            subprocess.Popen(shlex.split(cls.APPLICATION_COMMAND))
            
            # Wait for app to appear
            for _ in range(20):
                time.sleep(1)
                app = cls.attach(automation_engine)
                if app:
                    print(f"Attached to launched app: {app.name}")
                    return app
        
        return None
