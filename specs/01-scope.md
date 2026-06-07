# CodeCraftAI UIA Scope

## Goals
Provide a MacOS-first UI automation layer with a stable base interface for applications, windows, and elements. Offer a simple factory that selects the correct platform engine and a catalog that maps known MacOS bundle identifiers to specialized wrappers.

## In Scope
- MacOS UI automation via AppKit and ScriptingBridge.
- **Linux UI automation via AT-SPI and X11.** ✅
- Application discovery and launch through `NSWorkspace` (MacOS) or AT-SPI Registry (Linux).
- Application metadata lookup via `NSMetadataQuery` (MacOS).
- Wrapper classes that expose properties and behaviors of applications and windows (**MacApplication**, **MacWindow**, etc.).
- **Enhanced base class hierarchy with DisplayElement, ScreenElement, and UI component types (UIButton, UIText, UITable, UIMenu, etc.).** ✅
- **Base element utilities: `exists`, `wait_for_element`, and `wait_until_gone`.** ✅
- Well-known application catalog for common MacOS apps (**MacCatalog**).
- A single controller instance for convenience and reuse.

## Out Of Scope (Initial)
- Windows automation implementation.
- Full cross-platform API parity (Linux implements core interfaces but with platform-specific constraints).
- Performance optimization beyond reasonable responsiveness.
- End-user CLI tooling or standalone UI test runner.

## Supported Platforms
- **MacOS (Darwin)** - Full implementation via AppKit/ScriptingBridge
- **Linux** - Implementation via AT-SPI and X11 ✅
  - Known constraints: X11 window finding issues with some applications (e.g., LibreOffice)
- **Windows** - Not implemented

## Dependencies And Environment Assumptions
- PyObjC frameworks for AppKit and ScriptingBridge.
- Accessibility and automation permissions are expected to be granted by the user for UI automation to function.

## Non-Goals
- Full UI testing framework (this is a package intended to be used by other test frameworks).
- Comprehensive UI element tree traversal in the first iteration.

## Stability Expectations
- The base interfaces define the contract. MacOS implementations should conform to them before expanding feature breadth.
