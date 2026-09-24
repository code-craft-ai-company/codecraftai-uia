"""
    The test-count floor for the merge gate.

    A discovery regression (a wrong ``--includes`` prefix, an import error in a
    test module, a directory whose ``__platforms__.py`` starts refusing the
    host) makes the gate quietly run fewer tests while still reporting green.
    testbase only fails the run when the whole set is empty.  This test counts
    what the gate collects and fails when the count drops below the floor
    reached in the coverage roadmap, so shrinkage is loud.
"""

import ast
import os
import platform

from typing import Optional

from ccai import testbase


# The include expression the merge gate passes to ``testbase testing run``.
GATE_INCLUDE_EXPRESSION = "ccai.tests.singlehost"

# Tests collected on every operating system.  Raise this when tests are added;
# never lower it without a reason recorded in the commit.
FLOOR_ALL_PLATFORMS = 109

# Tests under ``ccai/tests/singlehost/uia/linux``, whose ``__platforms__.py``
# excludes the directory on any host that is not Linux.
FLOOR_LINUX_DESKTOP = 10


def _find_test_root(start: str) -> str:
    """
        Walks up from ``start`` to the directory holding ``__testroot__.py``,
        which is what the gate passes as ``--root``.

        :param start: A path inside the test tree.

        :returns: The absolute test root directory.
        :raises: FileNotFoundError when no test root marker is found.
    """
    current = os.path.abspath(start)
    while True:
        marker = os.path.join(current, "__testroot__.py")
        if os.path.exists(marker):
            break
        parent = os.path.dirname(current)
        if parent == current:
            raise FileNotFoundError("No __testroot__.py above {}".format(start))
        current = parent
    return current


def _count_like_the_runner(root: str, include_expression: str) -> Optional[int]:
    """
        Counts test functions with the same three steps the testbase runner uses
        for ``--root`` and ``--includes``: parse the include expression into a
        package and module filter, walk the root for the module files that
        filter selects (honouring ``__platforms__.py`` exclusions), then import
        each module and keep the module-level functions named ``test*``.

        :param root: The test root directory.
        :param include_expression: The gate's include expression.

        :returns: The number of tests, or ``None`` when the runner internals
                  are not importable so the caller can fall back.
    """
    try:
        from ccai.testbase.expressions import parse_test_include_expression
        from ccai.testbase.queries import collect_test_references
        from ccai.testbase.utilities import find_included_modules_under_root
    except ImportError:
        return None

    expr_package, expr_module, _expr_testclass, expr_testname = parse_test_include_expression(
        include_expression, None, "test")

    included_files, _excluded_files = find_included_modules_under_root(root, expr_package, expr_module)

    references, _import_errors = collect_test_references(
        root, included_files, expr_package, expr_module, expr_testname, "test")

    rtnval = len(references)
    return rtnval


def _count_by_source_scan(root: str, include_expression: str) -> int:
    """
        Fallback count: parses every ``.py`` file under the directory the include
        expression names and counts module-level ``def test*`` statements.  This
        does not import anything, so it also cannot see import errors; it is
        only used when the runner internals are unavailable.

        :param root: The test root directory.
        :param include_expression: The gate's include expression.

        :returns: The number of test functions found in source.
    """
    root_package = os.path.basename(root)
    relative_parts = include_expression.split(".")
    if relative_parts[0] == root_package:
        relative_parts = relative_parts[1:]
    search_dir = os.path.join(root, *relative_parts)

    count = 0
    for dirpath, _dirnames, filenames in os.walk(search_dir):
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, filename)
            with open(filepath, "r", encoding="utf-8") as source_file:
                tree = ast.parse(source_file.read(), filename=filepath)
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                    count = count + 1

    return count


def test_gate_collects_at_least_the_floor():
    """
        The number of tests the gate collects is at least the floor for this host.

        The count is produced by the same collection steps ``testbase testing run
        --root <root> --includes ccai.tests.singlehost`` performs (see
        ``_count_like_the_runner``), falling back to a source scan of ``def test*``
        when those internals cannot be imported.  The floor is the count on every
        platform plus, on Linux, the desktop tests that other hosts exclude
        through ``__platforms__.py``.
    """
    root = _find_test_root(os.path.dirname(__file__))

    collected = _count_like_the_runner(root, GATE_INCLUDE_EXPRESSION)
    if collected is None:
        collected = _count_by_source_scan(root, GATE_INCLUDE_EXPRESSION)

    floor = FLOOR_ALL_PLATFORMS
    if platform.system() == "Linux":
        floor = floor + FLOOR_LINUX_DESKTOP

    detail = "collected {} tests under {!r} from {}; floor for {} is {}".format(
        collected, GATE_INCLUDE_EXPRESSION, root, platform.system(), floor)
    testbase.assert_true(collected >= floor, detail)

    return
