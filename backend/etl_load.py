"""
NebulaScreen ETL 脚本 — 将 bigdata 四张明细表加工后写入 MySQL

数据来源:
  1. bigdata/host_detail.dat        — 主机信息 (20 台)
  2. bigdata/mod_detail.dat         — 指标字典 (55 个)
  3. bigdata/disk_tsar.dat          — 磁盘监控采集 (12,000 条)
  4. bigdata/pref_tsar.dat          — 性能监控采集 (67,200 条)
  5. bigdata/outputs/数据清洗/tsar_cleaned_with_datetime.csv  — 已清洗统一数据
  6. bigdata/outputs/核心结果表/hourly_stats_by_metric.csv    — 小时级按指标聚合
  7. bigdata/outputs/核心结果表/hourly_stats_by_host_mod.csv  — 小时级按主机聚合

用法:
  docker compose up mysql -d          # 先启动 MySQL
  pip install pymysql pandas sqlalchemy --break-system-packages
  python backend/etl_load.py          # 运行 ETL 导入
"""

import csv
import os
import sys
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# ── Configuration ─────────────────────────────────────────────
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "nebula"),
    "password": os.getenv("MYSQL_PASSWORD", "nebula2026!"),
    "database": os.getenv("MYSQL_DATABASE", "nebula_screen"),
    "charset": "utf8mb4",
}

BIGDATA_DIR = Path(os.getenv("BIGDATA_DIR", os.path.join(os.path.dirname(__file__), "..", "bigdata")))
DATA_CLEAN_DIR = BIGDATA_DIR / "outputs" / "数据清洗"
CORE_RESULT_DIR = BIGDATA_DIR / "outputs" / "核心结果表"

CHUNK_SIZE = 5000  # Rows per INSERT batch

# ── SQLAlchemy Engine ─────────────────────────────────────────
def get_engine() -> Engine:
    url = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        f"?charset={DB_CONFIG['charset']}"
    )
    return create_engine(url, echo=False, pool_pre_ping=True)


def get_conn():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset=DB_CONFIG["charset"],
        local_infile=True,
    )


