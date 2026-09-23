"""
    Display-free tests for the selection queries of the Linux control wrappers:
    :attr:`LinuxTabItem.is_selected`, :attr:`LinuxTab.selected_tab` and
    :attr:`LinuxComboBox.selected_item`.  The trees are fake AT-SPI nodes read
    through :class:`FakeAccessibilityAgent`; selected nodes carry the state the
    way pyatspi reports it (``STATE_SELECTED``).
"""

from ccai import testbase

from ccai.uia.platforms.linux.wrappers.controls import LinuxComboBox, LinuxTab, LinuxTabItem

from ccai.testshared.fakes.uia.fakeelements import FakeAccessibilityAgent, FakeNativeNode


# The string form of the pyatspi ``StateType`` values the accessibility agent returns.
UNSELECTED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_SELECTABLE"]
SELECTED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_SELECTABLE", "STATE_SELECTED"]


def _build_tab_list(selected_index: int) -> FakeNativeNode:
    """
        A page tab list with three page tabs, one of which is selected.

        :param selected_index: The index of the selected tab, or -1 for none.

        :returns: The page tab list node.
    """
    tab_list = FakeNativeNode("", "page tab list")
    for index, tab_name in enumerate(["General", "Advanced", "About"]):
        states = UNSELECTED_STATES
        if index == selected_index:
            states = SELECTED_STATES
        tab_list.add_child(tab_name, "page tab", states=list(states))
    return tab_list


def test_tab_item_is_selected_recognizes_the_pyatspi_state():
    """
        ``is_selected`` is true for the pyatspi ``STATE_SELECTED`` state and false
        when only unrelated states such as ``STATE_SELECTABLE`` are present.
    """
    access = FakeAccessibilityAgent()
    selected = LinuxTabItem(FakeNativeNode("A", "page tab", states=list(SELECTED_STATES)), access, None)
    unselected = LinuxTabItem(FakeNativeNode("B", "page tab", states=list(UNSELECTED_STATES)), access, None)

    testbase.assert_true(selected.is_selected, "STATE_SELECTED reads as selected")
    testbase.assert_false(unselected.is_selected, "STATE_SELECTABLE alone does not read as selected")

    return


def test_tab_item_is_selected_accepts_the_plain_state_name():
    """
        Agents that report plain state names are still recognized.
    """
    access = FakeAccessibilityAgent()
    tab = LinuxTabItem(FakeNativeNode("A", "page tab", states=["visible", "selected"]), access, None)

    testbase.assert_true(tab.is_selected, "'selected' reads as selected")

    return


def test_selected_tab_returns_the_selected_tab_not_the_first():
    """
        ``selected_tab`` returns the tab carrying the selected state rather than the
        first page tab.
    """
    access = FakeAccessibilityAgent()
    tabs = LinuxTab(_build_tab_list(selected_index=1), access, None)

    selected = tabs.selected_tab

    testbase.assert_true(isinstance(selected, LinuxTabItem), "a LinuxTabItem is returned")
    testbase.assert_equal(selected.name, "Advanced")

    return


def test_selected_tab_is_none_when_no_tab_is_selected():
    """
        With no selected page tab, ``selected_tab`` is ``None``.
    """
    access = FakeAccessibilityAgent()
    tabs = LinuxTab(_build_tab_list(selected_index=-1), access, None)

    testbase.assert_true(tabs.selected_tab is None, "no tab selected")

    return


def test_selected_tab_ignores_tabs_of_a_nested_tab_list():
    """
        A selected tab of a tab list nested inside an unselected page does not hide
        the selected tab of the list itself.
    """
    access = FakeAccessibilityAgent()
    tab_list = FakeNativeNode("", "page tab list")
    first = tab_list.add_child("General", "page tab", states=list(UNSELECTED_STATES))
    nested_list = first.add_child("", "page tab list")
    nested_list.add_child("Nested", "page tab", states=list(SELECTED_STATES))
    tab_list.add_child("Advanced", "page tab", states=list(SELECTED_STATES))
    tabs = LinuxTab(tab_list, access, None)

    selected = tabs.selected_tab

    testbase.assert_equal(selected.name, "Advanced")

    return


def test_selected_tab_searches_below_an_intermediate_container():
    """
        When the page tabs are not direct children of the tab list, the subtree is
        searched.
    """
    access = FakeAccessibilityAgent()
    tab_list = FakeNativeNode("", "page tab list")
    filler = tab_list.add_child("", "filler")
    filler.add_child("General", "page tab", states=list(UNSELECTED_STATES))
    filler.add_child("Advanced", "page tab", states=list(SELECTED_STATES))
    tabs = LinuxTab(tab_list, access, None)

    selected = tabs.selected_tab

    testbase.assert_equal(selected.name, "Advanced")

    return


def test_combo_box_selected_item_finds_the_selected_menu_item():
    """
        ``selected_item`` returns the item of the combo box's popup menu that
        carries the selected state.
    """
    access = FakeAccessibilityAgent()
    combo = FakeNativeNode("Green", "combo box")
    menu = combo.add_child("", "menu")
    menu.add_child("Red", "menu item", states=list(UNSELECTED_STATES))
    menu.add_child("Green", "menu item", states=list(SELECTED_STATES))
    menu.add_child("Blue", "menu item", states=list(UNSELECTED_STATES))
    combo_box = LinuxComboBox(combo, access, None)

    selected = combo_box.selected_item

    testbase.assert_true(selected is not None, "an item is selected")
    testbase.assert_equal(selected.name, "Green")

    return


def test_combo_box_selected_item_finds_the_selected_list_item():
    """
        Toolkits that expose the combo box items as a list are handled too.
    """
    access = FakeAccessibilityAgent()
    combo = FakeNativeNode("Blue", "combo box")
    item_list = combo.add_child("", "list")
    item_list.add_child("Red", "list item", states=list(UNSELECTED_STATES))
    item_list.add_child("Blue", "list item", states=list(SELECTED_STATES))
    combo_box = LinuxComboBox(combo, access, None)

    selected = combo_box.selected_item

    testbase.assert_true(selected is not None, "an item is selected")
    testbase.assert_equal(selected.name, "Blue")

    return


def test_combo_box_selected_item_is_none_when_nothing_is_selected():
    """
        With no selected item, ``selected_item`` is ``None`` instead of raising.
    """
    access = FakeAccessibilityAgent()
    combo = FakeNativeNode("", "combo box")
    menu = combo.add_child("", "menu", states=list(SELECTED_STATES))
    menu.add_child("Red", "menu item", states=list(UNSELECTED_STATES))
    combo_box = LinuxComboBox(combo, access, None)

    testbase.assert_true(combo_box.selected_item is None, "no item selected")

    return
