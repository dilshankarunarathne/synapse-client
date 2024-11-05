class SYNFileNotFoundError(Exception):
    # Constructor
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    # String representation
    def __str__(self):
        return f"SYNFileNotFoundError: {self.message}"
