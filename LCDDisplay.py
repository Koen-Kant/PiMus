import threading
import time
import LCD_Lib


class LCDThread(threading.Thread):
    def __init__(self):
        super(LCDThread, self).__init__()
        self.go = True
        self.top_string_to_write = "---[Booting]---"
        self.lower_string_to_write = "-[Please wait]-"
        LCD_Lib.main_set_up()
        self.start()

    def spool_string_value(self, top_string_to_lcd=None, lower_string_to_lcd=None):
        if top_string_to_lcd:
            self.top_string_to_write = top_string_to_lcd
        if lower_string_to_lcd:
            self.lower_string_to_write = lower_string_to_lcd

    def string_to_lcd(self):
        LCD_Lib.set_on_lcd(self.top_string_to_write, self.lower_string_to_write)

    def run(self):
        while self.go:
            try:
                self.string_to_lcd()
            except UnicodeEncodeError:
                self.top_string_to_write = "---[Odd char]---"
            time.sleep(0.2)

    def stop(self):
        self.go = False
