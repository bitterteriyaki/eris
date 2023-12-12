"""
Copyright (C) 2023  kyomi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import re
from typing import Callable, Iterable, List, Optional, Tuple, TypeVar

T = TypeVar("T")


def finder(
    text: str,
    collection: Iterable[T],
    *,
    key: Optional[Callable[[T], str]] = None,
    raw: bool = False,
) -> List[Tuple[int, int, T]] | List[T]:
    """Fuzzy matching algorithm. Returns a list of tuples of the form
    (score, index, object), sorted by score. If raw is ``True``, only
    returns the objects.

    Parameters
    ----------
    text: :class:`str`
        The text to search for.
    collection: :class:`Iterable[T]`
        The collection to search in.
    key: Optional[:class:`Callable[[T], str]]`
        A function that returns a string to match against ``text``.
        Defaults to ``str``.
    raw: :class:`bool`
        Whether to return only the objects or the tuples.

    Returns
    -------
    List[Tuple[int, int, T]] | List[T]
        A list of tuples of the form (score, index, object), sorted by
        score. If raw is ``True``, only returns the objects.
    """

    suggestions: List[Tuple[int, int, T]] = []
    text = str(text)

    pat = ".*?".join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)

    for item in collection:
        to_search = key(item) if key else str(item)
        r = regex.search(to_search)

        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup: Tuple[int, int, T]) -> Tuple[int, int, str | T]:
        return (tup[0], tup[1], key(tup[2])) if key else tup

    if raw:
        return sorted(suggestions, key=sort_key)
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]
