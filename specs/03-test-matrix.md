# CodeCraftAI UIA Test Matrix

## Test Framework
- `testbase` is the required framework.
- Only singlehost tests should be run by automation.

## Test Roots
- Root: `/Users/myron/repos/codecraftai-uia/source/testroots/ccai`
- Singlehost package: `ccai.tests.singlehost`

## Test Command
```sh
source .venv/bin/activate
testbase testing run --root source/testroots/ccai --includes=ccai.tests.singlehost --output=./.output
```

## Output Artifacts
- JSOS stream: `./.output/testrun_results_stream.jsos`
- Every test emits a preview and final result entry.

## Matrix (Initial)
| Dimension | Current Coverage | Notes |
| --- | --- | --- |
| Platform | MacOS | Windows and Linux are not implemented. |
| Engine | `MacOSAutomation` | Factory returns MacOS on Darwin only. |
| Apps | Well-known MacOS apps | Coverage should follow `MacCatalog`. |
| Metadata | `UiaMetadataQuery` | Validate timeouts and lookup behavior. |
| Windows | `MacApplication.windows()` | Validate window list access and basic properties. |

## Planned Additions
- Factory and catalog unit tests under `source/testroots/ccai/tests/singlehost/uia/`.
- Integration tests that launch a safe system app (Calculator or TextEdit) and validate window enumeration.
