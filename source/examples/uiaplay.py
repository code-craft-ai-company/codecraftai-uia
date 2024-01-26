

from mojo.uia.uiacontroller import UiaController


def uiaplay_main():
    controller = UiaController()

    controller.get_application("Finder")
    
    return

if __name__ == "__main__":
    uiaplay_main()