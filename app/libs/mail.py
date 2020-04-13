import threading
from flask_mail import Mail as _Mail


class Mail(_Mail):
    def async_send(self, message, app):
        thread = threading.Thread(target=self.__async_send, kwargs={'message': message, 'app': app})
        thread.start()

    def __async_send(self, message, app):
        with app.app_context():
            self.send(message)
