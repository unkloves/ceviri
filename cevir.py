# -*- coding: utf-8 -*-
"""metin.txt (temiz Rusça) -> Turkce, Vesperis formatinda: maca-kizi-TR.txt
Baslik satirlarinin onune '# ', bolum ayraclarina '***', en sona ceviri notu.
GitHub Actions uzerinde calisir; ceviriyi Google (deep-translator) yapar."""
import re, time
from deep_translator import GoogleTranslator

SRC = "metin.txt"
OUT = "maca-kizi-TR.txt"

NOT = ("— — —\n\n"
       "Bu kitap, Aleksandr Puşkin adlı yazarın kamu malı olan “Maça Kızı” adlı "
       "eserinin Rusça özgün metninden makine çevirisiyle Türkçeye çevrilmiştir. "
       "Çeviri bir insan çevirmen tarafından yapılmamıştır; metinde hatalar ve "
       "anlam kaymaları bulunabilir.")

CHWORDS = ("ЧАСТЬ ГЛАВА КНИГА ПЕСНЬ Глава Часть Книга Песнь Пролог Эпилог "
           "Заключение ЗАКЛЮЧЕНИЕ Вступление Предисловие").split()

def is_heading(s):
    s = s.strip()
    if "\n" in s or len(s) > 72:
        return False
    if any(s.startswith(w) for w in CHWORDS):
        return True
    if re.fullmatch(r"[IVXLC]{1,6}\.?", s):          # I, II, III, IV, V, VI...
        return True
    st = s.rstrip(".").strip()
    if 2 <= len(st) <= 60 and st == st.upper() and re.search(r"[A-ZÀ-ÖØ-ÞА-ЯЁ]{2}", st):
        return True
    return False

def split_chunks(text, n=4500):
    out, cur = [], ""
    for part in re.split(r"(?<=[.!?…])\s+", text):
        while len(part) > n:
            if cur:
                out.append(cur); cur = ""
            out.append(part[:n]); part = part[n:]
        if len(cur) + len(part) + 1 > n:
            out.append(cur); cur = part
        else:
            cur = (cur + " " + part).strip()
    if cur:
        out.append(cur)
    return out

tr = GoogleTranslator(source="auto", target="tr")

def translate(text):
    res = []
    for ch in split_chunks(text):
        got = None
        for attempt in range(5):
            try:
                got = tr.translate(ch)
                break
            except Exception as e:
                if attempt == 4:
                    print("   !! ceviri hatasi, orijinal birakildi:", str(e)[:90])
                else:
                    time.sleep(3 * (attempt + 1))
        res.append(got if got else ch)
        time.sleep(1)
    return " ".join(res)

def main():
    txt = open(SRC, encoding="utf-8").read()
    sep = "\n\n" if "\n\n" in txt else "\n"
    blocks = [b for b in txt.split(sep) if b.strip()]
    out, total = [], len(blocks)
    for i, b in enumerate(blocks, 1):
        bs = b.strip()
        if re.fullmatch(r"\*( \*)*", bs):
            out.append("***")
        elif is_heading(bs):
            out.append("# " + translate(bs))
        else:
            out.append(translate(bs))
        if i % 10 == 0 or i == total:
            print(f"[{i}/{total}] blok cevrildi")
    result = "\n\n".join(out) + "\n\n" + NOT
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(result)
    print("YAZILDI:", OUT, "—", len(result), "karakter")

if __name__ == "__main__":
    main()
