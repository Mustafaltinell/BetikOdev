

import argparse, csv, json, os, statistics
from typing import List, Dict
from schema_decorator import ensure_schema, SchemaError

REQUIRED = ["name", "age", "city"]

def read_csv_rows(path: str):
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    return headers, rows

@ensure_schema(REQUIRED)
def clean_rows(headers: List[str], rows: List[Dict[str, str]]):
    cleaned = []
    for r in rows:
        # varsa olmayan anahtarlar için güvenli çekim
        name = (r.get("name") or "").strip()
        age_raw = (r.get("age") or "").strip()
        city = (r.get("city") or "").strip()

        # 3.a: age boşsa veya sayısal değilse atla
        if age_raw == "" or not age_raw.isdigit():
            continue

        # 3.b: age -> int
        age = int(age_raw)

        # 3.b: name ve city baş/son boşluk kırp (yukarıda yapıldı)
        cleaned.append({"name": name, "age": age, "city": city})
    return cleaned

def make_stats(cleaned: List[Dict[str, str]]):
    ages = [r["age"] for r in cleaned]
    valid_count = len(cleaned)
    avg_age = float(round(sum(ages) / valid_count, 2)) if valid_count else 0.0

    # şehre göre kişi sayısı
    by_city = {}
    for r in cleaned:
        c = r["city"]
        by_city[c] = by_city.get(c, 0) + 1

    return {
        "valid_record_count": valid_count,
        "average_age": avg_age,
        "count_by_city": by_city
    }

def write_outputs(cleaned: List[Dict[str, str]], stats: Dict, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "cleaned_records.json"), "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # 5.c: Kısa bir rapor .txt
    lines = []
    lines.append("RAPOR")
    lines.append("------")
    lines.append(f"Geçerli kayıt sayısı: {stats['valid_record_count']}")
    lines.append(f"Ortalama yaş: {stats['average_age']}")
    lines.append("Şehirlere göre dağılım:")
    for city, cnt in stats["count_by_city"].items():
        lines.append(f"  - {city}: {cnt}")
    with open(os.path.join(out_dir, "report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    ap = argparse.ArgumentParser(description="CSV temizleme ve istatistik üretme aracı")
    ap.add_argument("--input", required=True, help="Girdi CSV yolu (UTF-8)")
    ap.add_argument("--out", required=True, help="Çıktı klasörü")
    args = ap.parse_args()

    headers, rows = read_csv_rows(args.input)

    try:
        cleaned = clean_rows(headers=headers, rows=rows)
    except SchemaError as e:
        # 2: Zorunlu sütunlardan biri eksikse hata ver
        raise SystemExit(f"Şema hatası: {e}")

    stats = make_stats(cleaned)
    write_outputs(cleaned, stats, args.out)

if __name__ == "__main__":
    main()
