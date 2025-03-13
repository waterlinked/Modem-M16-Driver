import json
import threading
import time
import tkinter as tk
from tkinter import ttk, PhotoImage
from tkinter.scrolledtext import ScrolledText
from m16_driver import M16

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s:%(lineno)d=%(levelname)s:%(message)s')

class M16GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("M16 Modem Controller")
        self.geometry("600x900")
        self.modem = None  # Instance of M16
        self.diag_window = None  # Diagnostic window reference
        self.filename = None
        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Create the layout of the GUI app
        """
        # Create a ttk style for caption labels
        style = ttk.Style()
        style.configure("Custom.TLabelframe.Label", font=("Helvetica", 11, "bold"))
        # --- Connection Frame ---
        conn_frame = ttk.LabelFrame(self, text="Connection", style="Custom.TLabelframe")
        conn_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(conn_frame, text="Port:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.port_entry = ttk.Entry(conn_frame, width=12)
        self.port_entry.insert(0, "COM3")
        self.port_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.connect_button = ttk.Button(
            conn_frame, text="Connect", command=self.connect_modem, width=12
        )
        self.connect_button.grid(row=0, column=2, padx=5, pady=5)

        self.status_label = ttk.Label(
            conn_frame, text="Not Connected", foreground="red"
        )
        self.status_label.grid(row=0, column=3, padx=5, pady=5)        

        # Create a subframe for the logo in column 0 of conn_frame using grid
        logo_frame = ttk.Frame(conn_frame)
        logo_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        
        # Load and scale the logo image
        logo = PhotoImage(file="media/3-2-2_inverted_logo_waterlinked.png")
        scale_factor = 17  # Adjust as needed
        logo_small = logo.subsample(scale_factor, scale_factor)
        
        # Create a label for the logo and place it in the logo_frame
        self.logo_label = ttk.Label(logo_frame, image=logo_small)
        self.logo_label.image = logo_small
        self.logo_label.grid(row=0, column=0)


        # --- Current State Display ---
        state_frame = ttk.LabelFrame(self, text="Current State", style="Custom.TLabelframe")
        state_frame.pack(padx=10, pady=10, fill="x")
        self.state_label = ttk.Label(
            state_frame,
            text="Channel: Unknown   Level: Unknown   Mode: Unknown",
        )
        self.state_label.pack(padx=5, pady=5)

        # --- Controls Frame ---
        ctrl_frame = ttk.LabelFrame(self, text="Modem Controls", style="Custom.TLabelframe")
        ctrl_frame.pack(padx=10, pady=10, fill="x")

        button_width = 15

        # Set Channel
        ttk.Label(ctrl_frame, text="Set Channel (1-12):").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.channel_spin = ttk.Spinbox(ctrl_frame, from_=1, to=12, width=5)
        self.channel_spin.set(1)
        self.channel_spin.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.set_channel_button = ttk.Button(
            ctrl_frame, text="Set Channel", command=self.set_channel, width=button_width
        )
        self.set_channel_button.grid(row=0, column=2, padx=5, pady=5)

        # Set Power Level (displayed as 1-4 after remapping)
        ttk.Label(ctrl_frame, text="Set Power Level (1-4):").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        self.level_spin = ttk.Spinbox(ctrl_frame, from_=1, to=4, width=5)
        self.level_spin.set(4)
        self.level_spin.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.set_level_button = ttk.Button(
            ctrl_frame, text="Set Level", command=self.set_level, width=button_width
        )
        self.set_level_button.grid(row=1, column=2, padx=5, pady=5)

        # Mode display and toggle button
        self.mode_label = ttk.Label(ctrl_frame, text="Mode: Unknown")
        self.mode_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.toggle_mode_button = ttk.Button(
            ctrl_frame, text="Toggle Mode", command=self.toggle_mode, width=button_width
        )
        self.toggle_mode_button.grid(row=2, column=2, padx=5, pady=5, sticky="e")

        # Send Two Bytes
        ttk.Label(ctrl_frame, text="Send Two Bytes:").grid(
            row=3, column=0, padx=5, pady=5, sticky="w"
        )
        self.two_bytes_entry = ttk.Entry(ctrl_frame, width=10)
        self.two_bytes_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.send_two_bytes_button = ttk.Button(
            ctrl_frame, text="Send", command=self.send_two_bytes, width=button_width
        )
        self.send_two_bytes_button.grid(row=3, column=2, padx=5, pady=5)

        # Send a Longer Message using send_msg()
        ttk.Label(ctrl_frame, text="Send Message:").grid(
            row=4, column=0, padx=5, pady=5, sticky="w"
        )
        self.msg_entry = ttk.Entry(ctrl_frame, width=20)
        self.msg_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.send_msg_button = ttk.Button(
            ctrl_frame, text="Send Message", command=self.send_message, width=button_width
        )
        self.send_msg_button.grid(row=4, column=2, padx=5, pady=5)

        # Report File (optional) with placeholder behavior
        ttk.Label(ctrl_frame, text="Report File (optional):").grid(
            row=5, column=0, padx=5, pady=5, sticky="w"
        )
        self.report_file_entry = ttk.Entry(ctrl_frame, width=20)
        self.report_file_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.report_file_entry.insert(0, "Example: report.json")
        self.report_file_entry.config(foreground="grey")
        self.report_file_entry.bind(
            "<FocusIn>", self.handle_report_file_focus_in
        )
        self.report_file_entry.bind(
            "<FocusOut>", self.handle_report_file_focus_out
        )

        # Request Report
        self.request_report_button = ttk.Button(
            ctrl_frame, text="Request Report", command=self.request_report, width=button_width
        )
        self.request_report_button.grid(
            row=5, column=2, columnspan=3, padx=5, pady=5
        )

        # --- Output Log Frame ---
        output_frame = ttk.LabelFrame(self, text="Output Log", style="Custom.TLabelframe")
        output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_text = ScrolledText(output_frame, state="disabled", height=20)
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)

    def handle_report_file_focus_in(self, event: tk.Event) -> None:
        """
        Delete and change the color of the example text when the user selects the field to edit save file.
        """
        if self.report_file_entry.get() == "Example: report.json":
            self.report_file_entry.delete(0, tk.END)
            self.report_file_entry.config(foreground="black")

    def handle_report_file_focus_out(self, event: tk.Event) -> None:
        """
        Populate the report file field with the example text if the user did not specify a save file.
        """
        if not self.report_file_entry.get():
            self.report_file_entry.insert(0, "Example: report.json")
            self.report_file_entry.config(foreground="grey")

    def log_message(self, message: str):
        """
        Log a given message to the oputput field.

        Parameters:
            message (str): The message to log to the output log.
        """
        def append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.after(0, append)

    def update_state_display(self) -> None:
        """
        Update the Current State label using the modem's internal state.
        """
        if self.modem is not None:
            ch = self.modem.channel if self.modem.channel is not None else "Unknown"
            if self.modem.level is not None:
                lv = self.modem.level
            else:
                lv = "Unknown"
            if self.modem.diagnostic is None:
                mode = "Unknown"
            else:
                mode = "Diagnostic" if self.modem.diagnostic else "Transparent"
                self.mode_label.config(text=f"Mode: {mode}")
        else:
            ch, lv, mode = "Unknown", "Unknown", "Unknown"
        state_text = f"Channel: {ch}   Level: {lv}   Mode: {mode}"
        self.after(0, lambda: self.state_label.config(text=state_text))            

    def connect_modem(self) -> None:
        """
        Connect to the modem and update the modem states shown in the GUI app.
        """
        port = self.port_entry.get().strip()

        logger.debug(f"Starting init modem")
        self.modem = M16(port, channel=1, level=4, diagnostic=False)
        logger.debug(f"Done init modem")
        self.log_message(f"Connected to {port}")
        self.after(0, lambda: self.status_label.config(text="Connected", foreground="green"))
        self.update_state_display()
        logger.debug(f"Starting thread: monitor_received_packets")
        threading.Thread(target=self.monitor_received_packets, daemon=True).start()


    def set_channel(self) -> None:
        """
        Set the modem channel to the one specified by the user.
        """
        if not self.modem:
            self.log_message("Modem not connected.")
            return
        try:
            channel = int(self.channel_spin.get())
        except ValueError:
            self.log_message("Invalid channel value.")
            return

        def task():
            try:
                self.modem.set_channel(channel)
                self.log_message(f"Channel set to {channel}")
                self.update_state_display()
            except Exception as e:
                self.log_message(f"Error setting channel: {e}")
        logger.debug(f"Starting thread set_channel")
        threading.Thread(target=task, daemon=True).start()

    def set_level(self) -> None:
        """
        Set the modem power level to the one specified by the user.
        """
        if not self.modem:
            self.log_message("Modem not connected.")
            return
        try:
            level = int(self.level_spin.get())
        except ValueError:
            self.log_message("Invalid level value.")
            return

        def task():
            try:
                self.modem.set_level(level)
                self.log_message(f"Level set to {level}")
                self.update_state_display()
            except Exception as e:
                self.log_message(f"Error setting level: {e}")

        logger.debug(f"Starting thread set_level")
        threading.Thread(target=task, daemon=True).start()

    def toggle_mode(self) -> None:
        """
        Toggle the modem between transparent and diagnostic mode.
        """
        if not self.modem:
            self.log_message("Modem not connected.")
            return

        def task():
            try:
                self.modem.toggle_mode()
                new_mode = (
                    "Diagnostic" if self.modem.diagnostic else "Transparent"
                    if self.modem.diagnostic is not None else "Unknown"
                )
                self.log_message(f"Mode toggled. New mode: {new_mode}")
                self.after(0, lambda: self.mode_label.config(text=f"Mode: {new_mode}"))
                self.update_state_display()
                if self.modem.diagnostic:
                    self.after(0, self.open_diagnostic_window)
                else:
                    if self.diag_window is not None:
                        self.after(0, self.diag_window.destroy)
                        self.diag_window = None
            except Exception as e:
                self.log_message(f"Error toggling mode: {e}")

        logger.debug(f"Starting thread toggle_mode")
        threading.Thread(target=task, daemon=True).start()

    def open_diagnostic_window(self) -> None:
        """
        Open the diagnostic window and continously print diagnostic reports as they are recieved.
        """
        if self.diag_window is not None:
            return
        self.diag_window = tk.Toplevel(self)
        self.diag_window.title("Diagnostic Reports")
        self.diag_window.protocol("WM_DELETE_WINDOW", self.on_diag_window_closed)
        self.diag_text = ScrolledText(self.diag_window, state="disabled", height=20)
        self.diag_text.pack(padx=5, pady=5, fill="both", expand=True)
        logger.debug(f"Starting thread diganostic window")
        threading.Thread(target=self.monitor_received_packets, daemon=True).start()

    def on_diag_window_closed(self) -> None:
        """
        Close and change the modem mode when the diagnostic window is closed.
        """
        if self.diag_window is not None:
            self.diag_window.destroy()
            self.diag_window = None
        # Toggle modem back to transparent if still in diagnostic mode.
        if self.modem and self.modem.diagnostic:
            self.toggle_mode()

    def monitor_received_packets(self) -> None:
        """
        Continuously read from the modem and log received data.
        If the returned buffer is exactly 2 bytes, decode them as ASCII
        and log "Received bytes: ..." Otherwise, process it as a diagnostic report.
        """
        while self.modem:
            packet = self.modem.read_packet()
            if packet:
                # Handle recieved 2 bytes 
                if len(packet) == 2:
                    try:
                        text = packet.decode('ascii', errors='replace')
                    except Exception as e:
                        text = packet.hex()
                    self.after(0, lambda: self.log_message("Received bytes: " + text))
                # Handle everything else as a potential report
                else:
                    report = self.modem.decode_packet(packet)
                    if report:
                        self.modem.update_state_from_report(report)
                        ch_disp = self.modem.channel
                        lv_disp = self.modem.level
                        diag = self.modem.diagnostic
                        mode_disp = "Diagnostic" if diag == 1 else "Transparent" if diag is not None else "Unknown"
                        if self.focus_get() != self.channel_spin:
                            self.after(0, lambda: self.channel_spin.set(ch_disp))
                        if self.focus_get() != self.level_spin:
                            self.after(0, lambda: self.level_spin.set(lv_disp))
                        self.after(0, lambda: self.mode_label.config(text=f"Mode: {mode_disp}"))
                        self.update_state_display()
                        report_str = json.dumps(
                            report, indent=4, default=self.modem._default_converter
                        )
                        # Do not print to output log if in diagnostic
                        if self.modem.diagnostic != True:
                            self.log_message("Report received:")
                            self.log_message(report_str)

                            # Do not save report when in diagnostic
                            if self.filename is not None:
                                self.log_message(f"Report Saved to {self.filename}")
                                with open(self.filename, "w") as f:
                                    json.dump(report, f, indent=4, default=self.modem._default_converter)

                        self.after(0, lambda: self.append_diag_text(report_str))
            else:
                time.sleep(0.1)

    def append_diag_text(self, text: str):
        """
        Add the text to the diagnostic, ensuring it remains scrollable and disabling user edits.

        Parameters:
            text (str): Diagnostic report to be displayed to the user.
        """
        if self.diag_window is None:
            return
        self.diag_text.config(state="normal")
        self.diag_text.insert("end", text + "\n")
        self.diag_text.see("end")
        self.diag_text.config(state="disabled")

    def read_response(self) -> (str | None):
        """
        Attempt to read available data from the modem (regardless of mode).
        """
        if self.modem:
            if self.modem.ser.in_waiting:
                try:
                    data = self.modem.ser.read(self.modem.ser.in_waiting)
                    return data.decode('ascii', errors='replace')
                except Exception as e:
                    self.log_message(f"Error reading response: {e}")
        return None

    def send_two_bytes(self) -> None:
        """
        Send two bytes from the modem using the function from the driver while adding user feedback to the 
        output log.
        """
        if not self.modem:
            self.log_message("Modem not connected.")
            return
        data = self.two_bytes_entry.get().strip()
        if len(data) < 2:
            self.log_message("Please enter at least two characters for two-byte send.")
            return

        def task():
            try:
                self.modem.send_two_bytes(data)
                self.log_message(f"Sent two bytes: {data}")
                response = self.read_response()
                if response:
                    self.log_message(f"Received: {response}")
            except Exception as e:
                self.log_message(f"Error sending two bytes: {e}")

        logger.debug(f"Starting thread send_two_bytes")
        threading.Thread(target=task, daemon=True).start()

    def send_message(self) -> None:
        """
        Send a message (more than two bytes) from the modem using the function from the driver 
        while adding user feedback to the output log.
        """
        if not self.modem:
            self.log_message("Modem not connected.")
            return
        message = self.msg_entry.get().strip()
        if not message:
            self.log_message("Please enter a message to send.")
            return

        def task():
            try:
                self.log_message(f"Sending message: {message}")
                self.modem.send_msg(message)
                self.log_message("Finished sending message.")
                time.sleep(1)
                response = self.read_response()
                if response:
                    self.log_message(f"Received: {response}")
            except Exception as e:
                self.log_message(f"Error sending message: {e}")

        logger.debug(f"Starting thread send_message")
        threading.Thread(target=task, daemon=True).start()

    def request_report(self) -> None:
        """
        Request a report using the driver function and show it in the output log.
        """
        if not self.modem:
            self.log_message("Modem not connected.")
            return
        filename = self.report_file_entry.get().strip()
        if filename == "" or filename == "Example: report.json":
            self.filename = None
        else:
            self.filename = filename

        def task():
            try:
                self.log_message("Requesting report...")
                self.modem.get_report()
            except Exception as e:
                self.log_message(f"Error requesting report: {e}")

        threading.Thread(target=task, daemon=True).start()



if __name__ == "__main__":
    app = M16GUI()
    app.mainloop()