# ── Data Loaders ──────────────────────────────────────────────
def load_host_detail(bigdata_dir: Path):
    """Parse host_detail.dat (Tab-separated) → DataFrame."""
    file = bigdata_dir / "host_detail.dat"
    if not file.exists():
        print(f"[WARN] {file} not found, skipping host_detail")
        return None

    rows = []
    with open(file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            rows.append({
                "hostid": r["hostid"].strip(),
                "hostname": r["hostname"].strip(),
                "owner": r["owner"].strip(),
                "model": r["model"].strip(),
                "location1": r["location1"].strip(),
                "location2": r["location2"].strip(),
            })
    df = pd.DataFrame(rows)
    print(f"[OK] host_detail: {len(df)} rows loaded")
    return df


def load_mod_detail(bigdata_dir: Path):
    """Parse mod_detail.dat (Tab-separated) → DataFrame."""
    file = bigdata_dir / "mod_detail.dat"
    if not file.exists():
        print(f"[WARN] {file} not found, skipping mod_detail")
        return None

    rows = []
    with open(file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            rows.append({
                "mod": r["mod"].strip(),
                "type": r["type"].strip(),
                "desc": r["desc"].strip(),
                "unit": r.get("unit", "").strip() or None,
                "tag": r["tag"].strip(),
            })
    df = pd.DataFrame(rows)
    print(f"[OK] mod_detail: {len(df)} rows loaded")
    return df


def load_tsar_cleaned():
    """Load the already-cleaned unified CSV."""
    file = DATA_CLEAN_DIR / "tsar_cleaned_with_datetime.csv"
    if not file.exists():
        print(f"[WARN] {file} not found, skipping tsar_raw")
        return None

    # This is a large file (~7.6 MB), so read with chunks and selected dtypes
    dtypes = {
        "ts": "int64",
        "datetime_bj_str": "string",
        "hour_bj_str": "string",
        "hostid": "string",
        "type": "string",
        "mod": "string",
        "value": "float64",
        "tag": "string",
    }
    df = pd.read_csv(
        file,
        dtype=dtypes,
        encoding="utf-8-sig",
        low_memory=False,
    )
    # Rename datetime_bj_str → datetime for DB column
    df.rename(columns={"datetime_bj_str": "datetime"}, inplace=True)
    # Drop the hour_bj_str column (redundant with datetime)
    df.drop(columns=["hour_bj_str"], inplace=True, errors="ignore")
    print(f"[OK] tsar_cleaned: {len(df):,} rows loaded ({len(df.columns)} cols)")
    return df


def load_hourly_by_metric():
    file = CORE_RESULT_DIR / "hourly_stats_by_metric.csv"
    if not file.exists():
        print(f"[WARN] {file} not found, skipping hourly_stats_by_metric")
        return None
    df = pd.read_csv(file, encoding="utf-8-sig")
    print(f"[OK] hourly_stats_by_metric: {len(df):,} rows loaded")
    return df


def load_hourly_by_host_mod():
    file = CORE_RESULT_DIR / "hourly_stats_by_host_mod.csv"
    if not file.exists():
        print(f"[WARN] {file} not found, skipping hourly_stats_by_host_mod")
        return None
    df = pd.read_csv(file, encoding="utf-8-sig")
    print(f"[OK] hourly_stats_by_host_mod: {len(df):,} rows loaded")
    return df


# ── Database Writes ───────────────────────────────────────────
def write_to_mysql(df: pd.DataFrame, table: str, engine: Engine, if_exists: str = "append"):
    """Write a DataFrame to MySQL in chunks."""
    if df is None or len(df) == 0:
        return
    t0 = time.time()
    df.to_sql(table, engine, if_exists=if_exists, index=False,
              chunksize=CHUNK_SIZE, method="multi")
    elapsed = time.time() - t0
    print(f"[DB] {table}: {len(df):,} rows written in {elapsed:.1f}s")


def write_tsar_raw(df: pd.DataFrame, engine: Engine):
    """Write tsar_raw in chunks (large table)."""
    if df is None or len(df) == 0:
        return
    t0 = time.time()
    total = len(df)
    for start in range(0, total, CHUNK_SIZE):
        chunk = df.iloc[start : start + CHUNK_SIZE]
        chunk.to_sql("tsar_raw", engine, if_exists="append", index=False, method="multi")
        pct = min(100, round((start + len(chunk)) / total * 100))
        print(f"  tsar_raw: {start + len(chunk):,} / {total:,} ({pct}%)", end="\r")
    elapsed = time.time() - t0
    print(f"\n[DB] tsar_raw: {total:,} rows written in {elapsed:.1f}s")


# ── Derived Data Generators ───────────────────────────────────
def generate_alarms(engine: Engine, mod_detail_df: pd.DataFrame):
    """Generate synthetic alarms from metric thresholds in tsar_raw."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Clear existing alarms
            cur.execute("DELETE FROM alarms")
            conn.commit()

            # Generate alarms: find high-util, high-latency, and high-load hosts
            queries = {
                "critical": """
                    SELECT DISTINCT t.hostid,
                        CONCAT(h.location1, '-', h.location2) AS area,
                        CONCAT(m.`desc`, ' 严重超限 (',
                            CASE WHEN m.unit='%' AND t.value>90 THEN CONCAT(ROUND(t.value,1),'%')
                                 WHEN m.tag='disk_latency_ms' AND t.value>80 THEN CONCAT(ROUND(t.value,1),'ms')
                                 ELSE CONCAT(ROUND(t.value,1))
                            END,
                        ')') AS message
                    FROM tsar_raw t
                    JOIN mod_detail m ON t.`mod` = m.`mod`
                    JOIN host_detail h ON t.hostid = h.hostid
                    WHERE t.datetime >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                      AND (
                        (t.tag = 'disk_util_percent' AND t.value > 90)
                        OR (t.tag = 'disk_latency_ms' AND t.value > 80)
                        OR (t.tag = 'cpu_percent' AND t.mod = 'cpu_usage' AND t.value > 90)
                      )
                    LIMIT 3
                """,
                "major": """
                    SELECT DISTINCT t.hostid,
                        CONCAT(h.location1, '-', h.location2) AS area,
                        CONCAT(m.`desc`, ' 偏高 (',
                            CASE WHEN m.unit='%' THEN CONCAT(ROUND(t.value,1),'%')
                                 ELSE CONCAT(ROUND(t.value,1))
                            END,
                        ')') AS message
                    FROM tsar_raw t
                    JOIN mod_detail m ON t.`mod` = m.`mod`
                    JOIN host_detail h ON t.hostid = h.hostid
                    WHERE t.datetime >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                      AND (
                        (t.tag = 'disk_util_percent' AND t.value BETWEEN 75 AND 90)
                        OR (t.tag = 'disk_latency_ms' AND t.value BETWEEN 50 AND 80)
                        OR (t.tag = 'load_average' AND t.mod = 'load1' AND t.value > 20)
                      )
                    LIMIT 3
                """,
                "minor": """
                    SELECT DISTINCT t.hostid,
                        CONCAT(h.location1, '-', h.location2) AS area,
                        CONCAT(m.`desc`, ' 轻微波动 (',
                            CASE WHEN m.unit='%' THEN CONCAT(ROUND(t.value,1),'%')
                                 WHEN m.unit='MB' THEN CONCAT(ROUND(t.value,1),'MB')
                                 ELSE CONCAT(ROUND(t.value,1))
                            END,
                        ')') AS message
                    FROM tsar_raw t
                    JOIN mod_detail m ON t.`mod` = m.`mod`
                    JOIN host_detail h ON t.hostid = h.hostid
                    WHERE t.datetime >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                      AND (
                        (t.tag = 'disk_latency_ms' AND t.value BETWEEN 30 AND 50)
                        OR (t.tag = 'mem_metric' AND t.mod = 'mem_swap' AND t.value > 100000)
                      )
                    LIMIT 2
                """,
                "notice": """
                    SELECT DISTINCT t.hostid,
                        CONCAT(h.location1, '-', h.location2) AS area,
                        CONCAT('计划维护提醒 — ', h.hostname) AS message
                    FROM tsar_raw t
                    JOIN host_detail h ON t.hostid = h.hostid
                    WHERE t.datetime >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                    LIMIT 2
                """,
            }

            alarm_num = 0
            now = datetime.now()
            for level, query in queries.items():
                cur.execute(query)
                rows = cur.fetchall()
                for hostid, area, message in rows:
                    alarm_num += 1
                    alarm_id = f"ALM-{now.strftime('%Y%m%d')}-{alarm_num:04d}"
                    cur.execute(
                        """INSERT INTO alarms (alarm_id, `time`, area, `level`, message)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (alarm_id, now - timedelta(minutes=random.randint(1, 240)),
                         area, level, message[:256]),
                    )
            conn.commit()
            cur.execute("SELECT COUNT(*) FROM alarms")
            count = cur.fetchone()[0]
            print(f"[OK] alarms: {count} rows generated")
    finally:
        conn.close()


def update_metrics_snapshot(engine: Engine):
    """Refresh the metrics_snapshot table from live data."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE metrics_snapshot SET
                  device_count = (SELECT COUNT(*) FROM host_detail),
                  online_rate  = COALESCE(
                    (SELECT AVG(CASE WHEN t.value < 100 THEN 100 ELSE 0 END)
                     FROM (SELECT DISTINCT hostid, value FROM tsar_raw
                           WHERE `mod` = 'cpu_usage'
                           ORDER BY datetime DESC) t),
                    100.0
                  ),
                  daily_output = COALESCE(
                    (SELECT SUM(avg_value * sample_count)
                     FROM hourly_stats_by_metric hsm
                     JOIN mod_detail m ON hsm.`mod` = m.`mod`
                     WHERE hsm.hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
                       AND hsm.tag = 'disk_rw_sectors'),
                    0
                  ),
                  alarm_count  = (SELECT COUNT(*) FROM alarms),
                  snapshot_time = NOW()
            """)
            conn.commit()
            print("[OK] metrics_snapshot updated")
    finally:
        conn.close()


