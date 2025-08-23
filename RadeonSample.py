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

# 必要なライブラリをインポートまたはインストール
import_with_install("pyadl", "pyadl")
from pyadl import ADLManager

class RadeonGPUApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radeon GPU Monitor")
        self.label = tk.Label(root, text="Radeon GPU Info: Detecting...", font=("Arial", 16))
        self.label.pack(pady=20)
        self.running = True
        self.devices = self.detect_radeon()
        self.thread = Thread(target=self.update_info)
        self.thread.daemon = True
        self.thread.start()

    def detect_radeon(self):
        """Radeon GPUの検出"""
        if ADLManager is None:
            return None
        try:
            devices = ADLManager.getInstance().getDevices()
            return [device for device in devices if "AMD" in device.adapterName or "Radeon" in device.adapterName]
        except Exception:
            return None

    def update_info(self):
        """GPU情報を更新"""
        while self.running:
            if self.devices:
                try:
                    info = []
                    for device in self.devices:
                        clock = device.getCurrentEngineClock() or "N/A"
                        fan = device.getCurrentFanSpeed() or "N/A"
                        temp = device.getCurrentTemperature() or "N/A"
                        # VRAM情報（総量/使用量）
                        vram_total = "N/A"
                        vram_used = "N/A"
                        try:
                            vram_total = device.getCurrentVRAMUsage()['total'] / (1024 * 1024) if device.getCurrentVRAMUsage() else "N/A"
                            vram_used = device.getCurrentVRAMUsage()['used'] / (1024 * 1024) if device.getCurrentVRAMUsage() else "N/A"
                            vram_total = f"{vram_total:.2f} MB" if isinstance(vram_total, float) else vram_total
                            vram_used = f"{vram_used:.2f} MB" if isinstance(vram_used, float) else vram_used
                        except (AttributeError, KeyError, TypeError):
                            pass
                        info.append(
                            f"GPU: {device.adapterName}\n"
                            f"vram_total: {vram_total}\n"
                            f"vram_used: {vram_used}\n"
                            f"Clock: {clock} MHz\n"
                            f"Fan Speed: {fan} RPM\n"
                            f"Temperature: {temp} °C"
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
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RadeonGPUApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()