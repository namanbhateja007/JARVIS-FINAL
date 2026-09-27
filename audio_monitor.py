import pyaudiowpatch as pyaudio
import math
from array import array
import jarvis_ui


DEVICE_INDEX = 10


def start_audio_monitor():

    p = pyaudio.PyAudio()

    device = p.get_device_info_by_index(DEVICE_INDEX)

    print("Audio monitor using:", device["name"])

    stream = p.open(
        format=pyaudio.paInt16,
        channels=device["maxInputChannels"],
        rate=int(device["defaultSampleRate"]),
        input=True,
        input_device_index=DEVICE_INDEX,
        frames_per_buffer=1024
    )

    try:

        while True:

            data = stream.read(
                1024,
                exception_on_overflow=False
            )

            samples = array("h")
            samples.frombytes(data)

            if samples:

                square_sum = sum(
                    sample * sample
                    for sample in samples
                )

                rms = math.sqrt(
                    square_sum / len(samples)
                )

                # Convert raw RMS into 0.0 - 1.0
                level = min(rms / 12000, 1.0)

                jarvis_ui.set_audio_level(level)

    except KeyboardInterrupt:

        print("Audio monitor stopped.")

    finally:

        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    start_audio_monitor()