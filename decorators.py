def close_browser(func):
    def wrapper(self, *args, **kwargs):
        return_value = func(self, *args, **kwargs)
        self.browser.close()
        return return_value
    return wrapper
