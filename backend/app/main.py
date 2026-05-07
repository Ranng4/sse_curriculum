from typing import TypeVar
from dataclasses import dataclass
from optparse import Option


@dataclass
class C():
    A: int
    B: str = "24"


T = TypeVar("T", C, int)


def aaa[T](a: T) -> T:
    return a


def main():
    c = C(1)
    a = aaa(1)
    a = getattr(c, "d", "2")
    a = 12
    a = type(a)
    setattr(c, "A", 23)
    print(a)


if __name__ == "__main__":
    main()
