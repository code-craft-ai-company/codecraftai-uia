=======================
Code Craft AI UIA
=======================

The ``codecraftai-uia`` package provides cross-platform (Linux, Windows, macOS) user-interface automation capabilities. The code attempts to consolidate the UI patterns of multiple operating systems into a common object model that scripts can use to automate application user interfaces.

Highlights
==========

- Platform backends under ``uia/platforms/`` for macOS, Linux, and Windows.
- Common object model under ``uia/model/`` for applications, windows, and UI elements.
- Support utilities under ``uia/support/`` including Linux-specific helpers.
- CLI command tree under ``uia/cli/cmdtree/`` for operator-style interaction.
- Designed for consumption by higher-level testing frameworks with a focus on debuggability and clarity.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/`` - Package source code.
- ``source/testroots/ccai/`` - TestBase test roots, factories, and shared fixtures.
- ``source/examples/`` - Example usage scripts.
- ``specs/`` - Scope, API, and design documentation.
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-envrionment

Running Tests
=============

Activate the virtual environment:

.. code-block:: bash

   source .venv/bin/activate

Run the single-host test suite:

.. code-block:: bash

   testbase testing run --root source/testroots/ccai --includes=ccai.tests.singlehost.uia --output=./.output

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
- Scope: ``specs/01-scope.md``
- API: ``specs/02-api.md``
- Test matrix: ``specs/03-test-matrix.md``
