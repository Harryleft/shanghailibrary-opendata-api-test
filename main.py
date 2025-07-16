#!/usr/bin/env python3
"""
上海图书馆开放数据API测试工具
主程序入口点
"""
import sys
from config import Colors
from api_lists import get_all_apis
from api_client import run_api_test


def print_banner():
    """打印程序横幅"""
    print(f"{Colors.INFO}")
    print("=" * 60)
    print("  上海图书馆开放数据API测试工具")
    print("  Shanghai Library Open Data API Test Tool")
    print("=" * 60)
    print(f"{Colors.ENDC}")

def run_tests(apis, category_name="所有"):
    """
    运行API测试

    Args:
        apis: API定义列表
        category_name: 类别名称
    """
    if not apis:
        print(f"{Colors.WARNING}没有找到要测试的API{Colors.ENDC}")
        return

    print(f"\n{Colors.INFO}开始测试 {category_name} API ({len(apis)} 个)...{Colors.ENDC}\n")

    results = []
    success_count = 0

    for i, api_def in enumerate(apis, 1):
        print(f"[{i}/{len(apis)}] ", end="")
        result = run_api_test(api_def)
        results.append(result)

        if result["success"]:
            success_count += 1

        print()  # 空行分隔

    # 打印总结
    print(f"{Colors.INFO}=" * 60)
    print(f"测试完成!")
    print(f"总数: {len(apis)}, 成功: {success_count}, 失败: {len(apis) - success_count}")
    print(f"成功率: {success_count / len(apis) * 100:.1f}%")
    print(f"={Colors.ENDC}" * 60)


def main():
    """主函数"""
    print_banner()

    # 默认测试所有API
    apis = get_all_apis()
    category_name = "所有"

    try:
        run_tests(apis, category_name)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}用户中断测试{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}发生错误: {e}{Colors.ENDC}")


if __name__ == "__main__":
    main()
