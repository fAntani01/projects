import can
import time
import RPi.GPIO as GPIO
import usb.core

BITRATE = 125000
REVERSE_CAN_ID = 0x4F4
CHECK_INTERVAL = 0.1  # 100 ms

GPIO_PIN = 13  # BCM numbering (pin 11)


def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    GPIO.output(GPIO_PIN, GPIO.HIGH)


def reset_canable():
    dev = usb.core.find(idVendor=0x1D50, idProduct=0x606F)
    if dev:
        try:
            dev.reset()
            print("CANable USB device reset")
        except usb.core.USBError as e:
            print(f"USB reset failed: {e}")

def main():
    setup_gpio()

    bus = can.Bus(
        interface="gs_usb",
        bitrate=BITRATE,
        listen_only=True,
        channel=0
    )

    reverse_engaged = False

    print("Listening for reverse gear...")

    try:
        while True:
            msg = bus.recv(timeout=0.1)

            if msg and msg.arbitration_id == REVERSE_CAN_ID and len(msg.data) >= 2:
                new_state = (msg.data[1] == 0x01)

                if new_state != reverse_engaged:
                    reverse_engaged = new_state

                    if reverse_engaged:
                        
                        print("Reverse ENGAGED")
                        
                        GPIO.output(GPIO_PIN, GPIO.HIGH)

                    else:
                        print("Reverse DISENGAGED")
                        
                        GPIO.output(GPIO_PIN, GPIO.HIGH)

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.output(GPIO_PIN, GPIO.HIGH)
        GPIO.cleanup()
        bus.shutdown()
        reset_canable()

if __name__ == "__main__":
    main()
