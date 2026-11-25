from datetime import date, timedelta
from hashlib import sha256
from html import escape

from drawing import ASSETS, BLUE, GREEN, INK, INNER, MUTED, OCHRE, PAPER, PURPLE, RED, ROOT, TEAL
from drawing import icon, panel, sticker, width
from github_stats import DAY, LOGIN, fetch_profile


MONTHS = ("янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек")
HEAT = ("#3b3a55", "#28573d", "#347b4c", "#45a862", "#78de8d")


def number(value):
    return f"{value:,}".replace(",", " ")


def plural(n, one, few, many):
    if 11 <= n % 100 <= 14:
        return many
    if n % 10 == 1:
        return one
    return few if 2 <= n % 10 <= 4 else many


def contributions(n):
    return plural(n, "вклад", "вклада", "вкладов")


def duration(n):
    return f'{number(n)} {plural(n, "день", "дня", "дней")}'


def short_date(day):
    return f"{day.day} {MONTHS[day.month-1]}"


def month_start(day, offset=0):
    year, month = divmod(day.year*12 + day.month-1 + offset, 12)
    return date(year, month+1, 1)


def metric_card(w, h, color, symbol, value, lines, mobile):
    card = sticker(w, h, color, 20 if mobile else 24)
    left = 13 if mobile else 20
    icon(card, symbol, w-(43 if mobile else 55), 16, 24 if mobile else 30)
    size = 34 if mobile else 49
    value_size = min(size, size * (w-2*left-3) / width(value, size))
    card.text(left, 49 if mobile else 62, value, value_size)
    for i, label in enumerate(lines):
        size = 17 if mobile else 18.5
        card.text(left, (94+i*22) if mobile else (117+i*24), label, size, face="mono")
    return card


def counter(w, h, color, symbol, n, label, mobile):
    tile = sticker(w, h, color, 14 if mobile else 22)
    value = number(n)
    big, small, icon_size = (30, 17, 25) if mobile else (39, 17.5, 34)
    group_width = icon_size + 12 + width(value, big) + 9 + width(label, small, "mono")
    x, y = (w-group_width)/2, (h-5)/2
    icon(tile, symbol, x, y-icon_size/2, icon_size)
    x += icon_size + 12
    tile.text(x, y, value, big, anchor="lm")
    tile.text(x + width(value, big) + 9, y+1, label, small, face="mono", anchor="lm")
    return tile


