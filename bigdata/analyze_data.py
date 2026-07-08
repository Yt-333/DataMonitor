#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大数据监控数据分析脚本
根据图片要求对 host_detail、mod_detail、disk_tsar、pref_tsar 进行分析
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime
import statistics

# ==================== 配置 ====================
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_tsv(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            rows.append(row)
    return rows

print("=" * 70)
print("大数据监控数据分析报告")
print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# 读取所有数据
hosts = read_tsv(os.path.join(DATA_DIR, 'host_detail.dat'))
mods = read_tsv(os.path.join(DATA_DIR, 'mod_detail.dat'))
disk_data = read_tsv(os.path.join(DATA_DIR, 'disk_tsar.dat'))
pref_data = read_tsv(os.path.join(DATA_DIR, 'pref_tsar.dat'))

print(f"\n数据加载完成:")
print(f"  主机数: {len(hosts)}")
print(f"  指标数: {len(mods)}")
print(f"  磁盘采集记录: {len(disk_data)}")
print(f"  性能采集记录: {len(pref_data)}")

# 构建辅助字典
host_dict = {h['hostid']: h for h in hosts}
mod_dict = {m['mod']: m for m in mods}

def safe_mean(vals):
    return statistics.mean(vals) if vals else 0

# ==================== 【1】各类资源指标数量统计 ====================
print("\n" + "=" * 70)
print("【1】各类资源（type）的指标数量统计")
print("=" * 70)

type_stats = defaultdict(list)
tag_stats = defaultdict(list)
for m in mods:
    type_stats[m['type']].append(m['mod'])
    tag_stats[m['tag']].append(m['mod'])

for t in sorted(type_stats):
    print(f"\n  资源类型: {t}")
    print(f"  指标数量: {len(type_stats[t])}")
    print(f"  指标列表: {', '.join(type_stats[t])}")

print(f"\n  按tag分类:")
for tag in sorted(tag_stats):
    print(f"    {tag}: {len(tag_stats[tag])}个")

# ==================== 【2】各机房服务器分布 ====================
print("\n" + "=" * 70)
print("【2】各机房（location1）的服务器分布")
print("=" * 70)

loc_stats = defaultdict(list)
model_by_loc = defaultdict(lambda: defaultdict(int))
for h in hosts:
    loc_stats[h['location1']].append(h)
    model_by_loc[h['location1']][h['model']] += 1

total = len(hosts)
for loc in sorted(loc_stats, key=lambda l: len(loc_stats[l]), reverse=True):
    hl = loc_stats[loc]
    pct = len(hl) / total * 100
    models = [f"{m}({c})" for m, c in sorted(model_by_loc[loc].items())]
    print(f"  {loc}: {len(hl)}台 ({pct:.1f}%) — {', '.join(models)}")
    for h in hl:
        print(f"    {h['hostid']} | {h['hostname']} | {h['owner']} | {h['model']} | {h['location2']}")

# ==================== 【3】各负责人服务器数量 ====================
print("\n" + "=" * 70)
print("【3】各负责人（owner）的服务器数量")
print("=" * 70)

owner_stats = defaultdict(list)
for h in hosts:
    owner_stats[h['owner']].append(h)

for owner in sorted(owner_stats, key=lambda o: len(owner_stats[o]), reverse=True):
    hl = owner_stats[owner]
    print(f"  {owner}: {len(hl)}台 → {', '.join(h['hostid'] for h in hl)}")

# ==================== 【4】各硬件型号数量统计 ====================
print("\n" + "=" * 70)
print("【4】各硬件型号（model）数量统计")
print("=" * 70)

model_stats = defaultdict(list)
for h in hosts:
    model_stats[h['model']].append(h)

for model in sorted(model_stats, key=lambda m: len(model_stats[m]), reverse=True):
    hl = model_stats[model]
    locs = set(h['location1'] for h in hl)
    owners = set(h['owner'] for h in hl)
    print(f"  {model}: {len(hl)}台 — 机房: {', '.join(sorted(locs))} | 负责人: {', '.join(sorted(owners))}")

# ==================== 【5】磁盘使用率TOP5 ====================
print("\n" + "=" * 70)
print("【5】磁盘使用率TOP5（sda_util平均值）")
print("=" * 70)

util_by_host = defaultdict(list)
for r in disk_data:
    if r['mod'] == 'sda_util':
        util_by_host[r['hostid']].append(float(r['value']))

util_stats = {}
for hid, vals in util_by_host.items():
    util_stats[hid] = {
        'avg': statistics.mean(vals),
        'max': max(vals),
        'min': min(vals),
        'cnt': len(vals)
    }

top5 = sorted(util_stats.items(), key=lambda x: x[1]['avg'], reverse=True)[:5]
print(f"\n  {'排名':<5} {'主机':<8} {'主机名':<28} {'负责人':<6} {'平均%':<10} {'最大%':<10} {'最小%':<10}")
print(f"  {'-'*82}")
for i, (hid, s) in enumerate(top5, 1):
    h = host_dict.get(hid, {})
    print(f"  {i:<5} {hid:<8} {h.get('hostname','N/A'):<28} {h.get('owner','N/A'):<6} {s['avg']:>8.2f}   {s['max']:>8.2f}   {s['min']:>8.2f}")

# 全量
print(f"\n  全部主机sda_util汇总:")
for hid in sorted(util_stats.keys()):
    s = util_stats[hid]
    print(f"    {hid}: avg={s['avg']:.2f}%, max={s['max']:.2f}%, min={s['min']:.2f}%, n={s['cnt']}")

# ==================== 【6】CPU使用率统计 ====================
print("\n" + "=" * 70)
print("【6】CPU使用率统计（cpu_usage平均值）")
print("=" * 70)

cpu_usage = defaultdict(list)
cpu_user = defaultdict(list)
cpu_sys = defaultdict(list)
cpu_idle = defaultdict(list)
for r in pref_data:
    hid, mod, val = r['hostid'], r['mod'], float(r['value'])
    if mod == 'cpu_usage': cpu_usage[hid].append(val)
    elif mod == 'cpu_user': cpu_user[hid].append(val)
    elif mod == 'cpu_sys': cpu_sys[hid].append(val)
    elif mod == 'cpu_idle': cpu_idle[hid].append(val)

cpu_stats = {}
for hid in cpu_usage:
    cpu_stats[hid] = {
        'usage': safe_mean(cpu_usage[hid]),
        'user': safe_mean(cpu_user.get(hid, [])),
        'sys': safe_mean(cpu_sys.get(hid, [])),
        'idle': safe_mean(cpu_idle.get(hid, [])),
    }

sorted_cpu = sorted(cpu_stats.items(), key=lambda x: x[1]['usage'], reverse=True)
print(f"\n  {'主机':<8} {'主机名':<28} {'负责人':<6} {'CPU使用%':<12} {'用户态%':<10} {'系统态%':<10} {'空闲%':<10}")
print(f"  {'-'*90}")
for hid, s in sorted_cpu:
    h = host_dict.get(hid, {})
    print(f"  {hid:<8} {h.get('hostname','N/A'):<28} {h.get('owner','N/A'):<6} {s['usage']:>8.2f}     {s['user']:>8.2f}   {s['sys']:>8.2f}   {s['idle']:>8.2f}")

all_cpu = [v for vals in cpu_usage.values() for v in vals]
print(f"\n  全局CPU统计: avg={statistics.mean(all_cpu):.2f}%, max={max(all_cpu):.2f}%, min={min(all_cpu):.2f}%, std={statistics.stdev(all_cpu):.2f}%")

# ==================== 【7】磁盘I/O等待时间 ====================
print("\n" + "=" * 70)
print("【7】磁盘I/O等待时间分析（sda~sde await平均值，单位ms）")
print("=" * 70)

await_data = defaultdict(lambda: defaultdict(list))
for r in disk_data:
    mod = r['mod']
    if mod.endswith('_await'):
        disk = mod.replace('_await', '')
        await_data[r['hostid']][disk].append(float(r['value']))

disks = ['sda','sdb','sdc','sdd','sde']
print(f"\n  {'主机':<8} ", end='')
for d in disks:
    print(f"{'':>2}{d}_await{'':>2}", end='  ')
print(f"{'主机avg':>10}")
print(f"  {'-'*85}")

for hid in sorted(await_data.keys()):
    h = host_dict.get(hid, {})
    print(f"  {hid:<8} ", end='')
    all_disk_vals = []
    for d in disks:
        vals = await_data[hid].get(d, [])
        if vals:
            avg = statistics.mean(vals)
            all_disk_vals.extend(vals)
            print(f"{avg:>8.2f}ms", end='  ')
        else:
            print(f"{'N/A':>10}", end='  ')
    host_avg = statistics.mean(all_disk_vals) if all_disk_vals else 0
    print(f"{host_avg:>8.2f}ms")

# 各磁盘全局统计
print(f"\n  各磁盘全局await统计:")
print(f"  {'磁盘':<10} {'avg(ms)':<12} {'max(ms)':<12} {'min(ms)':<12}")
for d in disks:
    all_vals = []
    for hid in await_data:
        all_vals.extend(await_data[hid].get(d, []))
    if all_vals:
        print(f"  {d:<10} {statistics.mean(all_vals):>8.2f}     {max(all_vals):>8.2f}     {min(all_vals):>8.2f}")

# ==================== 【8】网络带宽TOP5 ====================
print("\n" + "=" * 70)
print("【8】网络带宽使用TOP5（net_in+net_out平均值）")
print("=" * 70)

net_in = defaultdict(list)
net_out = defaultdict(list)
for r in pref_data:
    hid, mod, val = r['hostid'], r['mod'], float(r['value'])
    if mod == 'net_in': net_in[hid].append(val)
    elif mod == 'net_out': net_out[hid].append(val)

net_stats = {}
for hid in net_in:
    avg_in = safe_mean(net_in[hid])
    avg_out = safe_mean(net_out.get(hid, []))
    net_stats[hid] = {
        'in': avg_in, 'out': avg_out, 'total': avg_in + avg_out,
        'max_in': max(net_in[hid]), 'max_out': max(net_out.get(hid, [0]))
    }

top5_net = sorted(net_stats.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
print(f"\n  {'排名':<5} {'主机':<8} {'主机名':<28} {'负责人':<6} {'入站avg':<12} {'出站avg':<12} {'总带宽avg':<12}")
print(f"  {'-'*90}")
for i, (hid, s) in enumerate(top5_net, 1):
    h = host_dict.get(hid, {})
    print(f"  {i:<5} {hid:<8} {h.get('hostname','N/A'):<28} {h.get('owner','N/A'):<6} {s['in']:>8.2f}MB/s  {s['out']:>8.2f}MB/s  {s['total']:>8.2f}MB/s")

# 全量
print(f"\n  全部主机网络带宽汇总:")
print(f"  {'主机':<8} {'入站avg':<12} {'出站avg':<12} {'总带宽avg':<12} {'入站max':<12} {'出站max':<12}")
for hid in sorted(net_stats.keys()):
    s = net_stats[hid]
    print(f"  {hid:<8} {s['in']:>8.2f}MB/s  {s['out']:>8.2f}MB/s  {s['total']:>8.2f}MB/s  {s['max_in']:>8.2f}MB/s  {s['max_out']:>8.2f}MB/s")

# ==================== 【额外】内存使用统计 ====================
print("\n" + "=" * 70)
print("【附加】内存使用统计（各主机mem_used平均值）")
print("=" * 70)

mem_used = defaultdict(list)
mem_free = defaultdict(list)
for r in pref_data:
    hid, mod, val = r['hostid'], r['mod'], float(r['value'])
    if mod == 'mem_used': mem_used[hid].append(val)
    elif mod == 'mem_free': mem_free[hid].append(val)

print(f"\n  {'主机':<8} {'主机名':<28} {'负责人':<6} {'used(MB)':<12} {'free(MB)':<12} {'total(MB)':<12} {'使用率%':<10}")
print(f"  {'-'*95}")
mem_list = []
for hid in sorted(mem_used.keys()):
    avg_used = safe_mean(mem_used[hid])
    avg_free = safe_mean(mem_free.get(hid, []))
    total = avg_used + avg_free
    pct = avg_used / total * 100 if total > 0 else 0
    h = host_dict.get(hid, {})
    mem_list.append((hid, avg_used, avg_free, total, pct))
    print(f"  {hid:<8} {h.get('hostname','N/A'):<28} {h.get('owner','N/A'):<6} {avg_used:>8.0f}     {avg_free:>8.0f}     {total:>8.0f}     {pct:>6.1f}%")

# ==================== 【额外】系统负载统计 ====================
print("\n" + "=" * 70)
print("【附加】系统负载统计（load1/5/15平均值）")
print("=" * 70)

loads = defaultdict(lambda: {'load1':[],'load5':[],'load15':[]})
for r in pref_data:
    hid, mod, val = r['hostid'], r['mod'], float(r['value'])
    if mod in loads[hid]:
        loads[hid][mod].append(val)

print(f"\n  {'主机':<8} {'主机名':<28} {'load1':<10} {'load5':<10} {'load15':<10}")
print(f"  {'-'*60}")
for hid in sorted(loads.keys(), key=lambda h: statistics.mean(loads[h]['load1']) if loads[h]['load1'] else 0, reverse=True):
    h = host_dict.get(hid, {})
    l1 = safe_mean(loads[hid]['load1'])
    l5 = safe_mean(loads[hid]['load5'])
    l15 = safe_mean(loads[hid]['load15'])
    print(f"  {hid:<8} {h.get('hostname','N/A'):<28} {l1:>8.2f}   {l5:>8.2f}   {l15:>8.2f}")

# ==================== 完成 ====================
print("\n" + "=" * 70)
print("分析完成！")
print("=" * 70)
print(f"\n详细报告已保存到: {os.path.join(OUTPUT_DIR, 'analysis_report.txt')}")
sys.stdout.flush()
