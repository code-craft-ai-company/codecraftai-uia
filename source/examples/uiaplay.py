

from automojo.uia.factory import AutomationFactory


def uiaplay_main():
    controller = AutomationFactory.get_automation_engine()

    app = controller.get_application_by_name("Calculator")
    windows = app.windows()
    for win in windows:
        win.groups()
    
    return

if __name__ == "__main__":
    uiaplay_main()