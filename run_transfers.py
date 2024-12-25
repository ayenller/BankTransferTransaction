import os
import sys
import time
import argparse
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from app.main import execute_random_transfers

def run_timed_transfers(duration_minutes):
    """
    执行定时转账交易
    每秒执行5笔转账，持续指定的分钟数
    """
    # 计算需要执行的总次数
    transfers_per_second = 1
    total_seconds = duration_minutes * 60
    total_transfers = total_seconds * transfers_per_second
    
    # 打印开始信息
    print(f"\n开始执行定时转账...")
    print(f"执行时间: {duration_minutes} 分钟")
    print(f"执行频率: {transfers_per_second} 笔/秒")
    print(f"总计划执行: {total_transfers} 笔")
    print("\n" + "=" * 50 + "\n")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    current_second = start_time.second
    transfers_this_second = 0
    total_executed = 0
    
    while datetime.now() < end_time:
        now = datetime.now()
        
        # 如果进入新的一秒，重置计数器
        if now.second != current_second:
            current_second = now.second
            transfers_this_second = 0
        
        # 如果当前秒内的转账次数未达到限制，执行转账
        if transfers_this_second < transfers_per_second:
            execute_random_transfers(1)  # 每次执行1笔转账
            transfers_this_second += 1
            total_executed += 1
            
            # 计算剩余时间
            remaining_time = end_time - datetime.now()
            remaining_minutes = remaining_time.total_seconds() // 60
            remaining_seconds = remaining_time.total_seconds() % 60
            
            # 如果还未达到每秒限制，短暂等待
            if transfers_this_second < transfers_per_second:
                time.sleep(0.2)  # 等待200毫秒
        else:
            # 如果达到每秒限制，等待到下一秒
            time.sleep(0.1)
    
    # 打印结束统计
    print("\n" + "=" * 50)
    print("\n转账执行完成!")
    print(f"计划执行: {total_transfers} 笔")
    print(f"实际执行: {total_executed} 笔")
    print(f"总耗时: {(datetime.now() - start_time).total_seconds():.2f} 秒")

def main():
    parser = argparse.ArgumentParser(description='执行定时转账交易')
    parser.add_argument('duration', type=int, help='执行时间（分钟）')
    args = parser.parse_args()
    
    if args.duration <= 0:
        print("执行时间必须大于0分钟")
        return
    
    try:
        run_timed_transfers(args.duration)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n执行出错: {str(e)}")

if __name__ == "__main__":
    main() 