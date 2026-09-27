import pyaudiowpatch as pyaudio
import math
from array import array

p = pyaudio.PyAudio()

# Your WASAPI speaker loopback device
device_index = 10

device = p.get_device_info_by_index(device_index)

print("Using:", device["name"])
print("Channels:", device["maxInputChannels"])
print("Sample Rate:", device["defaultSampleRate"])

stream = p.open(
    format=pyaudio.paInt16,
    channels=device["maxInputChannels"],
    rate=int(device["defaultSampleRate"]),
    input=True,
    input_device_index=device_index,
    frames_per_buffer=1024
)

print("\nListening to speaker output...")
print("Play music or make JARVIS speak.\n")

try:
    while True:
        data = stream.read(1024, exception_on_overflow=False)

        samples = array("h")
        samples.frombytes(data)

        if samples:
            square_sum = sum(sample * sample for sample in samples)
            rms = math.sqrt(square_sum / len(samples))

            # Convert to a simple 0.0 → 1.0 level
            level = min(rms / 12000, 1.0)

            print(f"Volume: {level:.2f}", end="\r")

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()