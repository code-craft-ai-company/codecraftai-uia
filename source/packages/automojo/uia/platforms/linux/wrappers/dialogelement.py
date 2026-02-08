from automojo.uia.platforms.base import UIDialog, UIModalDialog, UISaveDialog, UISaveAsDialog, UIOpenDialog, UIModalDialogFileAlreadyExists
from automojo.uia.platforms.linux.wrappers.uiawindow import LinuxWindow
from automojo.uia.platforms.linux.wrappers.uiaelement import LinuxElement
import time
import os

class LinuxDialog(LinuxWindow, UIDialog):
    """
    Linux implementation of a Dialog.
    """
    pass

class LinuxModalDialog(LinuxDialog, UIModalDialog):
    """
    Linux implementation of a Modal Dialog.
    """
    pass

class LinuxSaveDialog(LinuxModalDialog, UISaveDialog):
    """
    Linux implementation of a Save Dialog.
    """
    
    def set_filename(self, filename: str) -> None:
        """
        Sets the filename in the dialog.
        """
        # Ensure we have absolute path
        abs_path = os.path.abspath(filename)
        
        # Try to find the filename text field
        # In some GTK dialogs, it's a text object or entry
        filename_input = self.find_descendant(role="text", max_depth=5)
        if not filename_input:
            filename_input = self.find_descendant(role="entry", max_depth=5)
            
        if filename_input:
            filename_input.click()
            time.sleep(0.5)
            # Use X11 key typing via the element (which delegates to WM agent)
            filename_input.type_keys(abs_path)
        else:
            # Fallback: type directly into dialog assuming focus is there
            self.type_keys(abs_path)
            
    def save(self) -> None:
        """
        Clicks the Save button.
        """
        # Explicitly find Save button
        save_button = self.find_descendant(name="Save", role="push button")
        if not save_button:
            # Fallback to just "Save" name check
            save_button = self.find_descendant(name="Save")
            
        if save_button:
            save_button.click()
        else:
            # Fallback: press Enter
            self.type_keys("\n")

class LinuxSaveAsDialog(LinuxSaveDialog, UISaveAsDialog):
    """
    Linux implementation of Save As Dialog.
    """
    pass

class LinuxOpenDialog(LinuxModalDialog, UIOpenDialog):
    """
    Linux implementation of Open Dialog.
    """
    def set_filename(self, filename: str) -> None:
        """
        Sets the filename to open.
        """
        # Same implementation as Save for now, as GtkFileChooser is similar
        abs_path = os.path.abspath(filename)
        
        filename_input = self.find_descendant(role="text", max_depth=5)
        if not filename_input:
            filename_input = self.find_descendant(role="entry", max_depth=5)
            
        if filename_input:
            filename_input.click()
            time.sleep(0.5)
            filename_input.type_keys(abs_path)
        else:
            self.type_keys(abs_path)
        
    def open(self) -> None:
        """
        Clicks the Open button.
        """
        open_button = self.find_descendant(name="Open", role="push button")
        if not open_button:
            open_button = self.find_descendant(name="Open")
            
        if open_button:
            open_button.click()
        else:
            self.type_keys("\n")

class LinuxModalDialogFileAlreadyExists(LinuxModalDialog, UIModalDialogFileAlreadyExists):
    """
    Linux implementation of File Exists Confirmation.
    """
    def confirm_overwrite(self) -> None:
        """
        Clicks Yes or Replace to confirm overwrite.
        """
        yes_btn = self.find_descendant(name="Yes")
        if not yes_btn:
             yes_btn = self.find_descendant(name="Replace")
        
        if yes_btn:
            yes_btn.click()
