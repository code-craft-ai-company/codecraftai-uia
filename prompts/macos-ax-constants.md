This ask is for an agent running on a macOS host.  It cannot be done on Linux or Windows.

# Background
'source/packages/ccai/uia/platforms/macos/wrappers/uiaaccessibility.py' imports four accessibility
constants from HIServices in a single statement:

```
from HIServices import (
    kAXVisibleAttribute,
    kAXWindowsAttribute,
    kAXValueCGPointType,
    kAXValueCGSizeType
)
```

If any one of the four names is missing from pyobjc, the whole import fails and all four fall back to
hard-coded values ("AXVisible", "AXWindows", 1, 2).  The suspicion is that pyobjc does not define
'kAXVisibleAttribute' (there is no such constant in the macOS SDK), so the other three are always running on
their fallbacks.

What is known from the Linux side:

- 'kAXVisibleAttribute' is not used anywhere in the codecraftai-* packages.  'UiaAccessibilityElement.is_visible'
  always returns True and does not read it.
- 'kAXWindowsAttribute' is used to look up an application's windows ('self._copy_attribute(self.ax_app,
  kAXWindowsAttribute)').
- 'kAXValueCGPointType' and 'kAXValueCGSizeType' are used to decode element position and size
  ('AXValueGetValue(position_value, kAXValueCGPointType, None)').

The job is to find out on a real Mac whether the grouped import falls back, whether the values the module
ends up with are correct, and to fix the import if it needs it.

# Prerequisites
- Grant the terminal (or the agent host process) Accessibility permission in System Settings > Privacy &
  Security > Accessibility.  If it is not granted, halt and ask for it to be granted; do not work around it.
- Open at least one Finder window.
- Calculator must be installed (it is by default).  The Excel test skips itself when Excel is not installed.
- Set up the repository as described in 'AGENTS.md': run 'repository-setup/rehome-repository', then
  'development/setup-environment'.  If a dependency is missing, halt and ask for assistance.

# Steps
1. Run the diagnostic script and keep its output:

```
    source .venv/bin/activate

    mkdir -p .output
    python source/examples/check_macos_ax_constants.py | tee .output/check_macos_ax_constants.before.txt
```

   The script reports which of the names pyobjc exports, whether the grouped import fails, the values the uia
   module actually holds, and, against a live Finder window, whether window lookup and position/size decoding
   work and whether 'AXVisible' is an attribute that windows really have.  Exit code 0 means no problems were
   found, 1 means problems were found, 2 means it could not run (not macOS or no pyobjc).

2. Run the macOS single-host tests before changing anything and record the results from
   '.output/macos-before/testrun_results_stream.jsos':

```
    testbase testing run --root source/testroots/ccai --includes=ccai.tests.singlehost.uia.macos --output=./.output/macos-before
```

   If a test is skipped, record the skip reason.  A skip for missing Accessibility permission means the
   prerequisites are not met; fix that and run again.

3. Decide what to do from the diagnostic output:

   - **The grouped import succeeds and no problems are reported.**  The suspicion was wrong.  Make no code
     change and go to the report.
   - **The grouped import fails only because 'kAXVisibleAttribute' is missing, and there are no mismatches.**
     Remove 'kAXVisibleAttribute' from 'uiaaccessibility.py': from the HIServices import, from the
     'except ImportError' fallback block, and from the block that sets the names to None when
     ApplicationServices cannot be imported.  Keep the other three names and their fallbacks.  Do not implement
     'is_visible' as part of this change; it is a separate piece of work.
   - **A value mismatches, or position/size cannot be decoded, or window lookup fails.**  That is a real bug in
     the wrapper.  Fix it following the coding standards in 'userguide/10-00-coding-standards.rst'.  If newer
     pyobjc only exports the renamed constants ('kAXValueTypeCGPoint', 'kAXValueTypeCGSize'), import the new
     names and fall back to the old ones, rather than hard-coding numbers.

4. If you changed code, run the diagnostic and the macOS tests again, and also the full single-host test set to
   make sure nothing else broke:

```
    python source/examples/check_macos_ax_constants.py | tee .output/check_macos_ax_constants.after.txt

    testbase testing run --root source/testroots/ccai --includes=ccai.tests.singlehost.uia.macos --output=./.output/macos-after

    testbase testing run --root source/testroots/ccai --includes=ccai.tests.singlehost --output=./.output/singlehost-after
```

   The after run should report the grouped import succeeding, the module values coming from HIServices, and
   no problems.  Compare the test results with the before run; there must be no new failures or errors.

5. Create a branch named 'fix/macos-ax-constants', commit the change to it, and present the diff.  Do not
   push, do not change the version in 'pyproject.toml' and do not release.  The maintainer releases by bumping
   the version, and the GitHub Action publishes it.

# Report
Reply with:

- The macOS version, Python version and pyobjc version (the first section of the diagnostic output).
- The full diagnostic output from before, and from after if you changed code.
- The window attribute names the live check printed, and whether 'AXVisible' (or 'AXHidden') is among them.
  This decides how 'is_visible' should be implemented later.
- The before and after results of the macOS tests, with any skip reasons.
- Which case in step 3 applied, and the diff if you made a change.
