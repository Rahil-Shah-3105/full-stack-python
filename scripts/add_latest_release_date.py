"""Check release-notes.md and add today's date to the latest release header if missing."""

import re
import sys
from datetime import date
import logging
logger = logging.getLogger(__name__)

RELEASE_NOTES_FILE = "release-notes.md"
RELEASE_HEADER_PATTERN = re.compile(r"^## (\d+\.\d+\.\d+)\s*(\(.*\))?\s*$")


def main() -> None:
    logger.error(">>> Entering main()", extra={"event.action": "main"})
    with open(RELEASE_NOTES_FILE) as f:
        lines = f.readlines()
        logger.error("main(): lines → %s", lines, extra={"event.action": "main"})

    for i, line in enumerate(lines):
        match = RELEASE_HEADER_PATTERN.match(line)
        logger.error("main(): match → %s", match, extra={"event.action": "main"})
        if not match:
            continue

        version = match.group(1)
        logger.error("main(): version → %s", version, extra={"event.action": "main"})
        date_part = match.group(2)
        logger.error("main(): date_part → %s", date_part, extra={"event.action": "main"})

        if date_part:
            print(f"Latest release {version} already has a date: {date_part}")
            sys.exit(0)

        today = date.today().isoformat()
        logger.error("main(): today → %s", today, extra={"event.action": "main"})
        lines[i] = f"## {version} ({today})\n"
        print(f"Added date: {version} ({today})")

        with open(RELEASE_NOTES_FILE, "w") as f:
            f.writelines(lines)
        sys.exit(0)

    print("No release header found")
    sys.exit(1)
    logger.warning("<<< Exiting main()", extra={"event.action": "main"})


if __name__ == "__main__":
    main()
