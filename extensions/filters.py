def display_title(title):
    title = str(title).strip()
    return title.upper() if len(title) <= 2 else title[:1].upper() + title[1:]
