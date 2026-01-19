#!/usr/bin/env python3
"""
待ち行列シミュレーション GUI
Tkinterを使用したグラフィカルユーザーインターフェース
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
from queue_simulation import QueueSimulation


class QueueSimulationGUI:
    """待ち行列シミュレーションのGUIアプリケーション"""

    def __init__(self, root):
        self.root = root
        self.root.title("待ち行列シミュレーション")
        self.root.geometry("1200x800")
        
        self.sim = None
        self.is_running = False
        
        # デフォルトパラメータ
        self.num_servers = tk.IntVar(value=1)
        self.arrival_rate = tk.DoubleVar(value=1.0)
        self.service_rate = tk.DoubleVar(value=1.5)
        self.max_time = tk.DoubleVar(value=100.0)
        self.max_customers = tk.IntVar(value=0)  # 0 = 無制限
        
        self.create_widgets()
        
    def create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # グリッドの設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # タイトル
        title_label = ttk.Label(
            main_frame, 
            text="待ち行列シミュレーション", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # パラメータ設定フレーム
        params_frame = ttk.LabelFrame(main_frame, text="パラメータ設定", padding="10")
        params_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # サーバー数
        ttk.Label(params_frame, text="サーバー数 (c):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(
            params_frame, 
            from_=1, 
            to=10, 
            textvariable=self.num_servers,
            width=10
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 到着率
        ttk.Label(params_frame, text="到着率 (λ):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.arrival_rate, width=10).grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=5
        )
        
        # サービス率
        ttk.Label(params_frame, text="サービス率 (μ):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.service_rate, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )
        
        # シミュレーション時間
        ttk.Label(params_frame, text="シミュレーション時間:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(params_frame, textvariable=self.max_time, width=10).grid(
            row=1, column=3, sticky=tk.W, padx=5, pady=5
        )
        
        # 利用率表示
        self.utilization_label = ttk.Label(
            params_frame, 
            text="利用率 (ρ): --", 
            font=("Arial", 10, "bold")
        )
        self.utilization_label.grid(row=2, column=0, columnspan=4, pady=5)
        self.update_utilization_display()
        
        # パラメータ変更時の利用率更新
        self.num_servers.trace('w', lambda *args: self.update_utilization_display())
        self.arrival_rate.trace('w', lambda *args: self.update_utilization_display())
        self.service_rate.trace('w', lambda *args: self.update_utilization_display())
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="シミュレーション実行", 
            command=self.run_simulation
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(
            button_frame, 
            text="リセット", 
            command=self.reset_simulation
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # 統計表示フレーム
        stats_frame = ttk.LabelFrame(main_frame, text="統計結果", padding="10")
        stats_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))
        stats_frame.columnconfigure(1, weight=1)
        
        self.stats_labels = {}
        stats_items = [
            ("到着した顧客数:", "customers_arrived"),
            ("サービスを受けた顧客数:", "customers_served"),
            ("平均待ち時間:", "avg_waiting_time", "{:.4f}"),
            ("平均システム滞在時間:", "avg_system_time", "{:.4f}"),
            ("平均待ち行列長:", "avg_queue_length", "{:.4f}"),
            ("最大待ち行列長:", "max_queue_length"),
            ("サーバー利用率:", "server_utilization", "{:.2%}"),
            ("現在の待ち行列長:", "current_queue_length"),
            ("稼働中のサーバー数:", "busy_servers"),
        ]
        
        for i, item in enumerate(stats_items):
            label_text = item[0]
            key = item[1]
            format_str = item[2] if len(item) > 2 else "{}"
            
            ttk.Label(stats_frame, text=label_text).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2
            )
            value_label = ttk.Label(stats_frame, text="--", font=("Arial", 9))
            value_label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self.stats_labels[key] = (value_label, format_str)
        
        # グラフフレーム
        graph_frame = ttk.Frame(main_frame)
        graph_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Matplotlibの図
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212)
        
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初期グラフ
        self.ax1.text(0.5, 0.5, 'シミュレーションを実行して結果を表示', 
                     ha='center', va='center', transform=self.ax1.transAxes,
                     fontsize=12, color='gray')
        self.ax2.text(0.5, 0.5, 'シミュレーションを実行して結果を表示', 
                     ha='center', va='center', transform=self.ax2.transAxes,
                     fontsize=12, color='gray')
        self.canvas.draw()
        
    def update_utilization_display(self):
        """利用率の表示を更新"""
        try:
            arrival = self.arrival_rate.get()
            service = self.service_rate.get()
            servers = self.num_servers.get()
            
            if service > 0 and servers > 0:
                rho = arrival / (servers * service)
                color = "red" if rho >= 1.0 else "black"
                self.utilization_label.config(
                    text=f"利用率 (ρ): {rho:.4f}",
                    foreground=color
                )
                if rho >= 1.0:
                    self.utilization_label.config(
                        text=f"利用率 (ρ): {rho:.4f} ⚠️ システムが不安定です",
                        foreground=color
                    )
            else:
                self.utilization_label.config(text="利用率 (ρ): --")
        except:
            self.utilization_label.config(text="利用率 (ρ): --")
    
    def validate_parameters(self):
        """パラメータの検証"""
        try:
            if self.num_servers.get() < 1:
                messagebox.showerror("エラー", "サーバー数は1以上である必要があります")
                return False
            
            if self.arrival_rate.get() <= 0:
                messagebox.showerror("エラー", "到着率は正の数である必要があります")
                return False
            
            if self.service_rate.get() <= 0:
                messagebox.showerror("エラー", "サービス率は正の数である必要があります")
                return False
            
            if self.max_time.get() <= 0:
                messagebox.showerror("エラー", "シミュレーション時間は正の数である必要があります")
                return False
            
            rho = self.arrival_rate.get() / (self.num_servers.get() * self.service_rate.get())
            if rho >= 1.0:
                result = messagebox.askyesno(
                    "警告", 
                    "利用率が1以上です。システムが不安定になる可能性があります。\n続行しますか？"
                )
                if not result:
                    return False
            
            return True
        except Exception as e:
            messagebox.showerror("エラー", f"無効なパラメータ: {str(e)}")
            return False
    
    def run_simulation(self):
        """シミュレーションを実行"""
        if not self.validate_parameters():
            return
        
        if self.is_running:
            messagebox.showwarning("警告", "シミュレーションは既に実行中です")
            return
        
        # 別スレッドでシミュレーションを実行
        self.is_running = True
        thread = threading.Thread(target=self._run_simulation_thread)
        thread.daemon = True
        thread.start()
    
    def _run_simulation_thread(self):
        """シミュレーション実行スレッド"""
        try:
            # シミュレーションの作成と実行
            self.sim = QueueSimulation(
                num_servers=self.num_servers.get(),
                arrival_rate=self.arrival_rate.get(),
                service_rate=self.service_rate.get()
            )
            
            max_customers = self.max_customers.get() if self.max_customers.get() > 0 else None
            self.sim.run(max_time=self.max_time.get(), max_customers=max_customers)
            
            # GUIを更新（メインスレッドで実行する必要がある）
            self.root.after(0, self.update_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("エラー", f"シミュレーションエラー: {str(e)}"))
        finally:
            self.is_running = False
    
    def update_results(self):
        """結果を表示"""
        if not self.sim:
            return
        
        # 統計を更新
        stats = self.sim.get_statistics()
        for key, (label, format_str) in self.stats_labels.items():
            if key in stats:
                value = stats[key]
                if isinstance(value, float):
                    label.config(text=format_str.format(value))
                else:
                    label.config(text=str(value))
        
        # グラフを更新
        self.ax1.clear()
        self.ax2.clear()
        
        if self.sim.time_history:
            # 待ち行列の長さ
            self.ax1.plot(
                self.sim.time_history, 
                self.sim.queue_length_history,
                label='待ち行列の長さ', 
                linewidth=1.5
            )
            self.ax1.set_xlabel('時間')
            self.ax1.set_ylabel('待ち行列の長さ')
            self.ax1.set_title('時間経過に伴う待ち行列の長さ')
            self.ax1.grid(True, alpha=0.3)
            self.ax1.legend()
            
            # システム内の顧客数
            self.ax2.plot(
                self.sim.time_history, 
                self.sim.customers_in_system_history,
                label='システム内の顧客数', 
                color='orange', 
                linewidth=1.5
            )
            self.ax2.axhline(
                y=self.num_servers.get(), 
                color='r', 
                linestyle='--',
                label=f'サーバー数 ({self.num_servers.get()})', 
                alpha=0.7
            )
            self.ax2.set_xlabel('時間')
            self.ax2.set_ylabel('システム内の顧客数')
            self.ax2.set_title('時間経過に伴うシステム内の顧客数')
            self.ax2.grid(True, alpha=0.3)
            self.ax2.legend()
        
        self.fig.tight_layout()
        self.canvas.draw()
        
        messagebox.showinfo("完了", "シミュレーションが完了しました")
    
    def reset_simulation(self):
        """シミュレーションをリセット"""
        self.sim = None
        self.is_running = False
        
        # 統計をリセット
        for key, (label, format_str) in self.stats_labels.items():
            label.config(text="--")
        
        # グラフをリセット
        self.ax1.clear()
        self.ax2.clear()
        self.ax1.text(0.5, 0.5, 'シミュレーションを実行して結果を表示', 
                     ha='center', va='center', transform=self.ax1.transAxes,
                     fontsize=12, color='gray')
        self.ax2.text(0.5, 0.5, 'シミュレーションを実行して結果を表示', 
                     ha='center', va='center', transform=self.ax2.transAxes,
                     fontsize=12, color='gray')
        self.canvas.draw()


def main():
    """メイン関数"""
    root = tk.Tk()
    app = QueueSimulationGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
