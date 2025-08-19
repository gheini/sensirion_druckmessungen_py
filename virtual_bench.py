from pyvirtualbench import PyVirtualBench, DmmFunction
import time
import threading
import os
import csv

class VirtualBench:
    def __init__(self, device_name):
        """
        Initialize the VirtualBench device for voltage measurement and power supply control.
        :param device_name: The name of the VirtualBench device (e.g., "MyVirtualBench").
        """
        self.device_name = device_name
        self.vb = None
        self.dmm = None
        self.ps = None  # Add the power supply attribute
        self._stop_flag = threading.Event()  # Add a stop flag
        self.cdaq = None
                
    def setup(self):
        """
        Setup the VirtualBench device and acquire the digital multimeter (DMM) and power supply (PS) resources.
        """
        self.vb = PyVirtualBench(self.device_name)
        self.dmm = self.vb.acquire_digital_multimeter()
        self.ps = self.vb.acquire_power_supply()  # Acquire the power supply resource        
        self.dio_channels = [self.device_name + '/dig/0', self.device_name + '/dig/1']              
        self.dio = self.vb.acquire_digital_input_output(",".join(self.dio_channels))
        self.do0_channel = self.dio_channels[0]  # DO1
        self.do1_channel = self.dio_channels[1]  # DO2

        self.set_channel("+6V", 5.0, 0.1)  # Initialize +6V channel
 
        print(f"VirtualBench device '{self.device_name}' initialized.")   
    
    
    def stop_voltage_controller(self):
        """
        Stop the voltage controller thread.
        """
        self._stop_flag.set()
        if self.controller_thread.is_alive():
            self.controller_thread.join()   
    
    def set_channel(self, channel: str, voltage_level: float, current_limit: float):
        """
        Set the voltage and current for the specified channel of the DC power supply.
        :param channel: The channel to configure ("+6V", "+25V", or "-25V").
        :param voltage_level: Voltage to set in volts.
        :param current_limit: Current to set in amperes.
        """
        if self.ps is None:
            raise Exception("Power supply not initialized. Call setup() first.")
        
        # Map the channel name to the correct VirtualBench channel identifier
        channel_map = {
            "+6V": "ps/+6V",
            "+25V": "ps/+25V",
            "-25V": "ps/-25V"
        }

        if channel not in channel_map:
            raise ValueError("Invalid channel. Use '+6V', '+25V', or '-25V'.")

        # Configure the specified channel
        vb_channel = channel_map[channel]
        self.ps.configure_voltage_output(vb_channel, voltage_level, current_limit)
        self.ps.enable_all_outputs(True)
        #print(f"Set {channel} channel to {voltage_level:.2f} V and {current_limit:.2f} A.")

    def read_digital_inputs(self, line_range="dio/0"):
        self.dio.configure_lines_direction(line_range, False)
        return self.dio.read_lines(line_range)
    
    def disable_all_outputs(self):
        """
        Disable all outputs of the DC power supply.
        """
        if self.ps is None:
            raise Exception("Power supply not initialized. Call setup() first.")
        
        self.ps.enable_all_outputs(False)
        print("All outputs of the DC power supply have been disabled.")
         
    def close(self):
        """
        Release the VirtualBench resources.
        """
        if self.dmm:
            self.dmm.release()
        if self.ps:  # Release the power supply resource
            self.ps.release()
        if self.vb:
            self.vb.release()
        print("VirtualBench resources released.")


# Example usage
if __name__ == "__main__":
    # Replace "VB8012-305A18E" with the actual name or serial number of your VirtualBench device
    vb_device_name = "VB8012-305A18E"

    try:
        vb = VirtualBench(vb_device_name)
        vb.setup()

        

    finally:
        vb.close()