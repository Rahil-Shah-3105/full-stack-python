"""Prepare a release by updating and extracting release notes."""

import re
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

import typer
import logging
logger = logging.getLogger(__name__)

RELEASE_NOTES_FILE = Path("release-notes.md")
RELEASE_NOTES_HEADER = "# Release Notes\n\n"
LATEST_CHANGES_HEADER = "## Latest Changes"
VERSION_HEADING_PATTERN = re.compile(r"(?m)^## (\d+\.\d+\.\d+)(?: \([^)]+\))?$")
BumpType = Literal["major", "minor", "patch"]

app = typer.Typer()


def parse_version(version: str) -> tuple[int, int, int]:
    logger.error(">>> Entering parse_version(version=%s)", version, extra={"event.action": "parse_version", "logrite.version": version})
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"Invalid version: {version!r}. Expected format: X.Y.Z")
    major, minor, patch = version.split(".")
    logger.warning("<<< Exiting parse_version(version=%s)", version, extra={"event.action": "parse_version", "logrite.version": version})
    return int(major), int(minor), int(patch)


def get_current_version(content: str, release_notes_file: Path) -> str:
    logger.error(">>> Entering get_current_version(content=%s,release_notes_file=%s)", content, release_notes_file, extra={"event.action": "get_current_version", "logrite.content": content, "logrite.release_notes_file": release_notes_file})
    match = VERSION_HEADING_PATTERN.search(content)
    logger.error("get_current_version(content=%s,release_notes_file=%s): match → %s", content, release_notes_file, match, extra={"event.action": "get_current_version", "logrite.content": content, "logrite.release_notes_file": release_notes_file})
    if not match:
        raise RuntimeError(f"Could not find a version section in {release_notes_file}")
    logger.warning("<<< Exiting get_current_version(content=%s,release_notes_file=%s)", content, release_notes_file, extra={"event.action": "get_current_version", "logrite.content": content, "logrite.release_notes_file": release_notes_file})
    return match.group(1)


def bump_version(version: str, bump: BumpType) -> str:
    logger.error(">>> Entering bump_version(version=%s,bump=%s)", version, bump, extra={"event.action": "bump_version", "logrite.version": version, "logrite.bump": bump})
    major, minor, patch = parse_version(version)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    logger.warning("<<< Exiting bump_version(version=%s,bump=%s)", version, bump, extra={"event.action": "bump_version", "logrite.version": version, "logrite.bump": bump})
    return f"{major}.{minor}.{patch + 1}"


