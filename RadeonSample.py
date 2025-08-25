import importlib
import os
import sys

def import_with_install(package, module_name=None):
    """
    パッケージをインポートし、必要であれば自動でインストールする関数。
    :param package: インストールするパッケージ名（pipで指定する名前）
    :param module_name: インポート時に使用するモジュール名（デフォルトはpackageと同じ）
    """
    module_name = module_name or package
    try:
        globals()[module_name] = importlib.import_module(module_name)
    except ImportError:
        os.system(f"{sys.executable} -m pip install {package}")
        globals()[module_name] = importlib.import_module(module_name)

import tkinter as tk
from threading import Thread
import time

import ADLXPybind as ADLX  # ADLXPybind.pydをインポート

class RadeonGPUApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radeon GPU Monitor")
        self.label = tk.Label(root, text="Radeon GPU Info: Detecting...", font=("Arial", 16))
        self.label.pack(pady=20)
        self.running = True
        # ADLXHelperで初期化
        self.adlx_helper = ADLX.ADLXHelper()
        self.ret = self.adlx_helper.Initialize()
        if self.ret != ADLX.ADLX_RESULT.ADLX_OK:
            print("ADLX initialization failed")
            return

        self.devices = self.detect_radeon()
        self.thread = Thread(target=self.update_info)
        self.thread.daemon = True
        self.thread.start()

    def detect_radeon(self):
        """Radeon GPUの検出"""
        try:
            # System Services取得
            system = self.adlx_helper.GetSystemServices()
            if system is None:
                print("Failed to get system services")
                self.adlx_helper.Terminate()
                return

            # Performance Monitoring Services取得
            perf_monitoring = system.GetPerformanceMonitoringServices()
            if perf_monitoring is None:
                print("Failed to get performance monitoring services")
                self.adlx_helper.Terminate()
                return
            
            # GPUリスト取得
            gpu_list = system.GetGPUs()
            if gpu_list is None:
                print("Failed to get GPU list")
                self.adlx_helper.Terminate()
                return

            # 最初のGPUでメトリクス取得（複数GPUの場合ループ）
            self.gpu = gpu_list[0]  # 最初のGPU
            metrics_support = perf_monitoring.GetSupportedGPUMetrics(self.gpu)
            if self.ret != ADLX.ADLX_RESULT.ADLX_OK:
                print("Failed to get metrics support")
                self.adlx_helper.Terminate()
                return

            # GPUUsageとVRAMUsageがサポートされているか確認
            if metrics_support.IsSupportedGPUUsage() and metrics_support.IsSupportedGPUVRAM():
                current_metrics = perf_monitoring.GetCurrentGPUMetrics(self.gpu)
                if self.ret == ADLX.ADLX_RESULT.ADLX_OK and current_metrics is not None:
                    gpu_usage = current_metrics.GPUUsage()  # GPU利用率 (%)
                    vram_usage = current_metrics.GPUVRAM()  # VRAM使用量 (MB)
                    print(f"GpuName: {self.gpu.Name()} ")

                    print(f"GPU Utilization: {gpu_usage}%")
                    print(f"VRAM Usage: {vram_usage} MB")
                    # Total VRAM取得
                    total_vram = self.gpu.TotalVRAM()  # IADLXGPUのVRAMメソッドで総VRAM取得 (MB)
                    print(f"Total VRAM: {total_vram} MB")
                    
            devices = {"gpuName":self.gpu.Name(),"GPUUsage":gpu_usage, "VramTotal":total_vram, "VramUsage":vram_usage}
            # return [device for device in devices if "AMD" in device.adapterName or "Radeon" in device.adapterName]
            return devices
        except Exception:
            return None
      
    def update_info(self):
        """GPU情報を更新"""
        while self.running:
            if self.devices:
                try:
                    self.devices = self.detect_radeon()
                    info = []
                    info.append(
                        f"gpuName: {self.devices["gpuName"]}\n"
                        f"GPUUsage: {self.devices["GPUUsage"]} %\n"
                        f"vram_total: {self.devices["VramTotal"]} MB\n"
                        f"vram_used: {self.devices["VramUsage"]} MB"
                    )
                    self.label.config(text="\n\n".join(info))
                except Exception as e:
                    self.label.config(text=f"Error: {e}\nEnsure AMD Adrenalin is installed")
            else:
                self.label.config(
                    text="Radeon GPU Not Detected\n"
                    "Ensure AMD Adrenalin is installed"
                )
            time.sleep(1)

    def on_closing(self):
        self.running = False
        # クリーンアップ
        self.adlx_helper.Terminate()
        print("ADLX terminated")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RadeonGPUApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()