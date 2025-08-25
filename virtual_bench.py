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
        self.vb = PyVirtualBench(self.device_name)
        self.dmm = self.vb.acquire_digital_multimeter()
        self.ps = self.vb.acquire_power_supply()
        self.mso = self.vb.acquire_mixed_signal_oscilloscope()
        
        print(f"VirtualBench device '{self.device_name}' initialized.")

    def set_digital_io(self):
        """
        Setup the digital input/output channels and assign DO channel variables.
        """
        self.dio_channels = [self.device_name + '/dig/0', self.device_name + '/dig/1']
        self.dio = self.vb.acquire_digital_input_output(",".join(self.dio_channels))
        self.do0_channel = self.dio_channels[0]  # DO1
        self.do1_channel = self.dio_channels[1]  # DO2

    def set_ps_channel(self, channel: str, voltage_level: float, current_limit: float):
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

    def disable_ps_outputs(self):
        """
        Disable all outputs of the DC power supply.
        """
        if self.ps is None:
            raise Exception("Power supply not initialized. Call setup() first.")
        
        self.ps.enable_all_outputs(False)
        print("All outputs of the DC power supply have been disabled.")         

    def read_digital_inputs(self, line_range="dio/0"):
        self.dio.configure_lines_direction(line_range, False)
        return self.dio.read_lines(line_range)

    def measure_ch1_voltage(self, mode="DC"):
        """
        Measure the voltage using the DMM.
        :param mode: The mode of voltage measurement ("DC" or "AC").
        :return: Measured voltage in volts.
        """
        if self.dmm is None:
            raise Exception("DMM not initialized. Call setup() first.")
        
        if mode.upper() == "DC":
            self.dmm.configure_measurement(DmmFunction.DC_VOLTS, True, 10)
        elif mode.upper() == "AC":
            self.dmm.configure_measurement(DmmFunction.AC_VOLTS, True, 10)
        else:
            raise ValueError("Invalid mode. Use 'DC' or 'AC'.")
        
        voltage = self.dmm.read()        
        return voltage
    
    def record_ch1_signal_mso(self, duration_sec, sample_rate=100000.0, vertical_range=5.0, vertical_offset=0.0):
        """
        Record the analog signal on CH1 using the MSO (oscilloscope).
        :param duration_sec: Time in seconds to record the signal.
        :param sample_rate: Sampling rate in Hz (default: 1000 Hz).
        :param vertical_range: Vertical range in volts (default: 5V).
        :param vertical_offset: Vertical offset in volts (default: 0V).
        :return: List of measured voltage values.
        """
        if self.mso is None:
            raise Exception("MSO not initialized. Call setup() first.")

        channel = self.device_name + "/mso/1"
        print(f"Requesting channel: {channel}")
        print(f"Requested sample_rate: {sample_rate} Hz, duration: {duration_sec} s, total samples: {int(sample_rate * duration_sec)}")
        try:
            self.mso.configure_analog_channel(channel, True, vertical_range, vertical_offset, 1, 0)  # 1x probe, DC coupling
            self.mso.configure_timing(sample_rate, duration_sec, 1e-9, 0)  # 0 = REAL_TIME
            # actual_sample_rate, actual_acq_time, _, _ = self.mso.query_timing()
            # print(f"Actual sample_rate: {actual_sample_rate} Hz, acquisition time: {actual_acq_time} s, total samples: {int(actual_sample_rate * actual_acq_time)}")
            self.mso.configure_immediate_trigger()
            self.mso.run()
            analog_data, analog_data_stride, analog_t0, *_ = self.mso.read_analog_digital_u64()
            print(f"Returned analog_data_stride: {analog_data_stride}, number of samples: {len(analog_data)}")
            return list(analog_data)
        except Exception as e:
            print(f"Error during MSO acquisition: {e}")
            raise
    
    def record_ch2_signal_mso(self, duration_sec, sample_rate=100000.0, vertical_range=5.0, vertical_offset=0.0):
        """
        Record the analog signal on CH1 using the MSO (oscilloscope).
        :param duration_sec: Time in seconds to record the signal.
        :param sample_rate: Sampling rate in Hz (default: 1000 Hz).
        :param vertical_range: Vertical range in volts (default: 5V).
        :param vertical_offset: Vertical offset in volts (default: 0V).
        :return: List of measured voltage values.
        """
        if self.mso is None:
            raise Exception("MSO not initialized. Call setup() first.")

        channel = self.device_name + "/mso/2"
        print(f"Requesting channel: {channel}")
        print(f"Requested sample_rate: {sample_rate} Hz, duration: {duration_sec} s, total samples: {int(sample_rate * duration_sec)}")
        try:
            self.mso.configure_analog_channel(channel, True, vertical_range, vertical_offset, 1, 0)  # 1x probe, DC coupling
            self.mso.configure_timing(sample_rate, duration_sec, 1e-9, 0)  # 0 = REAL_TIME
            # actual_sample_rate, actual_acq_time, _, _ = self.mso.query_timing()
            # print(f"Actual sample_rate: {actual_sample_rate} Hz, acquisition time: {actual_acq_time} s, total samples: {int(actual_sample_rate * actual_acq_time)}")
            self.mso.configure_immediate_trigger()
            self.mso.run()
            analog_data, analog_data_stride, analog_t0, *_ = self.mso.read_analog_digital_u64()
            print(f"Returned analog_data_stride: {analog_data_stride}, number of samples: {len(analog_data)}")
            return list(analog_data)
        except Exception as e:
            print(f"Error during MSO acquisition: {e}")
            raise
        
    def record_ch12_signal_mso(self, duration_sec, sample_rate=100000.0, vertical_range=5.0, vertical_offset=0.0):
        """
        Record the analog signals on CH1 and CH2 using the MSO (oscilloscope).
        :param duration_sec: Time in seconds to record the signal.
        :param sample_rate: Sampling rate in Hz (default: 100000 Hz).
        :param vertical_range: Vertical range in volts (default: 5V).
        :param vertical_offset: Vertical offset in volts (default: 0V).
        :return: [signal_1, signal_2] as lists of measured voltage values.
        """
        if self.mso is None:
            raise Exception("MSO not initialized. Call setup() first.")

        channel1 = self.device_name + "/mso/1"
        channel2 = self.device_name + "/mso/2"
        print(f"Requesting channels: {channel1}, {channel2}")
        print(f"Requested sample_rate: {sample_rate} Hz, duration: {duration_sec} s, total samples: {int(sample_rate * duration_sec)}")
        try:
            self.mso.configure_analog_channel(channel1, True, vertical_range, vertical_offset, 1, 0)  # 1x probe, DC coupling
            self.mso.configure_analog_channel(channel2, True, vertical_range, vertical_offset, 1, 0)  # 1x probe, DC coupling
            self.mso.configure_timing(sample_rate, duration_sec, 1e-9, 0)  # 0 = REAL_TIME
            self.mso.configure_immediate_trigger()
            self.mso.run()
            analog_data, analog_data_stride, analog_t0, *_ = self.mso.read_analog_digital_u64()
            print(f"Returned analog_data_stride: {analog_data_stride}, number of samples: {len(analog_data)}")
            # Split the interleaved analog_data into two separate lists
            signal_1 = analog_data[0::analog_data_stride]
            signal_2 = analog_data[1::analog_data_stride]
            return [list(signal_1), list(signal_2)]
        except Exception as e:
            print(f"Error during MSO acquisition: {e}")
            raise
    
    def deinit(self):
        """
        Release the VirtualBench resources.
        """
        if self.dmm:
            self.dmm.release()
        if self.ps:
            self.ps.release()
        if hasattr(self, 'mso') and self.mso:
            self.mso.release()
        if self.vb:
            self.vb.release()
        print("VirtualBench resources released.")


# Example usage
if __name__ == "__main__":
    # Replace "VB8012-305A18E" with the actual name or serial number of your VirtualBench device
    vb_device_name = "VB8012-305A18E"

    try:
        vb = VirtualBench(vb_device_name)
        
        # Example: Record 2 seconds of data at 1000 Hz from CH1 (MSO)
        signal = vb.record_ch1_signal_mso(duration_sec=1.0, sample_rate=100000.0, vertical_range=5.0, vertical_offset=0.0)
        print(f"Recorded signal (MSO): {signal}")
        print(f"Size of recorded signal: {len(signal)} samples")

    finally:
        vb.deinit()