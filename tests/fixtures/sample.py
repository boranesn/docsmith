"""A sample Python module used as a test fixture."""


def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"


def _internal_helper(x: int) -> int:
    return x + 1


class Greeter:
    """A greeter class that can greet multiple people."""

    def __init__(self, prefix: str = "Hello") -> None:
        self.prefix = prefix

    def greet(self, name: str) -> str:
        """Greet a person with the configured prefix."""
        return f"{self.prefix}, {name}!"

    def _build_message(self, name: str) -> str:
        return f"{self.prefix}, {name}!"
