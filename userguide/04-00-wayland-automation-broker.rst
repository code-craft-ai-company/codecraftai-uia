*************************
Wayland Automation Broker
*************************

The Wayland Automation Broker is a specialized component designed to enable automation capabilities on GNOME Wayland sessions, where traditional X11-based automation tools often fail due to security isolation.

Overview
========

On Wayland, applications are isolated from one another. This prevents standard automation tools from inspecting windows or obtaining screen coordinates of other applications. The Automation Broker bridges this gap by determining window locations and screen geometry through a privileged component (a GNOME Shell extension) and exposing this data via a secure, local-only interface.

Components
----------

The broker consists of two main parts:

1.  **GNOME Shell Extension**: Runs inside the compositor to access window and monitor information.
2.  **Service Manager**: A Python script that manages the extension's lifecycle and security tokens.

Installation
============

The broker is not installed system-wide by default. It must be installed into your user's GNOME Shell extensions directory.

Run the installation command from the repository root:

.. code-block:: bash

    ./source/packages/automojo/uia/support/linux/wayland-gnome/automation-broker/automation-broker-server/broker_service.py install

After installation, you may need to log out and log back in for GNOME Shell to recognize the new extension.

Usage
=====

The broker is designed to be "active" only when needed. You must explicitly start it to enable the automation capabilities.

Starting the Broker
-------------------

To enable the broker:

.. code-block:: bash

    ./source/packages/automojo/uia/support/linux/wayland-gnome/automation-broker/automation-broker-server/broker_service.py start

**What happens:**

1.  A secure, random access token is generated in ``$XDG_RUNTIME_DIR/automation-broker.token``.
2.  The GNOME Shell extension is enabled.
3.  The extension reads the token and opens a Unix domain socket at ``$XDG_RUNTIME_DIR/automation-broker.sock``.

Checking Status
---------------

To see if the broker is currently running and ready:

.. code-block:: bash

    ./source/packages/automojo/uia/support/linux/wayland-gnome/automation-broker/automation-broker-server/broker_service.py status

Stopping the Broker
-------------------

When automation is finished, you should stop the broker to disable the extension and remove the IPC socket:

.. code-block:: bash

    ./source/packages/automojo/uia/support/linux/wayland-gnome/automation-broker/automation-broker-server/broker_service.py stop

Security
========

The broker uses a strictly local security model:

*   **Unix Socket**: Listening only on a user-private socket (permissions ``0600``).
*   **Token Authentication**: Clients must present the contents of the ``automation-broker.token`` file (also protected with ``0600`` permissions) to make requests.
*   **On-Demand**: The capability is completely disabled (socket removed, extension stopped) when the service is stopped.
