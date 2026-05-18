# This script is an example for the test.
# It contains various comment styles.

class MyClass:
    """
    This is a class docstring.
    It should be removed.
    """
    def __init__(self, name):
        self.name = name # Inline comment

    def greet(self):
        """Method docstring."""
        # Print a message
        print(f"Hello, {self.name}")

# Top-level function
def top_level_function():
    """Another docstring to remove."""
    return 1 + 1 # Simple calculation
