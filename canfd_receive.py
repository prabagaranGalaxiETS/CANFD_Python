import can

def receive_can_fd_messages():
    # Create a CAN bus instance
    bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', can_fd = True, bitrate=500000)
    
    # Create a listener that will handle the received messages
    class FDListener(can.Listener):
        def on_message_received(self, msg):
            if msg.is_fd:
                print(f"Received CAN FD message: {msg}")
        
        def stop(self):
            # Implement the abstract stop method
            pass

    listener = FDListener()

    # Create a notifier to dispatch received messages to the listener
    notifier = can.Notifier(bus, [listener])

    print("Listening for CAN FD messages...")
    
    try:
        while True:
            # Receive a message
            message = bus.recv(timeout=1)  # Timeout in seconds
            if message is not None and message.is_fd:
                print(f"Received CAN FD message: {message}")

    except KeyboardInterrupt:
        print("Stopped listening for CAN FD messages.")

    finally:
        # Cleanup
        notifier.stop()
        bus.shutdown()

if __name__ == "__main__":
    receive_can_fd_messages()
