from pyvirtualbench import PyVirtualBench, DmmFunction
import virtual_bench as vb
import time
import threading

vb_device_name = "VB8012-305A18E"
virtualBench = vb.VirtualBench(vb_device_name)
virtualBench.setup()

periodTime = 600
iterations = 2

cdaq = cd.cDAQ9171(chassis_name="cDAQ1", module_name="Mod1")
channels = ["ai0", "ai1", "ai2"]
cdaq.start_continuous_temperature(channels=channels, excitation_current=100e-6, sample_rate=100.0)
time.sleep(1)  # Allow some time for the cDAQ to stabilize

csv_file_path = r"H:\tbheini\tbheini_10_SBB\Messungen\temperature_data_climate_-15_to_03_600s_02_dry.csv"
#csv_file_path = "test_01.csv"

# Start the temperature measurement thread
measurement_duration = 2 * periodTime * iterations  # Total duration for temperature measurement (in seconds)
interval = 0.01  # Time interval between measurements (in seconds)
measurement_thread = threading.Thread(target=cdaq.temperature_measurement_thread, args=(csv_file_path, measurement_duration, interval))
measurement_thread.start()

try:
    # Start measurement-thread
    for i in range(iterations):    
        virtualBench.start_voltage_controller(cdaq,Ttarget=-15.0, columns=0)
        time.sleep(periodTime)  
        virtualBench.stop_voltage_controller()
        virtualBench.start_voltage_controller(cdaq,Ttarget=3.0, columns=0)
        time.sleep(periodTime)  
        virtualBench.stop_voltage_controller()             

        
    # # Wait for the measurement thread to finish
    measurement_thread.join()

except KeyboardInterrupt:
    print("Measurement was cancelled by the user.")

finally:    
    cdaq.stop_measurement_thread(measurement_thread=measurement_thread)
    cdaq.stop_continuous_temperature()  
    virtualBench.disable_all_outputs()
    print("All outputs have been deactivated and the device has been shut down.")
    