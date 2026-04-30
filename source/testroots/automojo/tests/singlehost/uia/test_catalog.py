import platform

from automojo import testbase


def test_catalog_bundle_mapping():
    """
        Verifies the catalog resolves known and unknown bundle identifiers.
    """
    system = platform.system()
    if system != "Darwin":
        return

    from automojo.uia.platforms.macos.applications.appcalculator import AppCalculator
    from automojo.uia.platforms.macos.uiacatalog import MacCatalog
    from automojo.uia.platforms.macos.wrappers.uiaapplication import MacApplication

    catalog = MacCatalog()

    app_type = catalog.lookup_application_type_by_bundle_id(AppCalculator.BUNDLE_IDENTIFIER)
    testbase.assert_equal(app_type is AppCalculator, True)

    unknown_type = catalog.lookup_application_type_by_bundle_id("com.example.unknown")
    testbase.assert_equal(unknown_type is MacApplication, True)

    return
