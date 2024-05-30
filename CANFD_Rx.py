from PCANBasic import *
import os
import sys
from ctypes import c_ulonglong

class CANFDReader:
    # Defines
    #region

    # Sets the PCANHandle (Hardware Channel)
    PcanHandle = PCAN_USBBUS1

    # Sets the bitrate for CAN FD devices.
    # Nominal Bitrate: 500 kbps, Data Bitrate: 2 Mbps
    # Prescaler: 5, Sample Point: 75%
    BitrateFD = b"f_clock_mhz=20, nom_brp=5, nom_tseg1=13, nom_tseg2=2, nom_sjw=2, data_brp=1, data_tseg1=7, data_tseg2=2, data_sjw=1"

    #endregion

    def __init__(self):
        """
        Initializes the CAN FD reader
        """
        self.m_objPCANBasic = PCANBasic()
        self.initialize_channel()

    def initialize_channel(self):
        """
        Initializes the PCAN channel with CAN FD settings
        """
        # Initialize the CAN FD channel
        stsResult = self.m_objPCANBasic.InitializeFD(self.PcanHandle, self.BitrateFD)
        if stsResult != PCAN_ERROR_OK:
            print("Cannot initialize. Please check the defines in the code.")
            self.show_status(stsResult)
            sys.exit()

        print("Successfully initialized.")
        
        # Set message filter to allow all messages
        stsResult = self.m_objPCANBasic.SetValue(self.PcanHandle, PCAN_MESSAGE_FILTER, PCAN_FILTER_CLOSE)
        if stsResult != PCAN_ERROR_OK:
            print("Cannot set message filter to close.")
            self.show_status(stsResult)
            sys.exit()

        stsResult = self.m_objPCANBasic.SetValue(self.PcanHandle, PCAN_MESSAGE_FILTER, PCAN_FILTER_OPEN)
        if stsResult != PCAN_ERROR_OK:
            print("Cannot set message filter to open.")
            self.show_status(stsResult)
            sys.exit()

    def read_messages(self):
        """
        Reads CAN FD messages from the bus
        """
        while True:
            stsResult = self.m_objPCANBasic.ReadFD(self.PcanHandle)
            if stsResult[0] != PCAN_ERROR_QRCVEMPTY:
                if stsResult[0] == PCAN_ERROR_OK:
                    self.process_message_fd(stsResult[1], stsResult[2])
                else:
                    self.show_status(stsResult[0])
            else:
                print("No messages received. Waiting...")

    def process_message_fd(self, msg, timestamp):
        """
        Processes a received CAN FD message

        Parameters:
            msg: The received PCAN-Basic CAN-FD message
            timestamp: Timestamp of the message as microseconds (ulong)
        """
        print("Type: " + self.get_type_string(msg.MSGTYPE))
        print("ID: " + self.get_id_string(msg.ID, msg.MSGTYPE))
        print("Length: " + str(self.get_length_from_dlc(msg.DLC)))
        print("Time: " + self.get_time_string(timestamp))
        print("Data: " + self.get_data_string(msg.DATA, msg.DLC, msg.MSGTYPE))
        print("----------------------------------------------------------")

    def show_status(self, status):
        """
        Shows formatted status

        Parameters:
            status: Will be formatted
        """
        print("=========================================================================================")
        error_text = self.get_formatted_error(status)
        print(error_text)
        if b"Bus error" in error_text:
            print("Suggested actions:")
            print("1. Check CAN bus termination.")
            print("2. Ensure all devices use the same bitrate.")
            print("3. Inspect cabling for loose connections.")
        print("=========================================================================================")

    def get_formatted_error(self, error):
        """
        Gets the formatted text for a given error code

        Parameters:
            error: Error code to be formatted

        Returns:
            The formatted error code as string
        """
        stsReturn = self.m_objPCANBasic.GetErrorText(error, 0x09)
        if stsReturn[0] != PCAN_ERROR_OK:
            return f"An error occurred. Error-code's text ({error:X}) couldn't be retrieved"
        else:
            return stsReturn[1]

    def get_type_string(self, msgtype):
        """
        Gets the name of a MSGTYPE

        Parameters:
            msgtype: The type to be converted

        Returns:
            The type name as string
        """
        if (msgtype & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            if (msgtype & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
                return "RTR Frame (Extended ID)"
            else:
                return "Extended Frame"
        elif (msgtype & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            return "RTR Frame (Standard ID)"
        else:
            return "Standard Frame"

    def get_id_string(self, id, msgtype):
        """
        Gets the string representation of the ID of a CAN message

        Parameters:
            id: Id to be converted
            msgtype: The type of the CAN message

        Returns:
            The ID of the CAN message as string
        """
        if (msgtype & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            return f"{id:X}"
        else:
            return f"{id & 0x7FF:X}"

    def get_time_string(self, time):
        """
        Gets the string representation of the timestamp of a CAN message

        Parameters:
            time: Time to be converted

        Returns:
            The timestamp of the CAN message as string
        """
        # Convert the bytes object to a c_ulonglong and then to a native Python int
        dSeconds = c_ulonglong.from_buffer_copy(time).value / 1000000.0
        return f"{dSeconds:.1f}"

    def get_data_string(self, data, dlc, msgtype):
        """
        Gets the string representation of the data of a CAN message

        Parameters:
            data: Data to be converted
            dlc: Data Length Code
            msgtype: The type of the CAN message

        Returns:
            The data of the CAN message as string
        """
        if (msgtype & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            return "Remote Request"
        else:
            return " ".join(f"{byte:X}" for byte in data[:dlc])

    def get_length_from_dlc(self, dlc):
        """
        Gets the length of the data from the DLC value of a CAN message

        Parameters:
            dlc: DLC value to be converted

        Returns:
            The length of the data
        """
        if dlc <= 8:
            return dlc
        elif dlc == 9:
            return 12
        elif dlc == 10:
            return 16
        elif dlc == 11:
            return 20
        elif dlc == 12:
            return 24
        elif dlc == 13:
            return 32
        elif dlc == 14:
            return 48
        elif dlc == 15:
            return 64
        else:
            return 0

if __name__ == "__main__":
    reader = CANFDReader()
    reader.read_messages()
