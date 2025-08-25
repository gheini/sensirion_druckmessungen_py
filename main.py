from pyvirtualbench import PyVirtualBench, DmmFunction
import virtual_bench as vb
import signal_plotter as sp
import time
import threading

vb_device_name = "VB8012-305A18E"
virtualBench = vb.VirtualBench(vb_device_name)

# Properties
signal_name = "mso_signal_2.csv"
meas_time_sec = 3.0

signal = virtualBench.record_ch1_signal_mso(duration_sec=meas_time_sec, sample_rate=100000.0, vertical_range=0.1, vertical_offset=0.0)
sp.plot_signal(signal, sample_rate=100000.0, title="MSO Signal", xlabel="Time (s)", ylabel="Amplitude")
path = "C:\Codes\sensirion_druckmessungen_py\Messdaten"
sp.save_signal_to_csv(f"{path}/{signal_name}", signal)
print(f"Signal saved to {path}/{signal_name}")

virtualBench.deinit()
