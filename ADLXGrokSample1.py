#<!--
# Copyright (c) 2021 - 2025 Advanced Micro Devices, Inc. All rights reserved.
#
#-------------------------------------------------------------------------------------------------
#-->
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

import_with_install("ADLXPybind", "ADLXPybind")
import ADLXPybind as ADLX  # ADLXPybind.pydをインポート

def get_gpu_metrics():
    # ADLXHelperで初期化
    adlx_helper = ADLX.ADLXHelper()
    ret = adlx_helper.Initialize()
    if ret != ADLX.ADLX_RESULT.ADLX_OK:
        print("ADLX initialization failed")
        return

    # System Services取得
    system = adlx_helper.GetSystemServices()
    if system is None:
        print("Failed to get system services")
        adlx_helper.Terminate()
        return

    # Performance Monitoring Services取得
    perf_monitoring = system.GetPerformanceMonitoringServices()
    if perf_monitoring is None:
        print("Failed to get performance monitoring services")
        adlx_helper.Terminate()
        return
    
    # GPUリスト取得
    gpu_list = system.GetGPUs()
    if gpu_list is None:
        print("Failed to get GPU list")
        adlx_helper.Terminate()
        return

    # 最初のGPUでメトリクス取得（複数GPUの場合ループ）
    gpu = gpu_list[0]  # 最初のGPU
    metrics_support = perf_monitoring.GetSupportedGPUMetrics(gpu)
    if ret != ADLX.ADLX_RESULT.ADLX_OK:
        print("Failed to get metrics support")
        adlx_helper.Terminate()
        return

    # GPUUsageとVRAMUsageがサポートされているか確認
    if metrics_support.IsSupportedGPUUsage() and metrics_support.IsSupportedGPUVRAM():
        current_metrics = perf_monitoring.GetCurrentGPUMetrics(gpu)
        if ret == ADLX.ADLX_RESULT.ADLX_OK and current_metrics is not None:
            gpu_usage = current_metrics.GPUUsage()  # GPU利用率 (%)
            vram_usage = current_metrics.GPUVRAM()  # VRAM使用量 (MB)
            print(f"GpuName: {gpu.Name()} ")

            print(f"GPU Utilization: {gpu_usage}%")
            print(f"VRAM Usage: {vram_usage} MB")
            # Total VRAM取得
            total_vram = gpu.TotalVRAM()  # IADLXGPUのVRAMメソッドで総VRAM取得 (MB)
            print(f"Total VRAM: {total_vram} MB")
            
    # クリーンアップ
    adlx_helper.Terminate()
    print("ADLX terminated")

get_gpu_metrics()