def update_radar_scores(engine: Engine):
    """Compute radar scores from hourly aggregates."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 产能: based on CPU usage inverse
            cur.execute("""
                SELECT COALESCE(
                    ROUND((100 - AVG(avg_value)) * 1.2, 1), 88.0
                ) FROM hourly_stats_by_metric
                WHERE `mod` = 'cpu_usage'
                  AND hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
            """)
            prod = min(100, max(0, (cur.fetchone()[0] or 88.0)))

            # 质量: inverse of disk latency
            cur.execute("""
                SELECT COALESCE(
                    ROUND(GREATEST(0, 100 - AVG(avg_value) * 0.15), 1), 92.0
                ) FROM hourly_stats_by_metric
                WHERE tag = 'disk_latency_ms'
                  AND hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
            """)
            quality = min(100, max(0, (cur.fetchone()[0] or 92.0)))

            # 能效: based on disk utilization inverse
            cur.execute("""
                SELECT COALESCE(
                    ROUND(GREATEST(0, 100 - AVG(avg_value) * 0.25), 1), 79.0
                ) FROM hourly_stats_by_metric
                WHERE tag = 'disk_util_percent'
                  AND hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
            """)
            eff = min(100, max(0, (cur.fetchone()[0] or 79.0)))

            # 稳定性: based on load average
            cur.execute("""
                SELECT COALESCE(
                    ROUND(GREATEST(0, 100 - AVG(avg_value) * 1.2), 1), 85.0
                ) FROM hourly_stats_by_metric
                WHERE `mod` = 'load1'
                  AND hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
            """)
            stability = min(100, max(0, (cur.fetchone()[0] or 85.0)))

            # 安全: inverse of mem_swap
            cur.execute("""
                SELECT COALESCE(
                    ROUND(GREATEST(0, 100 - AVG(avg_value) * 0.01), 1), 94.0
                ) FROM hourly_stats_by_metric
                WHERE `mod` = 'mem_swap'
                  AND hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
            """)
            safety = min(100, max(0, (cur.fetchone()[0] or 94.0)))

            # 交付: based on network throughput
            cur.execute("""
                SELECT COALESCE(
                    ROUND(AVG(avg_value) * 0.08, 1), 81.0
                ) FROM hourly_stats_by_metric
                WHERE `mod` = 'net_in'
                  AND hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
            """)
            delivery = min(100, max(50, (cur.fetchone()[0] or 81.0)))

            scores = [
                ("产能", prod), ("质量", quality), ("能效", eff),
                ("稳定性", stability), ("安全", safety), ("交付", delivery),
            ]
            for name, val in scores:
                cur.execute(
                    "INSERT INTO radar_scores (name, value, max_score) VALUES (%s, %s, 100) "
                    "ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = NOW()",
                    (name, val),
                )
            conn.commit()
            print(f"[OK] radar_scores updated: {dict(scores)}")
    finally:
        conn.close()


# ── Main ──────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("NebulaScreen ETL — bigdata → MySQL")
    print("=" * 60)

    engine = get_engine()

    # Step 1: Load & insert dimension tables
    print("\n── Step 1: Dimension tables ──")
    host_df = load_host_detail(BIGDATA_DIR)
    if host_df is not None:
        write_to_mysql(host_df, "host_detail", engine, "replace")

    mod_df = load_mod_detail(BIGDATA_DIR)
    if mod_df is not None:
        write_to_mysql(mod_df, "mod_detail", engine, "replace")

    # Step 2: Load tsar_raw (largest table)
    print("\n── Step 2: tsar_raw ──")
    tsar_df = load_tsar_cleaned()
    if tsar_df is not None:
        write_tsar_raw(tsar_df, engine)

    # Step 3: Load hourly aggregations
    print("\n── Step 3: Hourly aggregations ──")
    by_metric = load_hourly_by_metric()
    if by_metric is not None:
        write_to_mysql(by_metric, "hourly_stats_by_metric", engine, "replace")

    by_host = load_hourly_by_host_mod()
    if by_host is not None:
        write_to_mysql(by_host, "hourly_stats_by_host_mod", engine, "replace")

    # Step 4: Generate derived data
    print("\n── Step 4: Derived data ──")
    if mod_df is not None:
        generate_alarms(engine, mod_df)
    update_metrics_snapshot(engine)
    update_radar_scores(engine)

    print("\n" + "=" * 60)
    print("ETL complete! All data loaded into MySQL nebula_screen.")
    print("=" * 60)


if __name__ == "__main__":
    main()