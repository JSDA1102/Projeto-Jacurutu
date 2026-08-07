"""
Atualiza automaticamente a base de dados a partir do CPGF (Portal da Transparência).

Fluxo:
    1. Detecta quais meses faltam em RAW_PATH (a partir dos CSVs já presentes).
    2. Baixa o ZIP de cada mês faltante (ou intervalo --start/--end).
    3. Extrai o CSV dentro de RAW_PATH.
    4. Roda o run_etl.py para regenerar o .parquet (a menos que --no-etl).

"""

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from urllib.request import urlopen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, "raw_data")
ETL_SCRIPT = os.path.join(BASE_DIR, "run_etl.py")

DOWNLOAD_URL = "https://portaldatransparencia.gov.br/download-de-dados/cpgf"


def month_key(y, m):
    """'YYYYMM' a partir de ano/mês."""
    return f"{y:04d}{m:02d}"


def first_day(y, m):
    """date primeiro dia do mês (m 1-12)."""
    return dt.date(y, m, 1)


def iter_months_until(end):
    """Gera YYYYMM de 2023-1 até end (inclusive)."""
    y, m = 2023, 1
    months = []
    while first_day(y, m) <= end:
        months.append(month_key(y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return months


def existing_months():
    """Set de YYYYMM presentes como CSVs na raw_data/."""
    if not os.path.isdir(RAW_PATH):
        return set()
    months = set()
    for f in os.listdir(RAW_PATH):
        head, ext = os.path.splitext(f)
        if ext.lower() != ".csv":
            continue
        ym = head.split("_")[0]
        if len(ym) == 6 and ym.isdigit():
            months.add(ym)
    return months


def download_zip(ym, dest_dir):
    """Baixa o ZIP do mês 'ym' e salva localmente. Retorna o caminho."""
    url = f"{DOWNLOAD_URL}/{ym}"
    dest = os.path.join(dest_dir, f"{ym}_CPGF.zip")
    sys.stdout.write(f"Baixando {ym}... ")
    sys.stdout.flush()
    with urlopen(url, timeout=120) as resp, open(dest, "wb") as out:
        shutil.copyfileobj(resp, out)
    sys.stdout.write("ok\n")
    return dest


def extract_csvs(zip_path):
    """Retorna o caminho do CSV extraído do ZIP para o diretório de trabalho."""
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".csv"):
                return zf.extract(name)
    return None


def parse_args():
    p = argparse.ArgumentParser(description="Atualiza a base CPGF do Portal da Transparência.")
    p.add_argument("--start", type=str, help="Mês inicial YYYYMM (default: mês mais antigo faltante).")
    p.add_argument("--end", type=str, help="Mês final YYYYMM (default: mês atual).")
    p.add_argument("--no-etl", action="store_true", help="Não roda o run_etl.py ao final.")
    p.add_argument("--dry-run", action="store_true", help="Apenas lista o plano, sem baixar.")
    return p.parse_args()


def main():
    args = parse_args()

    today = dt.date.today()
    end = dt.date(*map(int, (args.end[:4], args.end[4:6], 1))) if args.end else first_day(today.year, today.month)

    existing = existing_months()
    missing = sorted(m for m in iter_months_until(end) if m not in existing)

    if args.start:
        missing = [m for m in missing if m >= args.start]

    if not missing:
        print(f"Nenhum mês faltante até {end} — nada a fazer.")
        return

    print(f"Meses a atualizar: {len(missing)} ({missing[0]} → {missing[-1]}).")
    if args.dry_run:
        for m in missing:
            print(f"  - {m}")
        print("[dry-run] Encerrado sem baixar.")
        return

    os.makedirs(RAW_PATH, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        for ym in missing:
            zip_path = download_zip(ym, tmp)
            csv_path = extract_csvs(zip_path)
            if csv_path:
                dest = os.path.join(RAW_PATH, os.path.basename(csv_path))
                shutil.move(csv_path, dest)
                print(f"    -> salvo em {dest}")
            os.remove(zip_path)

    print(f"CSVs atualizados em {RAW_PATH}.")

    if not args.no_etl:
        print("Rodando run_etl.py para regenerar o .parquet...")
        subprocess.run([sys.executable, ETL_SCRIPT], check=True)
    else:
        print("ETL não executado (--no-etl). Rode manualmente: python run_etl.py")


if __name__ == "__main__":
    main()
