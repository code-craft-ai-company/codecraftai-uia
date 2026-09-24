"""
    Display-free tests for the state queries of the Linux control wrappers:
    :attr:`LinuxTabItem.is_selected`, :attr:`LinuxTab.selected_tab`,
    :attr:`LinuxComboBox.selected_item`, :attr:`LinuxComboBox.is_expanded`,
    :attr:`LinuxCheckBox.is_checked`, :attr:`LinuxRadioButton.is_selected` and
    :attr:`LinuxTreeItem.is_expanded` / :attr:`LinuxTreeItem.is_selected`.  The
    trees are fake AT-SPI nodes read through :class:`FakeAccessibilityAgent`;
    nodes carry their states the way pyatspi reports them (``STATE_CHECKED``,
    ``STATE_EXPANDED``, ``STATE_SELECTED``).
"""

from ccai import testbase

from ccai.uia.platforms.linux.wrappers.controls import (
    LinuxCheckBox,
    LinuxComboBox,
    LinuxRadioButton,
    LinuxTab,
    LinuxTabItem,
    LinuxTreeItem,
)

from ccai.testshared.fakes.uia.fakeelements import FakeAccessibilityAgent, FakeNativeNode


# The string form of the pyatspi ``StateType`` values the accessibility agent returns.
UNSELECTED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_SELECTABLE"]
SELECTED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_SELECTABLE", "STATE_SELECTED"]
UNCHECKED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_CHECKABLE"]
CHECKED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_CHECKABLE", "STATE_CHECKED"]
COLLAPSED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_EXPANDABLE", "STATE_COLLAPSED"]
EXPANDED_STATES = ["STATE_VISIBLE", "STATE_ENABLED", "STATE_EXPANDABLE", "STATE_EXPANDED"]


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


def test_check_box_is_checked_recognizes_the_pyatspi_state():
    """
        ``is_checked`` is true for ``STATE_CHECKED`` and false when only
        ``STATE_CHECKABLE`` is present.
    """
    access = FakeAccessibilityAgent()
    checked = LinuxCheckBox(FakeNativeNode("Bold", "check box", states=list(CHECKED_STATES)), access, None)
    unchecked = LinuxCheckBox(FakeNativeNode("Italic", "check box", states=list(UNCHECKED_STATES)), access, None)
    plain = LinuxCheckBox(FakeNativeNode("Underline", "check box", states=["visible", "checked"]), access, None)

    testbase.assert_true(checked.is_checked, "STATE_CHECKED reads as checked")
    testbase.assert_false(unchecked.is_checked, "STATE_CHECKABLE alone does not read as checked")
    testbase.assert_true(plain.is_checked, "the plain 'checked' name reads as checked")

    return


def test_check_box_check_and_uncheck_only_toggle_when_needed():
    """
        ``check`` leaves a box that reports ``STATE_CHECKED`` alone and ``uncheck``
        toggles it; the toggle is the element's click action.
    """
    access = FakeAccessibilityAgent()
    node = FakeNativeNode("Bold", "check box", states=list(CHECKED_STATES))
    check_box = LinuxCheckBox(node, access, None)

    check_box.check()
    testbase.assert_equal(len(access.actions), 0)

    check_box.uncheck()
    testbase.assert_equal(access.actions, [(node, 0)])

    return


def test_radio_button_is_selected_recognizes_the_pyatspi_states():
    """
        A radio button reads as selected for ``STATE_CHECKED`` (how toolkits mark
        the chosen radio button) and for ``STATE_SELECTED``, and not for
        ``STATE_CHECKABLE`` or ``STATE_SELECTABLE`` alone.
    """
    access = FakeAccessibilityAgent()
    checked = LinuxRadioButton(FakeNativeNode("Small", "radio button", states=list(CHECKED_STATES)), access, None)
    selected = LinuxRadioButton(FakeNativeNode("Medium", "radio button", states=list(SELECTED_STATES)), access, None)
    unchecked = LinuxRadioButton(FakeNativeNode("Large", "radio button", states=list(UNCHECKED_STATES)), access, None)
    unselected = LinuxRadioButton(FakeNativeNode("Huge", "radio button", states=list(UNSELECTED_STATES)), access, None)

    testbase.assert_true(checked.is_selected, "STATE_CHECKED reads as selected")
    testbase.assert_true(selected.is_selected, "STATE_SELECTED reads as selected")
    testbase.assert_false(unchecked.is_selected, "STATE_CHECKABLE alone does not read as selected")
    testbase.assert_false(unselected.is_selected, "STATE_SELECTABLE alone does not read as selected")

    return


