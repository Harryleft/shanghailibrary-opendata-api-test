#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件统计脚本
统计 api_results 目录下的文件数量、大小等信息
"""

import os
import json
from pathlib import Path
from collections import defaultdict


def analyze_api_results():
    """分析 api_results 目录下的文件"""
    api_results_path = Path("api_results")

    if not api_results_path.exists():
        print("❌ api_results 目录不存在")
        return

    # 统计信息
    stats = {
        "total_files": 0,
        "total_size": 0,
        "file_types": defaultdict(int),
        "file_type_sizes": defaultdict(int),
        "categories": defaultdict(int),
        "largest_files": [],
        "files_by_category": defaultdict(list)
    }

    print("🔍 正在分析 api_results 目录...")
    print("=" * 60)

    # 遍历所有文件
    for file_path in api_results_path.rglob("*"):
        if file_path.is_file():
            # 基本统计
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            file_name = file_path.name

            stats["total_files"] += 1
            stats["total_size"] += file_size
            stats["file_types"][file_ext] += 1
            stats["file_type_sizes"][file_ext] += file_size

            # 分析文件类别（从文件名中提取）
            if file_name.startswith("[") and "]" in file_name:
                category = file_name.split("]")[0][1:]
                stats["categories"][category] += 1
                stats["files_by_category"][category].append(file_name)

            # 记录最大的文件
            stats["largest_files"].append((file_name, file_size))

    # 排序最大文件
    stats["largest_files"].sort(key=lambda x: x[1], reverse=True)
    stats["largest_files"] = stats["largest_files"][:10]  # 只保留前10个

    return stats


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def print_stats(stats):
    """打印统计结果"""
    print(f"📊 文件统计结果")
    print("=" * 60)
    print(f"📁 总文件数: {stats['total_files']}")
    print(f"💾 总大小: {format_size(stats['total_size'])}")
    print()

    # 文件类型统计
    print("📋 文件类型分布:")
    for ext, count in sorted(stats["file_types"].items(), key=lambda x: x[1], reverse=True):
        size = format_size(stats["file_type_sizes"][ext])
        ext_display = ext if ext else "(无扩展名)"
        print(f"  {ext_display:<10} {count:>3} 个文件  {size:>10}")
    print()

    # 分类统计
    print("🏷️  API 分类统计:")
    for category, count in sorted(stats["categories"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {category:<15} {count:>3} 个文件")
    print()

    # 最大文件
    print("📈 最大的文件 (前10个):")
    for i, (filename, size) in enumerate(stats["largest_files"], 1):
        print(f"  {i:>2}. {filename:<50} {format_size(size):>10}")
    print()

    # 详细分类信息
    print("📝 详细分类文件列表:")
    for category, files in sorted(stats["files_by_category"].items()):
        print(f"\n  [{category}] ({len(files)} 个文件):")
        for file in sorted(files):
            print(f"    - {file}")


def save_stats_to_json(stats):
    """将统计结果保存为JSON文件"""
    # 转换 defaultdict 为普通 dict
    json_stats = {
        "total_files": stats["total_files"],
        "total_size": stats["total_size"],
        "total_size_formatted": format_size(stats["total_size"]),
        "file_types": dict(stats["file_types"]),
        "file_type_sizes": {k: {"count": stats["file_types"][k],
                               "size": v,
                               "size_formatted": format_size(v)}
                           for k, v in stats["file_type_sizes"].items()},
        "categories": dict(stats["categories"]),
        "largest_files": [{"name": name, "size": size, "size_formatted": format_size(size)}
                         for name, size in stats["largest_files"]],
        "files_by_category": {k: list(v) for k, v in stats["files_by_category"].items()}
    }

    output_file = "api_results_stats.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_stats, f, ensure_ascii=False, indent=2)

    print(f"💾 统计结果已保存到: {output_file}")


def main():
    """主函数"""
    print("🚀 上海图书馆开放数据 API 测试项目文件统计")
    print("=" * 60)

    stats = analyze_api_results()
    if stats:
        print_stats(stats)
        save_stats_to_json(stats)

        # 给出优化建议
        print("\n💡 优化建议:")
        if stats["total_size"] > 10 * 1024 * 1024:  # 大于10MB
            print("  - 考虑将大文件添加到 .gitignore 中")
        if ".pdf" in stats["file_types"]:
            print("  - PDF 文件通常较大，建议不提交到 git 仓库")
        if stats["total_files"] > 100:
            print("  - 文件数量较多，考虑分类整理或压缩")


if __name__ == "__main__":
    main()
