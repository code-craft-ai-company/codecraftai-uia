# Automojo UIA Test Matrix

## Test Framework
- `testbase` is the required framework.
- Only singlehost tests should be run by automation.

## Test Roots
- Root: `/Users/myron/repos/automojo-uia/source/testroots/automojo`
- Singlehost package: `automojo.tests.singlehost`

## Test Command
```sh
source .venv/bin/activate
testbase testing run --root source/testroots/automojo --includes=automojo.tests.singlehost --output=./.output
```

## Output Artifacts
- JSOS stream: `./.output/testrun_results_stream.jsos`
- Every test emits a preview and final result entry.

## Matrix (Initial)
| Dimension | Current Coverage | Notes |
| --- | --- | --- |
| Platform | MacOS | Windows and Linux are not implemented. |
| Engine | `MacOSAutomation` | Factory returns MacOS on Darwin only. |
| Apps | Well-known MacOS apps | Coverage should follow `UiaCatalog`. |
| Metadata | `UiaMetadataQuery` | Validate timeouts and lookup behavior. |
| Windows | `UiaApplication.windows()` | Validate window list access and basic properties. |

## Planned Additions
- Factory and catalog unit tests under `source/testroots/automojo/tests/singlehost/uia/`.
- Integration tests that launch a safe system app (Calculator or TextEdit) and validate window enumeration.
