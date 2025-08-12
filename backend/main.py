from __future__ import annotations

from typing import List

from common import INDEX
from services import upsert_from_url


def seed_once(urls: List[str]) -> None:
    for i, url in enumerate(urls):
        upsert_from_url(
            INDEX,
            url,
            snippet="",
            extra_metadata={"source": "manual", "position": i},
        )


if __name__ == "__main__":
    SEED_URLS = [
        "https://www.fidelitycharitable.org/",
        "https://www.nptrust.org/",
        "https://www.schwabcharitable.org/",
        "https://www.dafgiving360.org/",
    ]
    seed_once(SEED_URLS)
