import asyncio
from datetime import datetime

import RPi.GPIO as GPIO


class IRRemote:
    def __init__(self, port_number: int):
        self.port_number = port_number
        pass

    def start_listen_key_press(self, on_key_event): pass

    def waiting_for_key_pressed(self) -> str: pass

    def release(self): pass


class RaspIRRemote(IRRemote):
    def __init__(self, port_number: int):
        super().__init__(port_number)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(port_number, GPIO.IN)

    @staticmethod
    def convert_hex(bin_val):
        tmp_b2 = int(str(bin_val), 2)
        return hex(tmp_b2)

    @staticmethod
    def __convert_segments_to_binary__(segments):
        binary = 1  # Decoded binary command

        # Covers data to binary
        for (bit_type, time_length) in segments:
            # If segment is high bit (high is 1, low is 0)
            if bit_type == 1:
                # According to NEC protocol a gap of 1687.5 microseconds repesents a logical 1 so over 1000 should
                # make a big enough distinction
                # shift 1 bit to left
                binary *= 10
                # if time > 1 seconds bit should be odd
                if time_length > 1000:
                    binary += 1

        # Sometimes the binary has two rouge charactes on the end
        # Just get 34 bit
        if len(str(binary)) > 34:
            binary = int(str(binary)[:34])
        return binary

    def __ignore_waiting_bit__(self):
        value = GPIO.input(self.port_number)  # Current pin state

        while value:
            value = GPIO.input(self.port_number)
        return value

    def __read_signal_segments__(self):
        num1s = 0  # Number of consecutive 1s
        segments = []  # Pulses and their timings
        previous_value = 0  # The previous pin state
        value = self.__ignore_waiting_bit__()

        start_time = datetime.now()  # Sets start time

        while True:
            # Waits until change in state occurs
            if value != previous_value:
                now = datetime.now()
                pulse_length = now - start_time
                start_time = now

                # Adds pulse time to array (previous val acts as an alternating 1 / 0 to show whether time is the on
                # time or off time)
                segments.append((previous_value,
                                 pulse_length.microseconds))

            # Interrupts code if an extended high period is detected (End Of Command)
            if value:
                num1s += 1
            else:
                num1s = 0

            # Just need to get 10000 bit signal
            if num1s > 10000:
                break

            previous_value = value
            # Reads next bit signal
            value = GPIO.input(self.port_number)

        return segments

    def waiting_for_key_pressed(self) -> str:
        GPIO.wait_for_edge(self.port_number, GPIO.FALLING)
        signal_segments = self.__read_signal_segments__()
        key_binary = self.__convert_segments_to_binary__(signal_segments)
        key_hex = RaspIRRemote.convert_hex(key_binary)
        return key_hex

    def start_listen_key_press(self, on_key_event):
        def on_receive(channel):
            signal_segments = self.__read_signal_segments__()
            key_binary = self.__convert_segments_to_binary__(signal_segments)
            if key_binary.bit_length() < 16:
                return
            key_hex = RaspIRRemote.convert_hex(key_binary)
            on_key_event(key_hex)

        GPIO.add_event_detect(self.port_number, GPIO.FALLING, callback=on_receive, bouncetime=100)
        asyncio.get_event_loop().run_forever()

    def release(self):
        loop = asyncio.get_event_loop()
        loop.stop()
        loop.close()
        GPIO.cleanup()


class SimulateIRRemote(IRRemote):
    def __init__(self, port_number: int):
        super().__init__(port_number)

    def start_listen_key_press(self, on_key_event):
        raise RuntimeError("Not support")

    def waiting_for_key_pressed(self) -> str:
        raise RuntimeError("Not support")

    def release(self):
        raise RuntimeError("Not support")
