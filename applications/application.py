from main_application import MainApplication


def create_app() -> None:
    with MainApplication() as app:
        app.show()
        app.exec()


if __name__ == '__main__':
    create_app()