def update_release_notes(
    content: str, version: str, release_date: date, release_notes_file: Path
) -> str:
    logger.error(">>> Entering update_release_notes(content=%s,version=%s,release_date=%s,release_notes_file=%s)", content, version, release_date, release_notes_file, extra={"event.action": "update_release_notes", "logrite.content": content, "logrite.version": version, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    latest_header = f"{RELEASE_NOTES_HEADER}{LATEST_CHANGES_HEADER}\n"
    logger.error("update_release_notes(content=%s,version=%s,release_date=%s,release_notes_file=%s): latest_header → %s", content, version, release_date, release_notes_file, latest_header, extra={"event.action": "update_release_notes", "logrite.content": content, "logrite.version": version, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    if not content.startswith(latest_header):
        raise RuntimeError(f"{release_notes_file} must start with {latest_header!r}")
    if re.search(rf"^## {re.escape(version)}(?: \([^)]+\))?$", content, re.M):
        raise RuntimeError(f"Release notes already contain a section for {version}")

    current_version = get_current_version(content, release_notes_file)
    logger.error("update_release_notes(content=%s,version=%s,release_date=%s,release_notes_file=%s): current_version → %s", content, version, release_date, release_notes_file, current_version, extra={"event.action": "update_release_notes", "logrite.content": content, "logrite.version": version, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    if parse_version(version) <= parse_version(current_version):
        raise RuntimeError(
            f"New version {version} must be greater than current version "
            f"{current_version}"
        )

    current_match = VERSION_HEADING_PATTERN.search(content)
    logger.error("update_release_notes(content=%s,version=%s,release_date=%s,release_notes_file=%s): current_match → %s", content, version, release_date, release_notes_file, current_match, extra={"event.action": "update_release_notes", "logrite.content": content, "logrite.version": version, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    assert current_match is not None
    latest_changes = content[len(latest_header) : current_match.start()].strip()
    logger.error("update_release_notes(content=%s,version=%s,release_date=%s,release_notes_file=%s): latest_changes → %s", content, version, release_date, release_notes_file, latest_changes, extra={"event.action": "update_release_notes", "logrite.content": content, "logrite.version": version, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    if not latest_changes:
        raise RuntimeError("The Latest Changes section is empty")

        logger.warning("<<< Exiting update_release_notes(content=%s,version=%s,release_date=%s,release_notes_file=%s)", content, version, release_date, release_notes_file, extra={"event.action": "update_release_notes", "logrite.content": content, "logrite.version": version, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    release_header = f"## {version} ({release_date.isoformat()})"
    logger.error("update_release_notes(content=%s,version=%s,release_date=%s,release_notes_file=%s): release_header → %s", content, version, release_date, release_notes_file, release_header, extra={"event.action": "update_release_notes", "logrite.content": content, "logrite.version": version, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    return content.replace(
        latest_header,
        f"{RELEASE_NOTES_HEADER}{LATEST_CHANGES_HEADER}\n\n{release_header}\n",
        1,
    )


def get_release_notes_body(content: str, version: str, release_notes_file: Path) -> str:
    logger.error(">>> Entering get_release_notes_body(content=%s,version=%s,release_notes_file=%s)", content, version, release_notes_file, extra={"event.action": "get_release_notes_body", "logrite.content": content, "logrite.version": version, "logrite.release_notes_file": release_notes_file})
    version_heading = re.compile(rf"(?m)^## {re.escape(version)}(?: \([^)]+\))?$")
    logger.error("get_release_notes_body(content=%s,version=%s,release_notes_file=%s): version_heading → %s", content, version, release_notes_file, version_heading, extra={"event.action": "get_release_notes_body", "logrite.content": content, "logrite.version": version, "logrite.release_notes_file": release_notes_file})
    match = version_heading.search(content)
    logger.error("get_release_notes_body(content=%s,version=%s,release_notes_file=%s): match → %s", content, version, release_notes_file, match, extra={"event.action": "get_release_notes_body", "logrite.content": content, "logrite.version": version, "logrite.release_notes_file": release_notes_file})
    if not match:
        raise RuntimeError(
            f"Could not find release notes section for {version} in "
            f"{release_notes_file}"
        )

    next_match = VERSION_HEADING_PATTERN.search(content, match.end())
    logger.error("get_release_notes_body(content=%s,version=%s,release_notes_file=%s): next_match → %s", content, version, release_notes_file, next_match, extra={"event.action": "get_release_notes_body", "logrite.content": content, "logrite.version": version, "logrite.release_notes_file": release_notes_file})
    end = next_match.start() if next_match else len(content)
    logger.error("get_release_notes_body(content=%s,version=%s,release_notes_file=%s): end → %s", content, version, release_notes_file, end, extra={"event.action": "get_release_notes_body", "logrite.content": content, "logrite.version": version, "logrite.release_notes_file": release_notes_file})
    body = content[match.end() : end].strip()
    logger.error("get_release_notes_body(content=%s,version=%s,release_notes_file=%s): body → %s", content, version, release_notes_file, body, extra={"event.action": "get_release_notes_body", "logrite.content": content, "logrite.version": version, "logrite.release_notes_file": release_notes_file})
    if not body:
        raise RuntimeError(
            f"Release notes section for {version} in {release_notes_file} is empty"
        )
    logger.warning("<<< Exiting get_release_notes_body(content=%s,version=%s,release_notes_file=%s)", content, version, release_notes_file, extra={"event.action": "get_release_notes_body", "logrite.content": content, "logrite.version": version, "logrite.release_notes_file": release_notes_file})
    return f"{body}\n"


def prepare_release(
    bump: BumpType, release_date: date, release_notes_file: Path
) -> str:
    logger.error(">>> Entering prepare_release(bump=%s,release_date=%s,release_notes_file=%s)", bump, release_date, release_notes_file, extra={"event.action": "prepare_release", "logrite.bump": bump, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    content = release_notes_file.read_text(encoding="utf-8")
    logger.error("prepare_release(bump=%s,release_date=%s,release_notes_file=%s): content → %s", bump, release_date, release_notes_file, content, extra={"event.action": "prepare_release", "logrite.bump": bump, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    version = bump_version(get_current_version(content, release_notes_file), bump)
    logger.error("prepare_release(bump=%s,release_date=%s,release_notes_file=%s): version → %s", bump, release_date, release_notes_file, version, extra={"event.action": "prepare_release", "logrite.bump": bump, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    release_notes_file.write_text(
        update_release_notes(content, version, release_date, release_notes_file),
        encoding="utf-8",
    )
    logger.warning("<<< Exiting prepare_release(bump=%s,release_date=%s,release_notes_file=%s)", bump, release_date, release_notes_file, extra={"event.action": "prepare_release", "logrite.bump": bump, "logrite.release_date": release_date, "logrite.release_notes_file": release_notes_file})
    return version


@app.command()
def prepare(
    bump: Annotated[
        BumpType,
        typer.Argument(help="The release bump to make: major, minor, or patch."),
    ],
    release_notes_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            writable=True,
            help="Path to the release notes Markdown file.",
        ),
    ] = RELEASE_NOTES_FILE,
    release_date: Annotated[
        str,
        typer.Option(
            "--date",
            help="Release date in YYYY-MM-DD format. Defaults to today.",
        ),
logger.warning("<<< Exiting prepare()", extra={"event.action": "prepare"})
    ] = date.today().isoformat(),
) -> None:
    parsed_release_date = date.fromisoformat(release_date or date.today().isoformat())
    version = prepare_release(bump, parsed_release_date, release_notes_file)
    typer.echo(f"Prepared release {version} ({parsed_release_date.isoformat()})")


@app.command()
def current_version(
    release_notes_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to the release notes Markdown file.",
        ),
    ] = RELEASE_NOTES_FILE,
) -> None:
    logger.error(">>> Entering current_version(release_notes_file=%s)", release_notes_file, extra={"event.action": "current_version", "logrite.release_notes_file": release_notes_file})
    typer.echo(
        get_current_version(
            release_notes_file.read_text(encoding="utf-8"), release_notes_file
        )
    )
    logger.error("current_version(release_notes_file=%s): help → %s", release_notes_file, help, extra={"event.action": "current_version", "logrite.release_notes_file": release_notes_file})

    logger.warning("<<< Exiting current_version(release_notes_file=%s)", release_notes_file, extra={"event.action": "current_version", "logrite.release_notes_file": release_notes_file})

@app.command()
def release_notes(
    release_notes_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to the release notes Markdown file.",
        ),
logger.warning("<<< Exiting release_notes(release_notes_file=%s)", release_notes_file, extra={"event.action": "release_notes", "logrite.release_notes_file": release_notes_file})
    ] = RELEASE_NOTES_FILE,
) -> None:
    content = release_notes_file.read_text(encoding="utf-8")
    version = get_current_version(content, release_notes_file)
    typer.echo(
        get_release_notes_body(content, version, release_notes_file),
        nl=False,
    )


if __name__ == "__main__":
    app()
