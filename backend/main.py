"""
NebulaScreen API Server — FastAPI backend for the data-center monitoring dashboard.

Endpoints (matching the front-end DataService interface):
  GET /api/metrics    → Metrics { deviceCount, onlineRate, dailyOutput, alarmCount }
  GET /api/trend      → TrendPoint[] (24-hour output + efficiency trend)
  GET /api/alarms     → AlarmItem[] (real-time alarm list)
  GET /api/charts     → ChartData { alarmCategories, regionalRanking, radar }
  GET /health         → Health check

Usage:
  docker compose up api -d     # or: python -m uvicorn main:app --host 0.0.0.0 --port 8000
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

import pymysql
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── Configuration ─────────────────────────────────────────────
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "nebula"),
    "password": os.getenv("MYSQL_PASSWORD", "nebula2026!"),
    "database": os.getenv("MYSQL_DATABASE", "nebula_screen"),
    "charset": "utf8mb4",
}

# ── Connection pool helper ────────────────────────────────────
def get_conn():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset=DB_CONFIG["charset"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


# ── CORS & App ────────────────────────────────────────────────
app = FastAPI(
    title="NebulaScreen API",
    description="Data-center monitoring dashboard backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models (mirror front-end types) ──────────────────
class Metrics(BaseModel):
    deviceCount: int
    onlineRate: float
    dailyOutput: int
    alarmCount: int


class TrendPoint(BaseModel):
    time: str
    output: float
    efficiency: float


class AlarmItem(BaseModel):
    id: str
    time: str
    area: str
    level: str
    message: str


class NamedValue(BaseModel):
    name: str
    value: float


class RadarMetric(BaseModel):
    name: str
    value: float
    max: float


class ChartData(BaseModel):
    alarmCategories: list[NamedValue]
    regionalRanking: list[NamedValue]
    radar: list[RadarMetric]


# ── Health Check ──────────────────────────────────────────────
@app.get("/health")
def health():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "db": str(e)},
        )


# ── GET /api/metrics ──────────────────────────────────────────
@app.get("/api/metrics", response_model=Metrics)
def get_metrics():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Read from the pre-computed snapshot
            cur.execute(
                "SELECT device_count, online_rate, daily_output, alarm_count "
                "FROM metrics_snapshot ORDER BY snapshot_time DESC LIMIT 1"
            )
            row = cur.fetchone()
            if row:
                return Metrics(
                    deviceCount=row["device_count"],
                    onlineRate=round(row["online_rate"], 2),
                    dailyOutput=int(row["daily_output"]),
                    alarmCount=row["alarm_count"],
                )

        # Fallback: compute live
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM host_detail")
            device_count = cur.fetchone()["c"]

            cur.execute(
                "SELECT COUNT(*) AS c FROM tsar_raw "
                "WHERE `mod` = 'cpu_usage' AND `value` < 100 "
                "AND datetime >= DATE_SUB(NOW(), INTERVAL 1 HOUR)"
            )
            alive = cur.fetchone()["c"] or device_count
            online_rate = round(alive / max(device_count, 1) * 100, 2)

            cur.execute(
                "SELECT COALESCE(SUM(avg_value * sample_count), 0) AS total "
                "FROM hourly_stats_by_metric "
                "WHERE tag = 'disk_rw_sectors' "
                "AND hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)"
            )
            daily_output = int(cur.fetchone()["total"])

            cur.execute("SELECT COUNT(*) AS c FROM alarms")
            alarm_count = cur.fetchone()["c"]

        return Metrics(
            deviceCount=device_count,
            onlineRate=online_rate,
            dailyOutput=daily_output,
            alarmCount=alarm_count,
        )
    finally:
        conn.close()


# ── GET /api/trend ────────────────────────────────────────────
@app.get("/api/trend", response_model=list[TrendPoint])
def get_trend():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # CPU usage trend per hour (24 hours) — average across all hosts
            cur.execute(
                "SELECT hour_bj_str, avg_value, "
                "  (SELECT AVG(h2.avg_value) FROM hourly_stats_by_metric h2 "
                "   WHERE h2.hour_bj_str = h1.hour_bj_str AND h2.tag = 'cpu_percent' AND h2.`mod` = 'cpu_usage') AS cpu_val "
                "FROM hourly_stats_by_metric h1 "
                "WHERE h1.tag = 'disk_rw_sectors' "
                "GROUP BY hour_bj_str "
                "ORDER BY hour_bj_str "
                "LIMIT 24"
            )
            rows = cur.fetchall()

        points: list[TrendPoint] = []
        for r in rows:
            hour_label = r["hour_bj_str"][-8:-3] if r["hour_bj_str"] else "00:00"
            output = round(r["avg_value"] or 0, 1)
            eff = round((r["cpu_val"] or 75), 1)
            points.append(TrendPoint(time=hour_label, output=output, efficiency=eff))

        # If less than 24 rows, pad with empty points
        while len(points) < 24:
            h = len(points)
            points.append(
                TrendPoint(
                    time=f"{h:02d}:00",
                    output=0.0,
                    efficiency=0.0,
                )
            )

        return points
    finally:
        conn.close()


# ── GET /api/alarms ──────────────────────────────────────────
@app.get("/api/alarms", response_model=list[AlarmItem])
def get_alarms(limit: int = Query(10, ge=1, le=50)):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT alarm_id, `time`, area, `level`, message "
                "FROM alarms "
                "ORDER BY `time` DESC "
                "LIMIT %s",
                (limit,),
            )
            rows = cur.fetchall()

        return [
            AlarmItem(
                id=r["alarm_id"],
                time=r["time"].strftime("%H:%M:%S") if isinstance(r["time"], datetime) else str(r["time"]),
                area=r["area"],
                level=r["level"],
                message=r["message"],
            )
            for r in rows
        ]
    finally:
        conn.close()


# ── GET /api/charts ──────────────────────────────────────────
@app.get("/api/charts", response_model=ChartData)
def get_charts():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 1. Alarm categories (from alarms)
            cur.execute(
                "SELECT `level` AS name, COUNT(*) AS value "
                "FROM alarms "
                "GROUP BY `level`"
            )
            alarm_cats = [NamedValue(name=r["name"], value=r["value"]) for r in cur.fetchall()]

            # Fallback: static categories if no alarms yet
            if not alarm_cats:
                alarm_cats = [
                    NamedValue(name="设备故障", value=38),
                    NamedValue(name="工艺偏差", value=26),
                    NamedValue(name="环境异常", value=18),
                    NamedValue(name="网络中断", value=11),
                    NamedValue(name="其他", value=7),
                ]
            else:
                # Map level names to Chinese labels
                level_map = {
                    "critical": "设备故障",
                    "major": "工艺偏差",
                    "minor": "环境异常",
                    "notice": "通知",
                }
                for item in alarm_cats:
                    item.name = level_map.get(item.name, item.name)

            # 2. Regional ranking (by location, CPU usage)
            cur.execute(
                "SELECT h.location1 AS name, ROUND(AVG(t.value), 1) AS value "
                "FROM tsar_raw t "
                "JOIN host_detail h ON t.hostid = h.hostid "
                "WHERE t.`mod` = 'cpu_usage' "
                "  AND t.datetime >= DATE_SUB(NOW(), INTERVAL 24 HOUR) "
                "GROUP BY h.location1 "
                "ORDER BY value DESC"
            )
            ranking_rows = cur.fetchall()
            if ranking_rows:
                regional_ranking = [NamedValue(name=r["name"], value=r["value"]) for r in ranking_rows]
            else:
                # Fallback from hourly aggregation
                cur.execute(
                    "SELECT h.location1 AS name, ROUND(AVG(hsm.avg_value), 1) AS value "
                    "FROM hourly_stats_by_host_mod hsm "
                    "JOIN host_detail h ON hsm.hostid = h.hostid "
                    "WHERE hsm.`mod` = 'cpu_usage' "
                    "  AND hsm.hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_host_mod) "
                    "GROUP BY h.location1 "
                    "ORDER BY value DESC"
                )
                regional_ranking = [NamedValue(name=r["name"], value=r["value"]) for r in cur.fetchall()]

            # 3. Radar scores
            cur.execute("SELECT name, value, max_score FROM radar_scores ORDER BY id")
            radar = [
                RadarMetric(name=r["name"], value=r["value"], max=float(r["max_score"]))
                for r in cur.fetchall()
            ]

        return ChartData(
            alarmCategories=alarm_cats,
            regionalRanking=regional_ranking,
            radar=radar,
        )
    finally:
        conn.close()


# ── Entrypoint ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)