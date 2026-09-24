#!/usr/bin/env python3
"""
    .. module:: check_macos_ax_constants
        :synopsis: Diagnoses the HIServices accessibility constants that ccai.uia's macOS wrapper imports.

    ``ccai/uia/platforms/macos/wrappers/uiaaccessibility.py`` imports four names from HIServices in one
    statement::

        from HIServices import kAXVisibleAttribute, kAXWindowsAttribute, kAXValueCGPointType, kAXValueCGSizeType

    If any one of them is missing, the whole import fails and all four fall back to hard-coded values
    ("AXVisible", "AXWindows", 1, 2).  This script shows which names pyobjc really exports, whether the uia
    module is running on the fallbacks, whether the fallbacks match the real values, and (live, against
    Finder) whether window lookup and position/size decoding work with the values the module uses.

    Run it on a Mac from the codecraftai-uia repository::

        source .venv/bin/activate
        python source/examples/check_macos_ax_constants.py

    Only pyobjc is required.  The ccai.uia checks are skipped if the package is not importable.  The live
    check needs Accessibility permission for the terminal app (System Settings > Privacy & Security >
    Accessibility) and at least one open Finder window; without them that section is skipped.
"""

import importlib
import platform
import sys

from typing import Any, Dict, List, Optional, Tuple

# The names the uia module imports together, with the fallback value it uses when the import fails.
CONSTANTS: List[Tuple[str, Any]] = [
    ("kAXVisibleAttribute", "AXVisible"),
    ("kAXWindowsAttribute", "AXWindows"),
    ("kAXValueCGPointType", 1),
    ("kAXValueCGSizeType", 2),
]

# Names newer SDKs use for the same values; reported for information only.
ALTERNATE_NAMES = ["kAXValueTypeCGPoint", "kAXValueTypeCGSize", "kAXHiddenAttribute"]

UIA_MODULE = "ccai.uia.platforms.macos.wrappers.uiaaccessibility"

MISSING = object()


def section(title: str) -> None:
    print("")
    print("== " + title)
    return


def check_environment() -> bool:
    """
        Prints the platform and pyobjc versions.

        :returns: True when running on macOS with pyobjc available.
    """
    section("Environment")
    system = platform.system()
    print("platform:  %s %s" % (system, platform.mac_ver()[0]))
    print("python:    %s" % sys.version.split()[0])

    ok = True
    if system != "Darwin":
        print("This script must run on macOS.")
        ok = False
    else:
        try:
            objc = importlib.import_module("objc")
            print("pyobjc:    %s" % getattr(objc, "__version__", "unknown"))
        except ImportError:
            print("pyobjc is not installed (pip install pyobjc-framework-ApplicationServices).")
            ok = False
    return ok


def check_exports() -> Dict[str, Dict[str, Any]]:
    """
        Checks which of the four names HIServices and ApplicationServices export.

        :returns: module name -> {constant name -> value, or MISSING}.
    """
    section("Names exported by pyobjc")
    exports: Dict[str, Dict[str, Any]] = {}
    for module_name in ("HIServices", "ApplicationServices"):
        values: Dict[str, Any] = {}
        try:
            module = importlib.import_module(module_name)
        except ImportError as xcpt:
            print("%-20s cannot be imported: %s" % (module_name, xcpt))
            exports[module_name] = values
            continue
        for name in [name for name, _fallback in CONSTANTS] + ALTERNATE_NAMES:
            values[name] = getattr(module, name, MISSING)
            shown = "MISSING" if values[name] is MISSING else repr(values[name])
            print("%-20s %-22s %s" % (module_name, name, shown))
        exports[module_name] = values
    return exports


def check_grouped_import() -> bool:
    """
        Repeats the uia module's grouped import exactly.

        :returns: True when the grouped import succeeds (no fallbacks needed).
    """
    section("The uia module's grouped HIServices import")
    names = ", ".join(name for name, _fallback in CONSTANTS)
    succeeded = False
    try:
        exec("from HIServices import (%s)" % names, {})
        succeeded = True
        print("succeeds: the module uses the real HIServices values")
    except ImportError as xcpt:
        print("FAILS: %s" % xcpt)
        print("the module falls back to hard-coded values for all four names")
    return succeeded


def real_value(exports: Dict[str, Dict[str, Any]], name: str) -> Any:
    """
        Returns the value pyobjc defines for a name, from HIServices first, then ApplicationServices.
    """
    value = exports.get("HIServices", {}).get(name, MISSING)
    if value is MISSING:
        value = exports.get("ApplicationServices", {}).get(name, MISSING)
    return value


def check_uia_module(exports: Dict[str, Dict[str, Any]], grouped_ok: bool) -> Tuple[Optional[Any], List[str]]:
    """
        Compares the values the uia module ended up with against the real pyobjc values.

        :param exports: The names pyobjc exports, from check_exports().
        :param grouped_ok: Whether the grouped HIServices import succeeds, which decides whether the module holds
                           the real values or its fallbacks.

        :returns: The imported uia module (or None) and a list of mismatch descriptions.
    """
    section("Values in " + UIA_MODULE)
    problems: List[str] = []
    try:
        module = importlib.import_module(UIA_MODULE)
    except ImportError as xcpt:
        print("skipped: ccai.uia is not importable here (%s)" % xcpt)
        return None, problems

    source = "HIServices" if grouped_ok else "fallback"
    for name, _fallback in CONSTANTS:
        used = getattr(module, name, MISSING)
        real = real_value(exports, name)
        if real is MISSING:
            verdict = "no real value exists in pyobjc; the module uses %r" % (used,)
        elif used == real:
            verdict = "matches the real value"
        else:
            verdict = "MISMATCH: real value is %r" % (real,)
            problems.append("%s: the module uses %r but pyobjc defines %r" % (name, used, real))
        print("%-22s %-10s %-12r %s" % (name, source, used, verdict))
    return module, problems


