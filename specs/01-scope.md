# Automojo UIA Scope

## Goals
Provide a MacOS-first UI automation layer with a stable base interface for applications, windows, and elements. Offer a simple factory that selects the correct platform engine and a catalog that maps known MacOS bundle identifiers to specialized wrappers.

## In Scope
- MacOS UI automation via AppKit and ScriptingBridge.
- Application discovery and launch through `NSWorkspace`.
- Application metadata lookup via `NSMetadataQuery`.
- Wrapper classes that expose properties and behaviors of applications and windows.
- Well-known application catalog for common MacOS apps.
- A single controller instance for convenience and reuse.

## Out Of Scope (Initial)
- Windows and Linux automation implementations.
- Cross-platform API parity beyond the abstract base interfaces.
- Performance optimization beyond reasonable responsiveness.
- End-user CLI tooling or standalone UI test runner.

## Supported Platforms
- MacOS only (Darwin). Windows and Linux are explicitly not implemented.

## Dependencies And Environment Assumptions
- PyObjC frameworks for AppKit and ScriptingBridge.
- Accessibility and automation permissions are expected to be granted by the user for UI automation to function.

## Non-Goals
- Full UI testing framework (this is a package intended to be used by other test frameworks).
- Comprehensive UI element tree traversal in the first iteration.

## Stability Expectations
- The base interfaces define the contract. MacOS implementations should conform to them before expanding feature breadth.
