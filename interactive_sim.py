#!/usr/bin/env python3
"""
Interactive Queue Simulation CLI
Provides an interactive interface for running queue simulations
"""

import sys
import os
from queue_simulation import QueueSimulation
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time


class InteractiveQueueSimulator:
    """Interactive CLI for queue simulation"""

    def __init__(self):
        self.sim = None
        self.num_servers = 1
        self.arrival_rate = 1.0
        self.service_rate = 1.5
        self.max_time = 100.0
        self.max_customers = None

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        """Print application header"""
        print("=" * 60)
        print(" " * 15 + "待ち行列シミュレーション")
        print("=" * 60)
        print()

    def print_current_parameters(self):
        """Print current simulation parameters"""
        print("現在のパラメータ:")
        print(f"  サーバー数 (c):        {self.num_servers}")
        print(f"  到着率 (λ):           {self.arrival_rate:.2f} customers/時間単位")
        print(f"  サービス率 (μ):        {self.service_rate:.2f} customers/時間単位")
        print(f"  利用率 (ρ):           {self.arrival_rate / (self.num_servers * self.service_rate):.2f}")
        print(f"  シミュレーション時間:   {self.max_time if self.max_time else '無制限'}")
        print()

        if self.arrival_rate / (self.num_servers * self.service_rate) >= 1:
            print("⚠️  警告: 利用率 >= 1 (システムが不安定)")
            print()

    def display_main_menu(self):
        """Display main menu and get user choice"""
        self.clear_screen()
        self.print_header()
        self.print_current_parameters()

        print("メニュー:")
        print("  1. パラメータを設定")
        print("  2. シミュレーションを実行")
        print("  3. 統計を表示")
        print("  4. グラフを表示")
        print("  5. 理論値と比較")
        print("  6. リアルタイムシミュレーション")
        print("  0. 終了")
        print()

        choice = input("選択してください (0-6): ").strip()
        return choice

    def set_parameters(self):
        """Set simulation parameters"""
        self.clear_screen()
        self.print_header()
        print("パラメータ設定\n")

        try:
            num_servers = input(f"サーバー数 (現在: {self.num_servers}): ").strip()
            if num_servers:
                self.num_servers = int(num_servers)
                if self.num_servers < 1:
                    print("サーバー数は1以上である必要があります")
                    input("Enterキーを押して続行...")
                    return

            arrival_rate = input(f"到着率 λ (現在: {self.arrival_rate}): ").strip()
            if arrival_rate:
                self.arrival_rate = float(arrival_rate)
                if self.arrival_rate <= 0:
                    print("到着率は正の数である必要があります")
                    input("Enterキーを押して続行...")
                    return

            service_rate = input(f"サービス率 μ (現在: {self.service_rate}): ").strip()
            if service_rate:
                self.service_rate = float(service_rate)
                if self.service_rate <= 0:
                    print("サービス率は正の数である必要があります")
                    input("Enterキーを押して続行...")
                    return

            max_time = input(f"シミュレーション時間 (現在: {self.max_time}): ").strip()
            if max_time:
                self.max_time = float(max_time)

            print("\n✓ パラメータが更新されました")

        except ValueError:
            print("エラー: 無効な入力です")

        input("\nEnterキーを押して続行...")

    def run_simulation(self):
        """Run the simulation"""
        self.clear_screen()
        self.print_header()
        print("シミュレーション実行中...\n")

        self.sim = QueueSimulation(
            num_servers=self.num_servers,
            arrival_rate=self.arrival_rate,
            service_rate=self.service_rate
        )

        start_time = time.time()
        self.sim.run(max_time=self.max_time, max_customers=self.max_customers)
        elapsed_time = time.time() - start_time

        print(f"✓ シミュレーション完了 (実行時間: {elapsed_time:.2f}秒)")
        print(f"  {self.sim.customers_served} 人の顧客にサービスを提供しました")
        input("\nEnterキーを押して続行...")

    def display_statistics(self):
        """Display simulation statistics"""
        if not self.sim:
            self.clear_screen()
            self.print_header()
            print("エラー: まずシミュレーションを実行してください")
            input("\nEnterキーを押して続行...")
            return

        self.clear_screen()
        self.print_header()
        print("シミュレーション統計\n")

        stats = self.sim.get_statistics()

        print(f"到着した顧客数:              {stats['customers_arrived']}")
        print(f"サービスを受けた顧客数:      {stats['customers_served']}")
        print(f"現在の待ち行列の長さ:        {stats['current_queue_length']}")
        print(f"稼働中のサーバー数:          {stats['busy_servers']}/{self.num_servers}")
        print()
        print(f"平均待ち時間:                {stats['avg_waiting_time']:.4f} 時間単位")
        print(f"平均システム滞在時間:        {stats['avg_system_time']:.4f} 時間単位")
        print(f"平均待ち行列長:              {stats['avg_queue_length']:.4f} 人")
        print(f"最大待ち行列長:              {stats['max_queue_length']} 人")
        print(f"サーバー利用率:              {stats['server_utilization']:.2%}")

        input("\nEnterキーを押して続行...")

    def plot_results(self):
        """Plot simulation results"""
        if not self.sim:
            self.clear_screen()
            self.print_header()
            print("エラー: まずシミュレーションを実行してください")
            input("\nEnterキーを押して続行...")
            return

        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        # Plot queue length over time
        axes[0].plot(self.sim.time_history, self.sim.queue_length_history,
                     label='待ち行列の長さ', linewidth=1.5)
        axes[0].set_xlabel('時間')
        axes[0].set_ylabel('待ち行列の長さ')
        axes[0].set_title('時間経過に伴う待ち行列の長さ')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()

        # Plot customers in system over time
        axes[1].plot(self.sim.time_history, self.sim.customers_in_system_history,
                     label='システム内の顧客数', color='orange', linewidth=1.5)
        axes[1].axhline(y=self.num_servers, color='r', linestyle='--',
                       label=f'サーバー数 ({self.num_servers})', alpha=0.7)
        axes[1].set_xlabel('時間')
        axes[1].set_ylabel('システム内の顧客数')
        axes[1].set_title('時間経過に伴うシステム内の顧客数')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()

        plt.tight_layout()
        plt.show()

    def compare_theoretical(self):
        """Compare simulation results with theoretical values"""
        if not self.sim:
            self.clear_screen()
            self.print_header()
            print("エラー: まずシミュレーションを実行してください")
            input("\nEnterキーを押して続行...")
            return

        self.clear_screen()
        self.print_header()
        print("シミュレーション結果 vs 理論値\n")

        sim_stats = self.sim.get_statistics()
        theo_stats = self.sim.get_theoretical_statistics()

        if 'note' in theo_stats:
            print(f"⚠️  {theo_stats['note']}")
            input("\nEnterキーを押して続行...")
            return

        print(f"{'指標':<30} {'シミュレーション':<20} {'理論値':<20} {'誤差':<15}")
        print("-" * 85)

        # Utilization
        sim_util = sim_stats['server_utilization']
        theo_util = theo_stats['utilization']
        error_util = abs(sim_util - theo_util) / theo_util * 100 if theo_util != 0 else 0
        print(f"{'利用率 (ρ)':<30} {sim_util:<20.4f} {theo_util:<20.4f} {error_util:<15.2f}%")

        # Average time in queue
        sim_wq = sim_stats['avg_waiting_time']
        theo_wq = theo_stats['avg_time_in_queue']
        error_wq = abs(sim_wq - theo_wq) / theo_wq * 100 if theo_wq != 0 else 0
        print(f"{'平均待ち時間 (Wq)':<30} {sim_wq:<20.4f} {theo_wq:<20.4f} {error_wq:<15.2f}%")

        # Average time in system
        sim_w = sim_stats['avg_system_time']
        theo_w = theo_stats['avg_time_in_system']
        error_w = abs(sim_w - theo_w) / theo_w * 100 if theo_w != 0 else 0
        print(f"{'平均システム滞在時間 (W)':<30} {sim_w:<20.4f} {theo_w:<20.4f} {error_w:<15.2f}%")

        # Average queue length
        sim_lq = sim_stats['avg_queue_length']
        theo_lq = theo_stats['avg_customers_in_queue']
        error_lq = abs(sim_lq - theo_lq) / theo_lq * 100 if theo_lq != 0 else 0
        print(f"{'平均待ち行列長 (Lq)':<30} {sim_lq:<20.4f} {theo_lq:<20.4f} {error_lq:<15.2f}%")

        input("\nEnterキーを押して続行...")

    def realtime_simulation(self):
        """Run simulation with real-time visualization"""
        self.clear_screen()
        self.print_header()
        print("リアルタイムシミュレーション\n")
        print("グラフウィンドウを閉じるとメニューに戻ります\n")

        input("Enterキーを押してリアルタイムシミュレーションを開始...")

        # Create new simulation
        self.sim = QueueSimulation(
            num_servers=self.num_servers,
            arrival_rate=self.arrival_rate,
            service_rate=self.service_rate
        )

        # Run simulation step by step with visualization
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Schedule first arrival
        first_arrival_time = self.sim.generate_interarrival_time()
        from queue_simulation import Customer
        first_customer = Customer(id=self.sim.next_customer_id, arrival_time=first_arrival_time)
        self.sim.next_customer_id += 1
        self.sim.schedule_event(first_arrival_time, 'arrival', first_customer)

        times = []
        queue_lengths = []
        customers_in_system = []

        def update(frame):
            # Process events for a small time window
            target_time = frame * (self.max_time / 200)  # 200 frames total

            while self.sim.event_queue and self.sim.event_queue[0][0] <= target_time:
                event_time, event_type, data = self.sim.event_queue[0]

                if event_time > self.max_time:
                    break

                # Pop event
                import heapq
                heapq.heappop(self.sim.event_queue)

                # Update statistics
                time_delta = event_time - self.sim.last_event_time
                self.sim.update_statistics(time_delta)
                self.sim.current_time = event_time
                self.sim.last_event_time = event_time

                # Handle event
                if event_type == 'arrival':
                    self.sim.handle_arrival(data)
                elif event_type == 'departure':
                    self.sim.handle_departure(data)

                # Record data
                times.append(self.sim.current_time)
                queue_lengths.append(len(self.sim.waiting_queue))
                customers_in_system.append(len(self.sim.waiting_queue) + self.sim.busy_servers)

            # Update plots
            ax1.clear()
            ax2.clear()

            if times:
                ax1.plot(times, queue_lengths, 'b-', linewidth=1.5)
                ax1.set_xlabel('時間')
                ax1.set_ylabel('待ち行列の長さ')
                ax1.set_title(f'リアルタイム待ち行列シミュレーション (時刻: {self.sim.current_time:.2f})')
                ax1.grid(True, alpha=0.3)

                ax2.plot(times, customers_in_system, 'orange', linewidth=1.5)
                ax2.axhline(y=self.num_servers, color='r', linestyle='--', alpha=0.7)
                ax2.set_xlabel('時間')
                ax2.set_ylabel('システム内の顧客数')
                ax2.set_title(f'顧客数: {self.sim.customers_served} サービス済')
                ax2.grid(True, alpha=0.3)

            plt.tight_layout()

        anim = FuncAnimation(fig, update, frames=200, interval=50, repeat=False)
        plt.show()

    def run(self):
        """Main application loop"""
        while True:
            choice = self.display_main_menu()

            if choice == '0':
                print("\nプログラムを終了します...")
                sys.exit(0)
            elif choice == '1':
                self.set_parameters()
            elif choice == '2':
                self.run_simulation()
            elif choice == '3':
                self.display_statistics()
            elif choice == '4':
                self.plot_results()
            elif choice == '5':
                self.compare_theoretical()
            elif choice == '6':
                self.realtime_simulation()
            else:
                input("\n無効な選択です。Enterキーを押して続行...")


if __name__ == '__main__':
    app = InteractiveQueueSimulator()
    app.run()
