import platform

from ccai.errors.exceptions import UnSupportedPlatformError


if platform.system() != "Linux":
    raise UnSupportedPlatformError("The Linux test suite is only supported on Linux hosts.")
