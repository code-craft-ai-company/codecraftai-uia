

from ccai.uia.factory import AutomationFactory


def uiaplay_main():
    controller = AutomationFactory.get_automation_engine()

    app = controller.get_application_by_name("Calculator")
    app.activate()

    windows = app.get_windows()
    if windows is not None:
        if len(windows) > 0:
            first_window = windows[0]
            try:
                first_window.focus()
            except NotImplementedError:
                first_window.click()
        else:
            pass
    else:
        raise ValueError("Expected a list of windows but received None.")

    app.terminate()
    
    return

if __name__ == "__main__":
    uiaplay_main()