def test_radio_button_select_does_not_click_a_chosen_button():
    """
        ``select`` does not click a radio button that already reports
        ``STATE_CHECKED``, and clicks one that does not.
    """
    access = FakeAccessibilityAgent()
    chosen_node = FakeNativeNode("Small", "radio button", states=list(CHECKED_STATES))
    other_node = FakeNativeNode("Large", "radio button", states=list(UNCHECKED_STATES))

    LinuxRadioButton(chosen_node, access, None).select()
    testbase.assert_equal(len(access.actions), 0)

    LinuxRadioButton(other_node, access, None).select()
    testbase.assert_equal(access.actions, [(other_node, 0)])

    return


def test_combo_box_is_expanded_recognizes_the_pyatspi_state():
    """
        ``is_expanded`` is true for ``STATE_EXPANDED`` and false when only
        ``STATE_EXPANDABLE`` is present; ``collapse`` clicks only an expanded box.
    """
    access = FakeAccessibilityAgent()
    expanded_node = FakeNativeNode("Colour", "combo box", states=list(EXPANDED_STATES))
    collapsed_node = FakeNativeNode("Size", "combo box", states=list(COLLAPSED_STATES))
    expanded = LinuxComboBox(expanded_node, access, None)
    collapsed = LinuxComboBox(collapsed_node, access, None)

    testbase.assert_true(expanded.is_expanded, "STATE_EXPANDED reads as expanded")
    testbase.assert_false(collapsed.is_expanded, "STATE_EXPANDABLE alone does not read as expanded")

    collapsed.collapse()
    testbase.assert_equal(len(access.actions), 0)

    expanded.collapse()
    testbase.assert_equal(access.actions, [(expanded_node, 0)])

    return


def test_tree_item_is_expanded_recognizes_the_pyatspi_state():
    """
        ``is_expanded`` is true for ``STATE_EXPANDED`` and false when only
        ``STATE_EXPANDABLE`` is present; ``expand`` performs the action only on a
        collapsed item.
    """
    access = FakeAccessibilityAgent()
    expanded_node = FakeNativeNode("Documents", "tree item", states=list(EXPANDED_STATES))
    collapsed_node = FakeNativeNode("Pictures", "tree item", states=list(COLLAPSED_STATES))
    expanded = LinuxTreeItem(expanded_node, access, None)
    collapsed = LinuxTreeItem(collapsed_node, access, None)

    testbase.assert_true(expanded.is_expanded, "STATE_EXPANDED reads as expanded")
    testbase.assert_false(collapsed.is_expanded, "STATE_EXPANDABLE alone does not read as expanded")

    expanded.expand()
    testbase.assert_equal(len(access.actions), 0)

    collapsed.expand()
    testbase.assert_equal(access.actions, [(collapsed_node, 0)])

    return


def test_tree_item_is_selected_recognizes_the_pyatspi_state():
    """
        ``is_selected`` is true for ``STATE_SELECTED`` and false when only
        ``STATE_SELECTABLE`` is present.
    """
    access = FakeAccessibilityAgent()
    selected = LinuxTreeItem(FakeNativeNode("Documents", "tree item", states=list(SELECTED_STATES)), access, None)
    unselected = LinuxTreeItem(FakeNativeNode("Pictures", "tree item", states=list(UNSELECTED_STATES)), access, None)
    plain = LinuxTreeItem(FakeNativeNode("Music", "tree item", states=["visible", "selected"]), access, None)

    testbase.assert_true(selected.is_selected, "STATE_SELECTED reads as selected")
    testbase.assert_false(unselected.is_selected, "STATE_SELECTABLE alone does not read as selected")
    testbase.assert_true(plain.is_selected, "the plain 'selected' name reads as selected")

    return
