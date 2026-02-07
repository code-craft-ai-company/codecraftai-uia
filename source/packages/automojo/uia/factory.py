
import platform
import sys
from typing import Any

from automojo.uia.platforms.base import AutomationEngine

class AutomationFactory:
    """
        Factory class for creating automation engines based on the current platform.
    """

    @staticmethod
    def get_automation_engine() -> AutomationEngine:
        """
            Returns the automation engine for the current platform.

            :returns: An instance of the platform-specific automation engine.
        """
        system = platform.system()

        if system == "Darwin":
            from automojo.uia.platforms.macos.automation import MacOSAutomation
            return MacOSAutomation()
        elif system == "Windows":
             # Placeholder for Windows support
             raise NotImplementedError("Windows automation is not yet implemented.")
        elif system == "Linux":
             from automojo.uia.platforms.linux.automation import LinuxAutomation
             return LinuxAutomation()
        else:
            raise NotImplementedError(f"Unsupported platform: {system}")
