

from mojo.uia.uiacontroller import UiaController


def uiaplay_main():
    controller = UiaController()

    app = controller.get_application_by_name("Calculator")
    windows = app.windows()
    for win in windows:
        win.groups()
    
    return

if __name__ == "__main__":
    uiaplay_main()