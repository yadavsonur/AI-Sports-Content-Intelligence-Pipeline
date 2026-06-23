class KeyPool:

    def __init__(self, keys):

        if not keys:
            raise ValueError(
                "At least one key required"
            )

        self.keys = keys

        self.current = 0

    def get_key(self):

        return self.keys[
            self.current
        ]

    def has_next(self):

        return (
            self.current
            <
            len(self.keys) - 1
        )

    def next_key(self):

        if self.has_next():

            self.current += 1

        return self.get_key()

    def reset(self):

        self.current = 0