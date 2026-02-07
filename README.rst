==================================================
Automaton Mojo - User Interface Automation Package
==================================================
Automation Mojo UIA is a MacOS-first UI automation package that exposes a stable, test-friendly
API for applications, windows, and UI elements. It is designed to be consumed by higher-level
testing frameworks with a focus on debuggability and clarity.

===================
Supported Platforms
===================
* MacOS (Darwin) only
* Windows and Linux are not implemented yet

============
Quick Start
============
Example usage:

.. code-block:: python

    from automojo.uia.factory import AutomationFactory

    controller = AutomationFactory.get_automation_engine()
    app = controller.get_application_by_name("Calculator")
    app.activate()

    windows = app.get_windows()
    if len(windows) > 0:
        windows[0].focus()

    app.terminate()

=======================
Permissions and Access
=======================
MacOS UI automation requires Accessibility permissions. Ensure your automation process has
permission to control the computer. Without this, accessibility operations will fail and the
system will fall back to higher-level scripting APIs where possible.

=================
Code Organization
=================
* development - Runtime environment scripts.
* repository-setup - Scripts to home the repository and prepare the machine.
* userguide - Standards and conventions for the project.
* source/packages - Python packages (source code).
* source/testroots - TestBase test suites and shared resources.
* source/examples - Example scripts and debug helpers.

==========
References
==========
- `User Guide <userguide/userguide.rst>`
- `Coding Standards <userguide/10-00-coding-standards.rst>`
