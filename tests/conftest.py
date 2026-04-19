from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    code = '''"""Sample module for testing."""


def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b


def _private_helper(x: int) -> int:
    return x * 2


class Calculator:
    """A simple calculator class."""

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b
'''
    f = tmp_path / "sample.py"
    f.write_text(code)
    return f


@pytest.fixture
def sample_ts_file(tmp_path: Path) -> Path:
    code = """/**
 * Sample TypeScript file for testing.
 */

export interface User {
  id: number;
  name: string;
  email: string;
}

export function greet(user: User): string {
  return `Hello, ${user.name}!`;
}

export class UserService {
  private users: User[] = [];

  addUser(user: User): void {
    this.users.push(user);
  }

  getUser(id: number): User | undefined {
    return this.users.find((u) => u.id === id);
  }
}
"""
    f = tmp_path / "sample.ts"
    f.write_text(code)
    return f
