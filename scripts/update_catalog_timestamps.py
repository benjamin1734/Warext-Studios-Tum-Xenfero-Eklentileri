import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPOSITORIES = [
    "benjamin1734/Warext-Studios-Xenfero-Turkce-Yazim-Denetim-Eklentisi",
    "benjamin1734/Warext-Studios---Konu-Guncellik-Sistemi",
    "benjamin1734/Warext-Studios-Xenfero-Davet-Referans-Sistemi",
    "benjamin1734/Warext-Studios-Kullanici-Icerik-Yoneticisi",
    "benjamin1734/Warext-Studios-Xenfero-Hata-Bildirim-Sistemi",
    "benjamin1734/Warext-Studios-XenForo-Minecraft-Sunucu-Vote-Sistemi",
    "benjamin1734/Warext-Studios-Xenfero-Portfolyo-Sistemi",
    "benjamin1734/Warext-Studios-XenForo-Moderasyon-Denetim-Sistemi",
    "benjamin1734/Warext-Studios-XenForo-S.S.S.-Sistemi",
]

README = Path("README.md")
TOKEN = os.environ.get("GH_TOKEN", "")
ISTANBUL = timezone(timedelta(hours=3))


def latest_commit_time(repo: str) -> str:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/commits?per_page=1",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "warext-xenforo-catalog",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)

    if not data:
        raise RuntimeError(f"{repo}: commit bulunamadı")

    raw = data[0]["commit"]["committer"]["date"]
    commit_time = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return commit_time.astimezone(ISTANBUL).strftime("%d.%m.%Y %H:%M")


def main() -> None:
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()

    for repo in REPOSITORIES:
        try:
            stamp = latest_commit_time(repo)
        except Exception as exc:
            print(f"UYARI: {exc}")
            continue

        repo_url = f"https://github.com/{repo}"
        found = False

        for index, line in enumerate(lines):
            if repo_url not in line or not line.startswith("|"):
                continue

            cells = line.split(" | ")
            if len(cells) < 6:
                raise RuntimeError(f"README tablo satırı beklenen biçimde değil: {line}")

            cells[3] = f"**{stamp}**"
            lines[index] = " | ".join(cells)
            found = True
            break

        if not found:
            print(f"UYARI: README içinde repo satırı bulunamadı: {repo}")

    updated = "\n".join(lines) + "\n"
    if updated != text:
        README.write_text(updated, encoding="utf-8")
        print("README güncellendi.")
    else:
        print("Değişiklik yok.")


if __name__ == "__main__":
    main()
