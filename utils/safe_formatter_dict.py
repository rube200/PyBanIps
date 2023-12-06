class SafeFormatterDict(dict):
    def __missing__(self, key):
        return f'{{{key}}}'
