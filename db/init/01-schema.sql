-- NebulaScreen 数据中心运行监控大屏 — MySQL 数据库初始化脚本
-- 基于 bigdata 四张明细表（host_detail / mod_detail / disk_tsar / pref_tsar）的加工结果

CREATE DATABASE IF NOT EXISTS nebula_screen
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE nebula_screen;

-- ============================================================
-- Table 1: host_detail — 主机信息
-- 来源: bigdata/host_detail.dat (20 台服务器)
-- ============================================================
CREATE TABLE IF NOT EXISTS host_detail (
  hostid    VARCHAR(16)  NOT NULL PRIMARY KEY COMMENT '主机ID',
  hostname  VARCHAR(128) NOT NULL            COMMENT '主机FQDN名',
  owner     VARCHAR(32)  NOT NULL            COMMENT '负责人',
  model     VARCHAR(64)  NOT NULL            COMMENT '硬件型号',
  location1 VARCHAR(32)  NOT NULL            COMMENT '机房位置',
  location2 VARCHAR(32)  NOT NULL            COMMENT '机柜编号',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '主机信息明细表';

CREATE INDEX idx_host_location ON host_detail(location1, location2);

-- ============================================================
-- Table 2: mod_detail — 指标字典
-- 来源: bigdata/mod_detail.dat (55 个指标: 35 disk + 20 pref)
-- ============================================================
CREATE TABLE IF NOT EXISTS mod_detail (
  `mod` VARCHAR(32)  NOT NULL PRIMARY KEY COMMENT '指标代码',
  `type` VARCHAR(8)  NOT NULL            COMMENT '资源类型: disk / pref',
  `desc` VARCHAR(128) NOT NULL           COMMENT '指标中文说明',
  unit   VARCHAR(32)  DEFAULT NULL       COMMENT '单位',
  tag    VARCHAR(64)  NOT NULL           COMMENT '指标分类标签',
  INDEX idx_mod_type (`type`),
  INDEX idx_mod_tag (tag)
) ENGINE=InnoDB COMMENT '指标字典表';

-- ============================================================
-- Table 3: tsar_raw — 原始采集记录（统一存储 disk + pref）
-- 来源: bigdata/disk_tsar.dat + bigdata/pref_tsar.dat (~79,200 条)
-- ============================================================
CREATE TABLE IF NOT EXISTS tsar_raw (
  id       BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  ts       BIGINT          NOT NULL            COMMENT '采集时间戳（毫秒）',
  datetime DATETIME        NOT NULL            COMMENT '北京时间（YYYY-MM-DD HH:MM:SS）',
  hostid   VARCHAR(16)     NOT NULL            COMMENT '主机ID → host_detail.hostid',
  `type`   VARCHAR(8)      NOT NULL            COMMENT '资源类型: disk / pref',
  `mod`    VARCHAR(32)     NOT NULL            COMMENT '指标代码 → mod_detail.mod',
  value    DOUBLE          DEFAULT NULL        COMMENT '采集数值',
  tag      VARCHAR(64)     NOT NULL            COMMENT '指标分类标签',
  INDEX idx_ts (ts),
  INDEX idx_datetime (datetime),
  INDEX idx_hostid (hostid),
  INDEX idx_type_mod (`type`, `mod`),
  INDEX idx_datetime_host (datetime, hostid),
  CONSTRAINT fk_raw_host FOREIGN KEY (hostid) REFERENCES host_detail(hostid),
  CONSTRAINT fk_raw_mod  FOREIGN KEY (`mod`)   REFERENCES mod_detail(`mod`)
) ENGINE=InnoDB COMMENT '原始采集明细表（disk + pref 合并）';

-- ============================================================
-- Table 4: metrics_snapshot — 当前指标快照（每 60s 刷新）
-- 对应前端: Metrics { deviceCount, onlineRate, dailyOutput, alarmCount }
-- ============================================================
CREATE TABLE IF NOT EXISTS metrics_snapshot (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  device_count  INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '设备总数',
  online_rate   DOUBLE       NOT NULL DEFAULT 0 COMMENT '在线率（%）',
  daily_output  INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '今日产量（磁盘 I/O 总量）',
  alarm_count   INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '当前告警数量',
  snapshot_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '快照时间',
  INDEX idx_snapshot_time (snapshot_time)
) ENGINE=InnoDB COMMENT '当前指标快照';

INSERT INTO metrics_snapshot (device_count, online_rate, daily_output, alarm_count) VALUES (20, 100.0, 0, 0);

-- ============================================================
-- Table 5: hourly_stats_by_metric — 按小时/指标聚合
-- 来源: bigdata/outputs/核心结果表/hourly_stats_by_metric.csv
-- 对应前端: TrendPoint[] (trend 折线图), ChartData.alarmCategories (饼图)
-- ============================================================
CREATE TABLE IF NOT EXISTS hourly_stats_by_metric (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hour_bj_str  VARCHAR(19)     NOT NULL            COMMENT '北京时间小时（YYYY-MM-DD HH:00:00）',
  `type`       VARCHAR(8)      NOT NULL            COMMENT '资源类型: disk / pref',
  `mod`        VARCHAR(32)     NOT NULL            COMMENT '指标代码',
  tag          VARCHAR(64)     NOT NULL            COMMENT '指标分类标签',
  avg_value    DOUBLE          DEFAULT NULL        COMMENT '平均值',
  max_value    DOUBLE          DEFAULT NULL        COMMENT '最大值',
  min_value    DOUBLE          DEFAULT NULL        COMMENT '最小值',
  median_value DOUBLE          DEFAULT NULL        COMMENT '中位数',
  sample_count INT UNSIGNED    DEFAULT 0           COMMENT '采样数',
  host_count   INT UNSIGNED    DEFAULT 0           COMMENT '涉及主机数',
  INDEX idx_hour (hour_bj_str),
  INDEX idx_type_mod (`type`, `mod`),
  INDEX idx_tag (tag),
  INDEX idx_hour_tag (hour_bj_str, tag)
) ENGINE=InnoDB COMMENT '按小时+指标聚合统计';

-- ============================================================
-- Table 6: hourly_stats_by_host_mod — 按小时/主机/指标聚合
-- 来源: bigdata/outputs/核心结果表/hourly_stats_by_host_mod.csv
-- 对应前端: ChartData.regionalRanking (区域排行条形图)
-- ============================================================
CREATE TABLE IF NOT EXISTS hourly_stats_by_host_mod (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  hour_bj_str  VARCHAR(19)     NOT NULL            COMMENT '北京时间小时（YYYY-MM-DD HH:00:00）',
  hostid       VARCHAR(16)     NOT NULL            COMMENT '主机ID',
  `type`       VARCHAR(8)      NOT NULL            COMMENT '资源类型: disk / pref',
  `mod`        VARCHAR(32)     NOT NULL            COMMENT '指标代码',
  tag          VARCHAR(64)     NOT NULL            COMMENT '指标分类标签',
  avg_value    DOUBLE          DEFAULT NULL        COMMENT '平均值',
  max_value    DOUBLE          DEFAULT NULL        COMMENT '最大值',
  min_value    DOUBLE          DEFAULT NULL        COMMENT '最小值',
  median_value DOUBLE          DEFAULT NULL        COMMENT '中位数',
  sample_count INT UNSIGNED    DEFAULT 0           COMMENT '采样数',
  INDEX idx_hour (hour_bj_str),
  INDEX idx_hostid (hostid),
  INDEX idx_type_mod (`type`, `mod`),
  INDEX idx_hour_host (hour_bj_str, hostid)
) ENGINE=InnoDB COMMENT '按小时+主机+指标聚合统计';

-- ============================================================
-- Table 7: alarms — 告警记录
-- 对应前端: AlarmItem[] (告警滚动列表)
-- ============================================================
CREATE TABLE IF NOT EXISTS alarms (
  id      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  alarm_id VARCHAR(32)    NOT NULL UNIQUE       COMMENT '告警编号（ALM-XXXX）',
  `time`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '告警时间',
  area    VARCHAR(64)     NOT NULL              COMMENT '区域/主机',
  `level` ENUM('critical','major','minor','notice') NOT NULL COMMENT '告警级别',
  message VARCHAR(256)    NOT NULL              COMMENT '告警内容',
  acked   TINYINT(1)      NOT NULL DEFAULT 0    COMMENT '是否已确认',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_level (`level`),
  INDEX idx_time (`time`),
  INDEX idx_area (area)
) ENGINE=InnoDB COMMENT '告警记录表';

-- ============================================================
-- Table 8: radar_scores — 综合运行评分
-- 对应前端: ChartData.radar (雷达图)
-- ============================================================
CREATE TABLE IF NOT EXISTS radar_scores (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(32)  NOT NULL UNIQUE       COMMENT '评分维度（产能/质量/能效/稳定性/安全/交付）',
  value       DOUBLE       NOT NULL              COMMENT '评分（0-100）',
  max_score   DOUBLE       NOT NULL DEFAULT 100  COMMENT '满分',
  updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT '综合运行评分';

INSERT INTO radar_scores (name, value, max_score) VALUES
  ('产能',    88.0, 100),
  ('质量',    92.0, 100),
  ('能效',    79.0, 100),
  ('稳定性',  85.0, 100),
  ('安全',    94.0, 100),
  ('交付',    81.0, 100);

-- ============================================================
-- View: latest_metrics — 实时聚合指标视图
-- 供 API 快速查询当前快照
-- ============================================================
CREATE OR REPLACE VIEW latest_metrics AS
SELECT
  (SELECT COUNT(*) FROM host_detail) AS device_count,
  (SELECT COALESCE(AVG(CASE WHEN latest.cpu_usage >= 0 THEN 1 ELSE 0 END), 1) * 100
   FROM (
     SELECT DISTINCT t.hostid,
       FIRST_VALUE(t.value) OVER (PARTITION BY t.hostid ORDER BY t.datetime DESC) AS cpu_usage
     FROM tsar_raw t WHERE t.mod = 'cpu_usage'
   ) latest
  ) AS online_rate,
  (SELECT COALESCE(SUM(avg_value * sample_count), 0)
   FROM hourly_stats_by_metric
   WHERE hour_bj_str = (SELECT MAX(hour_bj_str) FROM hourly_stats_by_metric)
     AND tag IN ('disk_rw_sectors')
  ) AS daily_output,
  (SELECT COUNT(*) FROM alarms WHERE `time` >= DATE_SUB(NOW(), INTERVAL 24 HOUR)) AS alarm_count;