#!/usr/bin/python3

import tkinter as tk

import math
#from matplotlib import pyplot as plt
import struct
import configparser

PROGRAM_NAME = "Continuous Wave Generator"


class Wavegen:
    def __init__(self, root):
        self.root = root
        self.root.title(PROGRAM_NAME)
        self.createVars()
        self.createWidgets()
        self.config = configparser.ConfigParser()
        self.load_cfg()

    def createVars(self):
        self.cw_type = tk.IntVar()
        self.cw_type.set(1)
        self.sampling_freq = tk.DoubleVar()
        self.cw_freq = tk.DoubleVar()
        self.interp = tk.IntVar()
        self.interp.set(1)
        self.adj_freq = tk.DoubleVar()
        self.adj_freq.set(0.0)
        self.ampl = tk.DoubleVar()
        self.ampl.set(1.0)
        self.m3db = tk.BooleanVar()
        self.m3db.set(False)
        self.length = tk.IntVar()
        self.length.set(32768)
        self.filename = tk.StringVar(self.root, value="filename")

    def createWidgets(self):
        # type_frame = Frame(self.root, height=15, bd=5, relief=GROOVE, padx=5, pady=5)
        self.frame = frame = tk.Frame(self.root, bd=3, relief=tk.GROOVE, padx=10, pady=10)
        frame.grid(row=3, column=3, sticky=tk.NW)

        row = 0
        tk.Label(frame, text="Waveform type").grid(column=0, row=0, sticky=tk.E)
        cwtype = tk.Radiobutton(frame, text="Real", variable=self.cw_type, value=0)
        cwtype.grid(padx=20, column=1, row=row)
        cwtype.bind("<ButtonRelease>", self.setFilename)
        cwtype = tk.Radiobutton(frame, text="Complex", variable=self.cw_type, value=1)
        cwtype.grid(column=2, row=row)
        cwtype.bind("<ButtonRelease>", self.setFilename)

        row += 1
        tk.Label(frame, text="Sampling Frequency (MHz)").grid(column=0, row=row)
        sampling = self.sampling = tk.Entry(frame, textvariable=self.sampling_freq, width=10)
        sampling.grid(column=1, row=row)
        sampling.bind("<FocusOut>", self.setFilename)

        row += 1
        tk.Label(frame, text="Interpolation").grid(column=0, row=row, sticky=tk.E)
        interp = tk.Entry(frame, textvariable=self.interp, width=10)
        interp.grid(column=1, row=row)
        interp.bind("<FocusOut>", self.setFilename)

        row += 1
        tk.Label(frame, text="Waveform Frequency (MHz)").grid(column=0, row=row)
        freq = tk.Entry(frame, textvariable=self.cw_freq, width=10)
        freq.grid(column=1, row=row)
        freq.bind("<FocusOut>", self.setFilename)

        row += 1
        tk.Label(frame, text="Waveform Amplitude").grid(column=0, row=row, sticky=tk.E)
        ampl = tk.Entry(frame, textvariable=self.ampl, width=10)
        ampl.grid(column=1, row=row)
        ampl.bind("<FocusOut>", self.setFilename)
        m3db = tk.Checkbutton(frame, text="-3dB", variable=self.m3db)
        m3db.grid(column=2, row=row)
        m3db.bind("<ButtonRelease>", self.setFilename)

        row += 1
        tk.Label(frame, text="Waveform Length (samples)").grid(column=0, row=row)
        length = tk.Entry(frame, textvariable=self.length, width=10)
        length.grid(column=1, row=row)
        length.bind("<FocusOut>", self.setFilename)

        row += 1
        tk.Label(frame, text="File Name").grid(column=0, row=row, sticky=tk.E)
        fname = self.fname = tk.Entry(frame, textvariable=self.filename, width=30)
        fname.grid(column=1, row=row, padx=20, columnspan=2)

        row += 1
        tk.Label(frame, text="Adjusted Frequency").grid(column=0, row=row, sticky=tk.E)
        tk.Entry(
            frame,
            textvariable=self.adj_freq,
            state=tk.DISABLED,
            disabledforeground="black",
            width=10,
        ).grid(column=1, row=row, sticky=tk.N)

        row += 1
        self.genButton = tk.Button(frame, text="Generate", command=self.generate)
        self.genButton.grid(column=1, row=row, pady=20)
        self.quitButton = tk.Button(frame, text="Quit", command=quit).grid(
            column=2, row=row
        )

    def load_cfg(self):
        self.config.read("wavegen.ini")
        if not self.config.sections():
            self.config["Waveform"] = {
                "Type": "1",
                "SamplingFrequency": "6400.0",
                "Interpolation": "1",
                "Frequency": "2.0",
                "Amplitude": "1.0",
                "Length": "32768",
            }
            with open("wavegen.ini", "w") as cfgfile:
                self.config.write(cfgfile)
        self.cw_type.set(self.config["Waveform"]["Type"])
        self.sampling_freq.set(self.config["Waveform"]["SamplingFrequency"])
        self.interp.set(self.config["Waveform"]["Interpolation"])
        self.cw_freq.set(self.config["Waveform"]["Frequency"])
        self.ampl.set(self.config["Waveform"]["Amplitude"])
        self.length.set(self.config["Waveform"]["Length"])

    def save_cfg(self):
        self.config["Waveform"]["Type"] = str(self.cw_type.get())
        self.config["Waveform"]["SamplingFrequency"] = str(self.sampling_freq.get())
        self.config["Waveform"]["Interpolation"] = str(self.interp.get())
        self.config["Waveform"]["Frequency"] = str(self.cw_freq.get())
        self.config["Waveform"]["Amplitude"] = str(self.ampl.get())
        self.config["Waveform"]["Length"] = str(self.length.get())
        with open("wavegen.ini", "w") as cfgfile:
            self.config.write(cfgfile)

    def quit():
        pass

    def generate(self):
        freq = self.sampling_freq.get() / float(self.interp.get())
        ampl = self.ampl.get()
        if self.m3db.get():
            ampl = 0.707
            self.ampl.set(ampl)
        data = self.sinewave(
            self.cw_freq.get(),
            ampl,
            freq,
            self.length.get(),
            self.cw_type.get(),
        )
        self.savefile(data)
        self.save_cfg()

    def setFilename(self, event):
        name = "cplx_" if self.cw_type.get() else "real_"
        name += f"{self.sampling_freq.get()}MHz_"
        name += f"{self.cw_freq.get()}MHz_"
        name += f"{self.interp.get()}x_"
        if self.m3db.get():
            name += f"-3db"
        else:
            name += f"{self.ampl.get()}a"
        self.filename.set(name)

    def sinewave(
        self, freq, amplitude=1.0, sampling_freq=1.0, length=4096, cw_type=False
    ):
        data = []
        fadj = sampling_freq / length * int(freq * length / sampling_freq)
        self.adj_freq.set(fadj)
        # print(f"Frequency adjustment, Requested = {freq}, Adjusted = {fadj}")
        for i in range(length):
            if cw_type:  # complex
                data.append(
                    math.cos(i * 2 * math.pi * fadj / sampling_freq) * amplitude
                )
            data.append(math.sin(i * 2 * math.pi * fadj / sampling_freq) * amplitude)
        #self.plot(data)
        return data

    def savefile(self, data):
        # TODO: fix rounding for generic sample width
        data = [int(round(x * 8191)) for x in data]
        with open(f"{self.filename.get()}.txt", "w") as f:
            f.write("\n".join([str(x) for x in data]))
        with open(f"{self.filename.get()}.bin", "wb") as f:
            for value in data:
                # fetch the 14 bit signed value as byte
                new_value = struct.pack("<h", value)
                f.write(new_value)

#    def plot(self, data):
#        plt.plot(data[0:32])
#        plt.title("Time Domain")
#        plt.xlabel("Sample")
#        plt.ylabel("ADC Code")
#        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    Wavegen(root)
    root.mainloop()
