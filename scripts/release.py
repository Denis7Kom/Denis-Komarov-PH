import re
import subprocess
from datetime import date
from pathlib import Path


def git(*args):
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").strip()


def replace_once(path, pattern, replacement):
    source = path.read_bytes().decode("utf-8")
    updated, count = re.subn(pattern, replacement, source)
    if count != 1:
        raise ValueError(f"Expected one version marker in {path}, found {count}")
    return updated.encode("utf-8")


index = Path("index.html")
html = index.read_bytes()
marker = b'<script type="module" src="./version-badge.js"></script>'
before = git("rev-parse", "HEAD")
if marker not in html:
    opening = list(re.finditer(rb"</body\s*>", html, re.I))
    if not opening:
        raise ValueError("No closing body in index.html")
    position = opening[-1].start()
    index.write_bytes(html[:position] + marker + html[position:])
    git("add", "index.html")
    git("commit", "-m", "chore(versioning): connect website badge")

version_path = Path("VERSION")
current = version_path.read_text().strip()
major, minor, patch, stage = re.fullmatch(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-alpha|-beta)?", current
).groups()
tag = f"v{current}"
if not git("tag", "--list", tag):
    baseline = git("log", "--first-parent", "--diff-filter=A", "-1", "--format=%H", "--", "VERSION")
    if git("rev-parse", "HEAD") != before:
        baseline = git("rev-parse", "HEAD")
    if not baseline or git("show", f"{baseline}:VERSION") != current:
        raise ValueError(f"Cannot identify baseline for {tag}")
    git("tag", tag, baseline)

bump = 0
changes = []
for commit in git("rev-list", "--reverse", f"{tag}..HEAD").splitlines():
    message = git("show", "-s", "--format=%B", commit)
    subject = message.splitlines()[0] if message else ""
    header = re.match(r"^\w+(?:\([^()\n]+\))?(!)?: ", subject)
    if (header and header[1]) or re.search(r"^BREAKING[ -]CHANGE: \S", message, re.M):
        rank = 3
    elif re.match(r"^feat(?:\([^()\n]+\))?: ", subject):
        rank = 2
    elif re.match(r"^fix(?:\([^()\n]+\))?: ", subject):
        rank = 1
    else:
        continue
    bump = max(bump, rank)
    changes.append(f"- {subject} ({commit[:7]})")

if bump:
    numbers = [int(major), int(minor), int(patch)]
    component = 3 - bump
    numbers[component] += 1
    numbers[component + 1:] = [0] * (2 - component)
    version = ".".join(map(str, numbers)) + (stage or "")
    next_tag = f"v{version}"
    if git("tag", "--list", next_tag):
        raise ValueError(f"Tag already exists: {next_tag}")
    badge = Path("version-badge.js")
    changelog = Path("CHANGELOG.md")
    badge_content = replace_once(badge, r'(?<=const projectVersion = ")[^"]+', version)
    heading, prior = changelog.read_text(encoding="utf-8").split("\n\n", 1)
    notes = "\n".join(changes)
    badge.write_bytes(badge_content)
    version_path.write_text(version + "\n")
    changelog.write_text(
        f"{heading}\n\n## {version} — {date.today().isoformat()}\n\n{notes}\n\n{prior}",
        encoding="utf-8",
    )
    git("add", "VERSION", "CHANGELOG.md", "version-badge.js")
    git("commit", "-m", f"chore(release): {version}")
    git("tag", next_tag)
    git("push", "--atomic", "origin", "HEAD:refs/heads/main",
        f"refs/tags/{tag}", f"refs/tags/{next_tag}")
else:
    git("push", "--atomic", "origin", "HEAD:refs/heads/main", f"refs/tags/{tag}")
