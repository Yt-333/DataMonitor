#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大数据监控数据分析脚本 - 备用版本
由于环境限制无法直接运行，此脚本可手动执行：
  python D:\OneDrive\桌面\bigdata\analyze_data.py
"""
import csv, os, statistics
from collections import defaultdict

DATA_DIR = r'D:\OneDrive\桌面\bigdata'
OUTPUT_DIR = r'D:\OneDrive\桌面\bigdata\output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def read_tsv(fp):
    rows = []
    with open(fp, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            rows.append(row)
    return rows

print("=" * 70)
print("大数据监控数据分析报告")
print("=" * 70)

hosts = read_tsv(os.path.join(DATA_DIR, 'host_detail.dat'))
mods = read_tsv(os.path.join(DATA_DIR, 'mod_detail.dat'))
disk_data = read_tsv(os.path.join(DATA_DIR, 'disk_tsar.dat'))
pref_data = read_tsv(os.path.join(DATA_DIR, 'pref_tsar.dat'))

print(f"\n数据加载完成:")
print(f"  主机数: {len(hosts)}")
print(f"  指标数: {len(mods)}")
print(f"  磁盘采集记录: {len(disk_data)}")
print(f"  性能采集记录: {len(pref_data)}")

host_dict = {h['hostid']: h for h in hosts}
mod_dict = {m['mod']: m for m in mods}

# [1] 各类资源指标数量统计
print("\n" + "=" * 70)
print("【1】各类资源(type)的指标数量统计")
print("=" * 70)
type_stats = defaultdict(lambda: {'count': 0, 'mods': []})
for m in mods:
    type_stats[m['type']]['count'] += 1
    type_stats[m['type']]['mods'].append(m['mod'])
for t, info in sorted(type_stats.items()):
    print(f"\n  资源类型: {t}")
    print(f"  指标数量: {info['count']}")
    print(f"  指标列表: {', '.join(info['mods'])}")
tag_stats = defaultdict(list)
for m in mods:
    tag_stats[m['tag']].append(m['mod'])
print(f"\n  按tag分类的指标数量:")
for tag, mod_list in sorted(tag_stats.items()):
    print(f"    {tag}: {len(mod_list)} 个指标")

# [2] 各机房服务器分布
print("\n" + "=" * 70)
print("【2】各机房(location1)的服务器分布统计")
print("=" * 70)
location_stats = defaultdict(int)
for h in hosts:
    location_stats[h['location1']] += 1
print(f"\n  {'机房':<10} {'服务器数量':<12} {'占比'}")
print(f"  {'-'*30}")
total_hosts = len(hosts)
for loc, count in sorted(location_stats.items()):
    pct = count / total_hosts * 100
    bar = chr(9608) * count
    print(f"  {loc:<10} {count:<12} {pct:5.1f}%  {bar}")
print(f"\n  各机房机柜明细:")
for h in hosts:
    print(f"    {h['location1']} - {h['location2']}: {h['hostid']} ({h['hostname']})")

# [3] 各负责人服务器数量
print("\n" + "=" * 70)
print("【3】各负责人(owner)的服务器数量统计")
print("=" * 70)
owner_stats = defaultdict(list)
for h in hosts:
    owner_stats[h['owner']].append(h)
sorted_owners = sorted(owner_stats.items(), key=lambda x: len(x[1]), reverse=True)
print(f"\n  {'负责人':<8} {'服务器数量':<12} {'服务器列表'}")
print(f"  {'-'*60}")
for owner, host_list in sorted_owners:
    host_ids = [h['hostid'] for h in host_list]
    print(f"  {owner:<8} {len(host_list):<12} {', '.join(host_ids)}")

# [4] 硬件型号统计
print("\n" + "=" * 70)
print("【4】各硬件型号(model)数量统计")
print("=" * 70)
model_stats = defaultdict(list)
for h in hosts:
    model_stats[h['model']].append(h)
sorted_models = sorted(model_stats.items(), key=lambda x: len(x[1]), reverse=True)
print(f"\n  {'硬件型号':<18} {'数量':<8} {'所在机房'}")
print(f"  {'-'*50}")
for model, host_list in sorted_models:
    locations = set(h['location1'] for h in host_list)
    print(f"  {model:<18} {len(host_list):<8} {', '.join(sorted(locations))}")

# [5] 磁盘使用率TOP5
print("\n" + "=" * 70)
print("【5】磁盘使用率TOP5(按sda_util平均值排序)")
print("=" * 70)
disk_util_by_host = defaultdict(list)
for row in disk_data:
    if row['mod'] == 'sda_util':
        disk_util_by_host[row['hostid']].append(float(row['value']))
host_avg_util = {}
for hostid, values in disk_util_by_host.items():
    host_avg_util[hostid] = {'avg': statistics.mean(values), 'max': max(values), 'min': min(values), 'count': len(values)}
top5_util = sorted(host_avg_util.items(), key=lambda x: x[1]['avg'], reverse=True)[:5]
print(f"\n  {'排名':<6} {'主机ID':<10} {'主机名':<30} {'负责人':<8} {'平均使用率':<12} {'最大值':<10} {'最小值':<10}")
print(f"  {'-'*90}")
for rank, (hostid, stats) in enumerate(top5_util, 1):
    host = host_dict.get(hostid, {})
    print(f"  {rank:<6} {hostid:<10} {host.get('hostname','N/A'):<30} {host.get('owner','N/A'):<8} {stats['avg']:>8.2f}%    {stats['max']:>8.2f}%   {stats['min']:>8.2f}%")
print(f"\n  全部主机sda_util汇总:")
print(f"  {'主机ID':<10} {'平均使用率':<12} {'最大值':<10} {'最小值':<10} {'采样数':<8}")
print(f"  {'-'*55}")
for hostid in sorted(host_avg_util.keys()):
    s = host_avg_util[hostid]
    print(f"  {hostid:<10} {s['avg']:>8.2f}%    {s['max']:>8.2f}%   {s['min']:>8.2f}%   {s['count']:<8}")

# [6] CPU使用率统计
print("\n" + "=" * 70)
print("【6】CPU使用率统计(各主机cpu_usage平均值)")
print("=" * 70)
cpu_by_host = defaultdict(list)
cpu_user_by_host = defaultdict(list)
cpu_sys_by_host = defaultdict(list)
cpu_idle_by_host = defaultdict(list)
for row in pref_data:
    hostid = row['hostid']; val = float(row['value'])
    if row['mod'] == 'cpu_usage': cpu_by_host[hostid].append(val)
    elif row['mod'] == 'cpu_user': cpu_user_by_host[hostid].append(val)
    elif row['mod'] == 'cpu_sys': cpu_sys_by_host[hostid].append(val)
    elif row['mod'] == 'cpu_idle': cpu_idle_by_host[hostid].append(val)
host_cpu_stats = {}
for hostid in cpu_by_host:
    vals = cpu_by_host[hostid]
    host_cpu_stats[hostid] = {
        'avg_usage': statistics.mean(vals), 'max_usage': max(vals), 'min_usage': min(vals),
        'avg_user': statistics.mean(cpu_user_by_host.get(hostid, [0])),
        'avg_sys': statistics.mean(cpu_sys_by_host.get(hostid, [0])),
        'avg_idle': statistics.mean(cpu_idle_by_host.get(hostid, [0])),
    }
sorted_cpu = sorted(host_cpu_stats.items(), key=lambda x: x[1]['avg_usage'], reverse=True)
print(f"\n  {'主机ID':<10} {'主机名':<30} {'负责人':<8} {'CPU使用率':<12} {'用户态':<10} {'系统态':<10} {'空闲率':<10}")
print(f"  {'-'*95}")
for hostid, stats in sorted_cpu:
    host = host_dict.get(hostid, {})
    print(f"  {hostid:<10} {host.get('hostname','N/A'):<30} {host.get('owner','N/A'):<8} {stats['avg_usage']:>8.2f}%   {stats['avg_user']:>8.2f}%  {stats['avg_sys']:>8.2f}%  {stats['avg_idle']:>8.2f}%")
all_cpu_vals = [v for vals in cpu_by_host.values() for v in vals]
print(f"\n  全局CPU使用率统计:")
print(f"    平均: {statistics.mean(all_cpu_vals):.2f}%")
print(f"    最大: {max(all_cpu_vals):.2f}%")
print(f"    最小: {min(all_cpu_vals):.2f}%")
print(f"    标准差: {statistics.stdev(all_cpu_vals):.2f}%")

# [7] 磁盘I/O等待时间
print("\n" + "=" * 70)
print("【7】磁盘I/O等待时间分析(sda~sde的await平均值)")
print("=" * 70)
await_by_host_disk = defaultdict(lambda: defaultdict(list))
for row in disk_data:
    if row['mod'].endswith('_await'):
        disk_name = row['mod'].replace('_await', '')
        await_by_host_disk[row['hostid']][disk_name].append(float(row['value']))
print(f"\n  {'主机ID':<10} {'sda_await':<12} {'sdb_await':<12} {'sdc_await':<12} {'sdd_await':<12} {'sde_await':<12} {'主机平均':<12}")
print(f"  {'-'*78}")
for hostid in sorted(await_by_host_disk.keys()):
    host = host_dict.get(hostid, {})
    disk_avgs = {}; all_vals = []
    for disk in ['sda','sdb','sdc','sdd','sde']:
        vals = await_by_host_disk[hostid].get(disk, [])
        if vals:
            avg = statistics.mean(vals); disk_avgs[disk] = avg; all_vals.extend(vals)
        else:
            disk_avgs[disk] = None
    host_avg = statistics.mean(all_vals) if all_vals else 0
    parts = [hostid]
    for disk in ['sda','sdb','sdc','sdd','sde']:
        parts.append(f"{disk_avgs[disk]:>8.2f}ms  " if disk_avgs.get(disk) is not None else f"{'N/A':>12}")
    parts.append(f"{host_avg:>8.2f}ms")
    print(f"  {parts[0]:<10} {parts[1]:<12} {parts[2]:<12} {parts[3]:<12} {parts[4]:<12} {parts[5]:<12} {parts[6]:<12}")
print(f"\n  各磁盘全局await统计:")
print(f"  {'磁盘':<10} {'平均':<12} {'最大':<12} {'最小':<12}")
print(f"  {'-'*40}")
for disk in ['sda','sdb','sdc','sdd','sde']:
    all_disk_vals = []
    for hostid in await_by_host_disk:
        all_disk_vals.extend(await_by_host_disk[hostid].get(disk, []))
    if all_disk_vals:
        print(f"  {disk:<10} {statistics.mean(all_disk_vals):>8.2f}ms  {max(all_disk_vals):>8.2f}ms  {min(all_disk_vals):>8.2f}ms")

# [8] 网络带宽TOP5
print("\n" + "=" * 70)
print("【8】网络带宽使用TOP5(按net_in+net_out总带宽平均值排序)")
print("=" * 70)
net_in_by_host = defaultdict(list); net_out_by_host = defaultdict(list)
for row in pref_data:
    hostid = row['hostid']; val = float(row['value'])
    if row['mod'] == 'net_in': net_in_by_host[hostid].append(val)
    elif row['mod'] == 'net_out': net_out_by_host[hostid].append(val)
host_net_stats = {}
for hostid in net_in_by_host:
    in_vals = net_in_by_host[hostid]; out_vals = net_out_by_host.get(hostid, [0])
    avg_in = statistics.mean(in_vals); avg_out = statistics.mean(out_vals) if out_vals else 0
    host_net_stats[hostid] = {'avg_in': avg_in, 'avg_out': avg_out, 'avg_total': avg_in + avg_out, 'max_in': max(in_vals), 'max_out': max(out_vals) if out_vals else 0}
top5_net = sorted(host_net_stats.items(), key=lambda x: x[1]['avg_total'], reverse=True)[:5]
print(f"\n  {'排名':<6} {'主机ID':<10} {'主机名':<30} {'负责人':<8} {'平均入站':<12} {'平均出站':<12} {'总带宽':<12}")
print(f"  {'-'*95}")
for rank, (hostid, stats) in enumerate(top5_net, 1):
    host = host_dict.get(hostid, {})
    print(f"  {rank:<6} {hostid:<10} {host.get('hostname','N/A'):<30} {host.get('owner','N/A'):<8} {stats['avg_in']:>8.2f}MB/s  {stats['avg_out']:>8.2f}MB/s  {stats['avg_total']:>8.2f}MB/s")
print(f"\n  全部主机网络带宽汇总:")
print(f"  {'主机ID':<10} {'平均入站':<12} {'平均出站':<12} {'总带宽':<12} {'最大入站':<12} {'最大出站':<12}")
print(f"  {'-'*65}")
for hostid in sorted(host_net_stats.keys()):
    s = host_net_stats[hostid]
    print(f"  {hostid:<10} {s['avg_in']:>8.2f}MB/s  {s['avg_out']:>8.2f}MB/s  {s['avg_total']:>8.2f}MB/s  {s['max_in']:>8.2f}MB/s  {s['max_out']:>8.2f}MB/s")

# [9] 内存使用统计
print("\n" + "=" * 70)
print("【9】内存使用统计(各主机mem_used平均值)")
print("=" * 70)
mem_by_host = defaultdict(list); mem_free_by_host = defaultdict(list)
for row in pref_data:
    hostid = row['hostid']; val = float(row['value'])
    if row['mod'] == 'mem_used': mem_by_host[hostid].append(val)
    elif row['mod'] == 'mem_free': mem_free_by_host[hostid].append(val)
mem_stats = []
for hostid in mem_by_host:
    used_vals = mem_by_host[hostid]; free_vals = mem_free_by_host.get(hostid, [0])
    avg_used = statistics.mean(used_vals); avg_free = statistics.mean(free_vals) if free_vals else 0
    mem_stats.append((hostid, avg_used, avg_free))
mem_stats.sort(key=lambda x: x[1], reverse=True)
print(f"\n  {'主机ID':<10} {'主机名':<30} {'负责人':<8} {'已用内存(MB)':<14} {'空闲内存(MB)':<14} {'总内存(MB)':<14} {'使用率':<10}")
print(f"  {'-'*105}")
for hostid, avg_used, avg_free in mem_stats:
    host = host_dict.get(hostid, {})
    total_mem = avg_used + avg_free; usage_pct = (avg_used / total_mem * 100) if total_mem > 0 else 0
    print(f"  {hostid:<10} {host.get('hostname','N/A'):<30} {host.get('owner','N/A'):<8} {avg_used:>10.0f}     {avg_free:>10.0f}     {total_mem:>10.0f}     {usage_pct:>6.1f}%")

# [10] 系统负载统计
print("\n" + "=" * 70)
print("【10】系统负载统计(各主机load1/load5/load15平均值)")
print("=" * 70)
load_by_host = defaultdict(lambda: {'load1': [], 'load5': [], 'load15': []})
for row in pref_data:
    hostid = row['hostid']; mod = row['mod']
    if mod in ('load1', 'load5', 'load15'):
        load_by_host[hostid][mod].append(float(row['value']))
load_stats = []
for hostid, loads in load_by_host.items():
    avg1 = statistics.mean(loads['load1']) if loads['load1'] else 0
    avg5 = statistics.mean(loads['load5']) if loads['load5'] else 0
    avg15 = statistics.mean(loads['load15']) if loads['load15'] else 0
    load_stats.append((hostid, avg1, avg5, avg15))
load_stats.sort(key=lambda x: x[1], reverse=True)
print(f"\n  {'主机ID':<10} {'主机名':<30} {'负责人':<8} {'load1':<10} {'load5':<10} {'load15':<10}")
print(f"  {'-'*80}")
for hostid, l1, l5, l15 in load_stats:
    host = host_dict.get(hostid, {})
    print(f"  {hostid:<10} {host.get('hostname','N/A'):<30} {host.get('owner','N/A'):<8} {l1:>8.2f}   {l5:>8.2f}   {l15:>8.2f}")

# [11] 磁盘读写性能统计
print("\n" + "=" * 70)
print("【11】磁盘读写性能统计(各主机sda读写扇区数平均值)")
print("=" * 70)
disk_rw_by_host = defaultdict(lambda: {'read': [], 'write': []})
for row in disk_data:
    hostid = row['hostid']; mod = row['mod']; val = float(row['value'])
    if mod == 'sda_read': disk_rw_by_host[hostid]['read'].append(val)
    elif mod == 'sda_write': disk_rw_by_host[hostid]['write'].append(val)
rw_stats = []
for hostid, rw in disk_rw_by_host.items():
    avg_read = statistics.mean(rw['read']) if rw['read'] else 0
    avg_write = statistics.mean(rw['write']) if rw['write'] else 0
    rw_stats.append((hostid, avg_read, avg_write, avg_read + avg_write))
rw_stats.sort(key=lambda x: x[3], reverse=True)
print(f"\n  {'主机ID':<10} {'主机名':<30} {'负责人':<8} {'读(sectors/s)':<14} {'写(sectors/s)':<14} {'总IO':<14}")
print(f"  {'-'*95}")
for hostid, avg_read, avg_write, total in rw_stats:
    host = host_dict.get(hostid, {})
    print(f"  {hostid:<10} {host.get('hostname','N/A'):<30} {host.get('owner','N/A'):<8} {avg_read:>10.0f}     {avg_write:>10.0f}     {total:>10.0f}")

report_path = os.path.join(OUTPUT_DIR, 'analysis_report.txt')
print(f"\n\n报告已输出到: {report_path}")
print("\n" + "=" * 70)
print("分析完成!")
print("=" * 70)