def statistics(profile, year_total, mobile):
    current, start, longest = profile.streaks()
    total = sum(profile.days.values())
    canvas = panel(420, 637) if mobile else panel(1120, 432)
    stamp = f"Обновлено {short_date(profile.today)} {profile.today.year}"
    if mobile:
        canvas.text(21, 23, "На GitHub", 33)
        canvas.text(22, 66, stamp, 16.5, MUTED, "mono")
    else:
        canvas.text(40, 40, "На GitHub", 38)
        canvas.text(1080, 59, stamp, 18, MUTED, "mono", "rm")

    metrics = (
        (BLUE, "calendar", number(year_total), (contributions(year_total), "за 365 дней" if mobile else "за последний год")),
        (GREEN, "flame", duration(current), ("текущая серия", f"с {short_date(start)}" if start else "сейчас")),
        (OCHRE, "trophy", duration(longest), ("рекордная серия", "за всё время")),
        (PURPLE, "chart", number(total), (contributions(total), f"с {profile.joined.year} года")),
    )
    for i, metric in enumerate(metrics):
        w, h = (185, 146) if mobile else (246, 180)
        tile = metric_card(w, h, *metric, mobile)
        x, y = (20 + i%2*195, 100 + i//2*157) if mobile else (39 + i*265, 100)
        canvas.place(tile, x, y, (1.0, -0.6, 0.6, -0.9)[i])

    counts = (
        (TEAL, "folder", profile.repositories, plural(profile.repositories, "репозиторий", "репозитория", "репозиториев")),
        (RED, "star", profile.stars, plural(profile.stars, "звезда", "звезды", "звёзд")),
        (GREEN, "download", profile.downloads, plural(profile.downloads, "загрузка", "загрузки", "загрузок") + " файлов"),
    )
    for i, metric in enumerate(counts):
        x, w = ((39, 307), (366, 305), (690, 391))[i]
        tile = counter(380 if mobile else w, 57 if mobile else 89, *metric, mobile)
        canvas.place(tile, 20 if mobile else x, 418+i*65 if mobile else 301, (0.5, -0.4, 0.4)[i])
    canvas.save("stats-mobile.png" if mobile else "stats.png")


def heat_level(n):
    return int(n > 0) + int(n >= 3) + int(n >= 6) + int(n >= 10)


def grid(canvas, profile, first, end, x, y, w, mobile):
    monday = first - timedelta(days=first.weekday())
    weeks = (end - monday).days // 7 + 1
    column = w / weeks
    row = 28.5 if mobile else 37
    label = first
    while label <= end:
        week = (label-monday).days // 7
        canvas.text(x+week*column+1, y-25, MONTHS[label.month-1].capitalize(), 17.5, MUTED, "mono")
        label = month_start(label, 1)

    day = first
    while day <= min(profile.today, end):
        n = profile.days.get(day, 0)
        level = heat_level(n)
        xx = x + (day-monday).days//7 * column
        yy = y + day.weekday()*row
        cw, ch = column-3.2, row-3.2
        canvas.rect((xx, yy, xx+cw, yy+ch), HEAT[level], 5)
        ink = "#101d18" if level >= 3 else (PAPER if level else "#c5c1d6")
        size = min(17, (cw-3)/(0.61*len(str(n))))
        canvas.text(xx+cw/2, yy+ch/2, str(n), size, ink, "mono", "mm")
        day += DAY


def legend(canvas, x, y, mobile):
    size = 15 if mobile else 17
    canvas.text(x, y, "Меньше", size, MUTED, "mono", "lm")
    x += width("Меньше", size, "mono")+9
    for color in HEAT:
        canvas.rect((x, y-8, x+15, y+7), color, 3)
        x += 19
    canvas.text(x+2, y, "Больше", size, MUTED, "mono", "lm")


def activity(profile, first, six_total, mobile):
    w, h = (420, 860) if mobile else (1120, 512)
    canvas = panel(w, h)
    pad = 12 if mobile else 35
    canvas.rect((pad+2, pad+4, w-pad, h-pad), INK, 19)
    canvas.rect((pad, pad, w-pad-3, h-pad-5), INNER, 19, INK, 2.5)
    x, baseline = (25, 55) if mobile else (55, 88)
    size = 28 if mobile else 33
    value = number(six_total)
    canvas.text(x, baseline, value, size, anchor="ls")
    canvas.text(x+width(value, size)+8, baseline-1, f"{contributions(six_total)} за 6 месяцев",
                17.5 if mobile else 21, face="mono", anchor="ls")
    if mobile:
        for i in range(3):
            start = month_start(first, i*2)
            grid(canvas, profile, start, month_start(start, 2)-DAY, 26, 98+i*239, w-52, True)
        canvas.text(25, 793, "Вклады по дням · Пн–Вс", 16, MUTED, "mono")
        legend(canvas, 25, 827, True)
    else:
        grid(canvas, profile, first, month_start(first, 6)-DAY, 55, 139, w-110, False)
        canvas.text(55, 445, "Вклады по дням · Пн–Вс", 18, MUTED, "mono", "lm")
        legend(canvas, 832, 445, False)
    canvas.save("activity-mobile.png" if mobile else "activity.png")


def image_url(filename):
    version = sha256((ASSETS / filename).read_bytes()).hexdigest()[:12]
    return f"https://raw.githubusercontent.com/{LOGIN}/{LOGIN}/main/assets/{filename}?v={version}"


def picture(name, alt):
    small = image_url(f"{name}-mobile.png")
    large = image_url(f"{name}.png")
    return (f'<p align="center">\n  <picture>\n    <source media="(max-width: 600px)" srcset="{small}">\n'
            f'    <img src="{large}" width="100%" alt="{escape(alt, quote=True)}">\n  </picture>\n</p>')


def render(profile):
    year_start = profile.today - 364*DAY
    first = month_start(profile.today, -5)
    year_total = sum(n for d, n in profile.days.items() if d >= year_start)
    six_total = sum(n for d, n in profile.days.items() if d >= first)
    for mobile in (False, True):
        statistics(profile, year_total, mobile)
        activity(profile, first, six_total, mobile)

    current, _, longest = profile.streaks()
    total = sum(profile.days.values())
    updated = f"{short_date(profile.today)} {profile.today.year}"
    stats_alt = (f"Статистика GitHub на {updated}. За 365 дней — {number(year_total)} {contributions(year_total)}. "
                 f"Текущая серия — {duration(current)}, рекорд — {duration(longest)}. "
                 f"С {profile.joined.year} года — {number(total)} {contributions(total)}. "
                 f"Публичные репозитории — {profile.repositories}, звёзды — {profile.stars}, "
                 f"скачивания файлов публичных релизов — {profile.downloads}.")
    calendar_alt = (f"Календарь с {short_date(first)} {first.year} по {updated}. "
                    f"Всего {number(six_total)} {contributions(six_total)}. В ячейках указано число вкладов за день.")
    readme = ROOT / "README.md"
    content = readme.read_text()
    begin, end = "<!-- profile-stats:start -->", "<!-- profile-stats:end -->"
    if content.count(begin) != 1 or content.count(end) != 1 or content.index(begin) > content.index(end):
        raise ValueError("Expected one statistics block in README.md")
    prefix, rest = content.split(begin)
    _, suffix = rest.split(end)
    block = "\n\n".join([begin, picture("stats", stats_alt), picture("activity", calendar_alt), end])
    readme.write_text(prefix + block + suffix)


if __name__ == "__main__":
    render(fetch_profile())