def finder_pid() -> Optional[int]:
    """
        Returns the process id of the running Finder, or None.
    """
    pid = None
    try:
        appkit = importlib.import_module("AppKit")
    except ImportError:
        return pid
    for app in appkit.NSWorkspace.sharedWorkspace().runningApplications():
        if app.bundleIdentifier() == "com.apple.finder":
            pid = int(app.processIdentifier())
            break
    return pid


def check_live(uia_module: Optional[Any], exports: Dict[str, Dict[str, Any]]) -> List[str]:
    """
        Uses the values the uia module relies on against Finder: window lookup, position/size decoding, and
        whether 'AXVisible' is an attribute windows actually have.

        :returns: A list of problem descriptions.
    """
    section("Live check against Finder")
    problems: List[str] = []
    try:
        services = importlib.import_module("ApplicationServices")
    except ImportError as xcpt:
        print("skipped: ApplicationServices is not importable (%s)" % xcpt)
        return problems

    if not services.AXIsProcessTrusted():
        print("skipped: this terminal does not have Accessibility permission.")
        print("grant it in System Settings > Privacy & Security > Accessibility, then run again.")
        return problems

    pid = finder_pid()
    if pid is None:
        print("skipped: Finder is not running")
        return problems

    def used(name: str, fallback: Any) -> Any:
        value = getattr(uia_module, name, MISSING) if uia_module is not None else MISSING
        if value is MISSING:
            value = real_value(exports, name)
        if value is MISSING:
            value = fallback
        return value

    windows_attr = used("kAXWindowsAttribute", "AXWindows")
    point_type = used("kAXValueCGPointType", 1)
    size_type = used("kAXValueCGSizeType", 2)
    visible_attr = used("kAXVisibleAttribute", "AXVisible")

    app = services.AXUIElementCreateApplication(pid)
    error, windows = services.AXUIElementCopyAttributeValue(app, windows_attr, None)
    if error != 0:
        problems.append("reading %r from Finder failed with AXError %d" % (windows_attr, error))
        print("reading %r failed: AXError %d" % (windows_attr, error))
        return problems
    windows = list(windows or [])
    print("%r returned %d Finder window(s)" % (windows_attr, len(windows)))
    if len(windows) == 0:
        print("open a Finder window and run again to check the position, size and attribute names")
        return problems

    window = windows[0]
    error, title = services.AXUIElementCopyAttributeValue(window, "AXTitle", None)
    print("first window: %r" % (title if error == 0 else "<no title>"))

    error, names = services.AXUIElementCopyAttributeNames(window, None)
    names = list(names or []) if error == 0 else []
    has_visible = visible_attr in names
    print("window attributes: %s" % ", ".join(sorted(str(n) for n in names)))
    print("%r is %s attribute of the window" % (visible_attr, "an" if has_visible else "NOT an"))
    if not has_visible:
        error, value = services.AXUIElementCopyAttributeValue(window, visible_attr, None)
        print("reading %r directly: AXError %d" % (visible_attr, error))

    for attribute, value_type, label in (("AXPosition", point_type, "kAXValueCGPointType"),
                                         ("AXSize", size_type, "kAXValueCGSizeType")):
        error, axvalue = services.AXUIElementCopyAttributeValue(window, attribute, None)
        if error != 0:
            problems.append("reading %s failed with AXError %d" % (attribute, error))
            print("%s: AXError %d" % (attribute, error))
            continue
        decoded_ok, decoded = services.AXValueGetValue(axvalue, value_type, None)
        print("%s decoded with %s=%r: ok=%s value=%r" % (attribute, label, value_type, decoded_ok, decoded))
        if not decoded_ok:
            problems.append("%s could not be decoded with %s=%r" % (attribute, label, value_type))
    return problems


def main() -> int:
    if not check_environment():
        return 2

    exports = check_exports()
    grouped_ok = check_grouped_import()
    uia_module, problems = check_uia_module(exports, grouped_ok)
    problems.extend(check_live(uia_module, exports))

    section("Summary")
    visible_real = real_value(exports, "kAXVisibleAttribute")
    if grouped_ok:
        print("- The grouped HIServices import works; no fallbacks are in use.")
    else:
        print("- The grouped HIServices import fails, so all four names use their fallbacks.")
    if visible_real is MISSING:
        print("- pyobjc defines no kAXVisibleAttribute. The uia module imports it but never uses it, so it can be")
        print("  dropped from the grouped import, which lets the other three names load from HIServices.")
    if len(problems) == 0:
        print("- No mismatches: the values the module uses work against a live Finder window.")
    else:
        print("- Problems found:")
        for problem in problems:
            print("    " + problem)
    print("")
    print("Paste this output back into the conversation.")

    exit_code = 0 if len(problems) == 0 else 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
