.. _03-00-declarative-automation:

**********************
Declarative Automation
**********************

The `codecraftai-uia` framework supports declarative automation, allowing you to define the structure of your application's UI using hints and models. This approach separates the definition of UI elements from the test logic, leading to more maintainable and readable tests with better IDE support.

Hints and Models
================

The core of declarative automation is the ``DeclarativeApplication`` class and various ``ElementHint`` subclasses.

Application Model
-----------------
You define an application by inheriting from ``DeclarativeApplication`` and defining hints as class attributes.

.. code-block:: python

    from ccai.uia.model.declarative import DeclarativeApplication, WindowHint, ButtonHint, TextHint

    class Calculator(DeclarativeApplication):
        APPLICATION_NAME = "gnome-calculator"
        
        MainWindow = WindowHint(name="Calculator")
        Display = TextHint(role="text")
        
        Button1 = ButtonHint(name="1")
        ButtonAdd = ButtonHint(name="+")
        ButtonEquals = ButtonHint(name="=")

Element Hints
-------------
Hints describe how to locate a UI element. They are generic classes, meaning they provide type information to your IDE.

*   ``ElementHint[T]``: Base hint class.
*   ``WindowHint``: Locates a ``UIWindow``. Default role: "window".
*   ``DialogHint``: Locates a ``UIDialog``. Default role: "dialog".
*   ``ButtonHint``: Locates a ``UIButton``. Default role: "push button".
*   ``TextHint``: Locates a ``UIText``. Default role: "text".
*   ``MenuBarHint``: Locates a ``UIMenuBar``. Default role: "menu bar".
*   ``MenuHint``: Locates a ``UIMenu``. Default role: "menu".
*   ``MenuItemHint``: Locates a ``UIMenuItem``. Default role: "menu item".

Usage in Tests
--------------
You can use the model to launch or attach to the application and resolve elements.

.. code-block:: python

    # Launch or Attach
    app = Calculator.attach(automation)
    
    # Resolve Main Window
    window = Calculator.MainWindow.resolve(app)
    
    # Resolve Elements (relative to parent)
    display = Calculator.Display.resolve(window)
    btn_1 = Calculator.Button1.resolve(window)
    
    # Interact
    btn_1.click()
    print(display.text)

XPath-Style Search
==================

Hints support an advanced XPath-style syntax for locating elements using the ``path`` argument. This is useful for complex hierarchies or when simple name/role matching is insufficient.

Syntax
------

*   ``//``: Recursive descendant search (find anywhere in subtree).
*   ``/``: Direct child search.
*   ``.``: Relative to current context.
*   ``{key:value}``: Filter by property (e.g., name, role).
*   ``*``: Wildcard node (matches any element).

Property Values
---------------

*   ``*``: Wildcard value (matches any value). Example: ``{name:Calc*}`` matches "Calculator", "Calc".
*   ``~``: Contains operator. Example: ``{name:~Untitled}`` matches "Untitled 1", "My Untitled Doc".

Examples
--------

**Find a descendant button named "OK":**

.. code-block:: python

    OKButton = ButtonHint(path="//{name:OK, role:push button}")

**Find a direct child panel:**

.. code-block:: python

    Panel = ElementHint(path="./{role:panel}")

**Find a grandchild item:**

.. code-block:: python

    Item = ElementHint(path="/*/{role:menu item}")

**Complex Chain:**
Find a window containing "Calc" in the title, then a panel, then a button with "Save" in the name.

.. code-block:: python

    SaveBtn = ButtonHint(path="//{name:~Calc, role:window}/{role:panel}/{name:~Save}")

Best Practices
==============

*   **Prefer Type-Specific Hints**: Use ``ButtonHint`` instead of ``ElementHint`` for better IDE autocompletion.
*   **Use Docstrings**: Add docstrings to your hints in the model class. They will appear in IDE popups.
*   **Keep Models Clean**: Group related elements (like dialogs) into their own Hint classes or sub-models.
