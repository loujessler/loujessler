from drawing import BLUE, CORAL, INK, MUTED, OCHRE, PAPER, PURPLE, RED, Canvas, icon, panel, sticker, width


CHIPS = (("macOS и Swift", BLUE), ("Telegram-боты", OCHRE),
         ("React", PURPLE), ("Тестовые данные", RED))
LINKS = (
    ("macgenuity", "MacGenuity", "desktop", RED),
    ("tronwalletbot", "TronWalletBot", "plane", PURPLE),
    ("codewars", "Codewars", "code", BLUE),
    ("repositories", "Репозитории", "folder", "#272641"),
)


def monogram(size):
    mark = Canvas(size, size)
    mark.rect((8, 9, size-1, size-1), "#f06b49", size*0.21, INK, 2.5)
    mark.rect((1, 1, size-8, size-8), "#f7f3e8", size*0.2, "#201d19", size*0.077)
    mark.text((size-7)/2, (size-9)/2, "A", size*0.76, "#221f1b", anchor="mm")
    return mark


def cover(mobile):
    canvas = panel(420, 320) if mobile else panel(1120, 310)
    logo_size = 70 if mobile else 119
    canvas.place(monogram(logo_size), 20 if mobile else 53, 66 if mobile else 54)

    title_size = 36 if mobile else 66
    title_x, baseline = (102, 116) if mobile else (216, 135)
    greeting = "Привет, я"
    name_x = title_x + width(greeting, title_size) + (8 if mobile else 13)
    pad = 8 if mobile else 13
    box_top = baseline - title_size*0.94
    canvas.rect((name_x, box_top, name_x + width("Alex", title_size) + 2*pad,
                 baseline + title_size*0.19), RED, 10 if mobile else 15)
    canvas.text(title_x, baseline, greeting, title_size, anchor="ls")
    canvas.text(name_x+pad, baseline, "Alex", title_size, anchor="ls")

    tag_w, tag_h, tag_size = (131, 36, 18) if mobile else (167, 55, 23)
    tag = sticker(tag_w, tag_h, CORAL, 11)
    tag.text((tag_w-3)/2, (tag_h-5)/2, "@loujessler", tag_size, INK, anchor="mm")
    canvas.place(tag, canvas.w-tag_w-(22 if mobile else 37), 15 if mobile else 36, -5)

    if mobile:
        canvas.text(22, 150, "Разрабатываю MacGenuity", 20, MUTED, "body")
        canvas.text(22, 176, "для мышей и микрофонов HyperX.", 20, MUTED, "body")
    else:
        canvas.text(217, 174, "Разрабатываю MacGenuity для мышей и микрофонов HyperX.", 23, MUTED, "body")

    x = title_x
    for i, (label, color) in enumerate(CHIPS):
        size = 16.5 if mobile else 18
        w = 184 if mobile else round(width(label, size) + 33)
        chip = sticker(w, 41 if mobile else 45, color, 11)
        chip.text((w-4)/2, (chip.h-5)/2, label, size, anchor="mm")
        if mobile:
            canvas.place(chip, 21 + (i%2)*194, 216 + (i//2)*46)
        else:
            canvas.place(chip, x, 218)
            x += w+12
    canvas.save("cover-mobile.png" if mobile else "cover.png")


def navigation():
    for slug, label, symbol, color in LINKS:
        w = round(width(label, 18) + 58)
        button = sticker(w, 46, color, 12)
        icon(button, symbol, 13, 10, 23, PAPER, INK)
        button.text(43, 20, label, 18, anchor="lm")
        button.save(f"link-{slug}.png")


if __name__ == "__main__":
    cover(False)
    cover(True)
    navigation()
