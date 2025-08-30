from collections.abc import Sequence


def first[T](sequence: Sequence[T] | None) -> T | None:
    return sequence[0] if sequence else None
