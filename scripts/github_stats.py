import json
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from urllib.request import Request, urlopen


LOGIN = "loujessler"
DAY = timedelta(days=1)


class CalendarParser(HTMLParser):
    """Read dates and their numeric tooltips from GitHub's public contribution grid."""

    def __init__(self):
        super().__init__()
        self.cells = {}
        self.days = {}
        self.tip_date = None
        self.tip_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs:
            self.cells[attrs["id"]] = date.fromisoformat(attrs["data-date"])
        elif tag == "tool-tip":
            self.tip_date = self.cells.get(attrs.get("for"))
            self.tip_text = []

    def handle_data(self, data):
        if self.tip_date is not None:
            self.tip_text.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.tip_date is not None:
            label = "".join(self.tip_text).strip()
            match = re.match(r"^(No|[\d,]+) contributions? on\b", label)
            if not match:
                raise ValueError(f"Unexpected calendar label for {self.tip_date}: {label!r}")
            count = match[1]
            self.days[self.tip_date] = 0 if count == "No" else int(count.replace(",", ""))
            self.tip_date = None


def public_calendar(joined, today):
    days = {}
    for year in range(joined.year, today.year + 1):
        url = f"https://github.com/users/{LOGIN}/contributions?from={year}-01-01&to={year}-12-31"
        request = Request(url, headers={"User-Agent": "loujessler-profile", "Accept-Language": "en-US"})
        parser = CalendarParser()
        with urlopen(request, timeout=35) as response:
            parser.feed(response.read().decode())
        parser.close()
        days.update(parser.days)
    public = {day: count for day, count in days.items() if joined <= day <= today}
    if len(public) != (today - joined).days + 1:
        raise ValueError("Incomplete public contribution calendar")
    return public


def github(endpoint, paginate=False):
    command = ["gh", "api", endpoint]
    if paginate:
        command += ["--paginate", "--slurp"]
    data = json.loads(subprocess.check_output(command))
    return [item for page in data for item in page] if paginate else data


@dataclass
class Profile:
    today: date
    joined: date
    days: dict[date, int]
    repositories: int
    stars: int
    downloads: int

    def streaks(self):
        current = longest = 0
        for day in sorted(self.days):
            if day == self.today and self.days[day] == 0:
                break
            current = current + 1 if self.days[day] else 0
            longest = max(longest, current)
        last_active = self.today if self.days[self.today] else self.today - DAY
        start = last_active - (current - 1) * DAY if current else None
        return current, start, longest


def fetch_profile():
    today = datetime.now(timezone.utc).date()
    joined = date.fromisoformat(github(f"users/{LOGIN}")["created_at"][:10])
    days = public_calendar(joined, today)
    repos = github(f"users/{LOGIN}/repos?type=owner&per_page=100", paginate=True)
    public_repos = [repo for repo in repos if not repo["private"]]
    stars = sum(repo["stargazers_count"] for repo in public_repos)
    downloads = 0
    for repo in public_repos:
        releases = github(f"repos/{repo['full_name']}/releases?per_page=100", paginate=True)
        downloads += sum(
            asset["download_count"]
            for release in releases if not release["draft"]
            for asset in release["assets"]
        )
    return Profile(today, joined, days, len(public_repos), stars, downloads)
