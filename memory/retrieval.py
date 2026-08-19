import re


def retrieve(memories, message, limit=3):

    if not memories or not message:
        return []

    words = _words(message)

    if not words:
        return []

    scored = []

    for memory in memories:
        content = memory[1]
        overlap = len(words & _words(content))

        if overlap > 0:
            scored.append((overlap, memory))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [memory for _, memory in scored[:limit]]


def _words(text):
    return set(
        re.findall(
            r"[a-zA-Z\u0B80-\u0BFF]{3,}",
            text.lower()
        )
    )