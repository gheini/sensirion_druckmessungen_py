from pyvirtualbench import PyVirtualBench, DmmFunction
import virtual_bench as vb
import signal_plotter as sp
import time
import threading

vb_device_name = "VB8012-305A18E"
virtualBench = vb.VirtualBench(vb_device_name)

signal = virtualBench.record_ch1_signal_mso(duration_sec=3.0, sample_rate=100000.0, vertical_range=0.2, vertical_offset=0.0)
print(f"Recorded signal (MSO): {signal}")
sp.plot_signal(signal, sample_rate=100000.0, title="MSO Signal", xlabel="Time (s)", ylabel="Amplitude")
path = "C:\Codes\sensirion_druckmessungen_py\Messdaten"
signalName = "mso_signal.csv"
sp.save_signal_to_csv(f"{path}/{signalName}", signal)

virtualBench.deinit()
