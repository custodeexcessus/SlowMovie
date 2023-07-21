#!/usr/bin/python3
# -*- coding:utf-8 -*-

"""
A script to play preprocessed frames on an e-ink display.
"""

import os
import time
import sys
import signal
import logging
import json
from PIL import Image
#import epaper

#epd_driver = epaper.epaper('epd7in5_V2').EPD()

class MockDisplayDriver:
    """
    A mock display driver for testing purposes.
    """

    def __init__(self):
        self.current_frame = None

    def display(self, frame, output_directory=None):
        """
        Instead of displaying the frame on a screen, we'll just save it to a variable.
        If an output directory is provided, also save the image to disk.
        """
        self.current_frame = frame
        if output_directory is not None:
            output_path = os.path.join(output_directory, f"frame_{self.currentFrame}.bmp")
            frame.save(output_path)

    def get_current_frame(self):
        """
        Return the current frame.
        """
        return self.current_frame

    def clear(self):
        """
        Clear the current frame.
        """
        self.current_frame = None

class FramePlayer:
    """
    A class to play preprocessed frames on an e-ink display.
    """

    def __init__(self, display_driver=None):
        """Initialize the FramePlayer class."""
        self.logger = logging.getLogger()
        file_handler = logging.FileHandler("slowmovie.log", encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-8s: %(module)s : %(message)s"))
        self.logger.addHandler(file_handler)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(levelname)s:%(module)s:%(message)s"))
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

        # Load config
        self.config = self.read_config()

        # Set up display
        self.epd = display_driver if display_driver is not None else self.setup_display()

        # Load frame data
        self.frame_count, self.image_files = self.load_frame_data()

        # Handle program exit
        signal.signal(signal.SIGTERM, self.exit_handler)
        signal.signal(signal.SIGINT, self.exit_handler)

        # Load current frame
        self.current_frame = self.load_current_frame()

    def read_config(self):
        """Read the configuration file."""
        with open("config.json", "r", encoding='utf-8') as file:
            return json.load(file)

    def setup_display(self):
        """Set up the e-Paper display."""
        try:
            epd = epd_driver.EPD()
            epd.init()
            return epd
        except Exception:
            self.logger.error("Failed to initialize the e-Paper display")
            sys.exit(1)

    def load_frame_data(self):
        """Load the frame data from the image files."""
        image_files = sorted([f for f in os.listdir(self.config["image_folder_path"]) if os.path.isfile(os.path.join(self.config["image_folder_path"], f))])
        return len(image_files), image_files

    def load_current_frame(self):
        """Load the current frame number."""
        if os.path.isfile(self.config["current_frame_file"]):
            with open(self.config["current_frame_file"], "r", encoding='utf-8') as file:
                return int(file.read().strip())
        else:
            return 0

    def exit_handler(self, *_):
        """Handle exit signals to ensure the program exits gracefully."""
        self.logger.info("Exiting Program")
        try:
            self.epd.init()
            self.epd.clear()
        finally:
            self.save_current_frame(self.current_frame)
            sys.exit()

    def save_current_frame(self, frame):
        """Save the current frame number."""
        with open(self.config["current_frame_file"], "w", encoding='utf-8') as file:
            file.write(str(frame))

    def display_frame(self, image_file_path, output_directory=None):
        """Display the given frame."""
        pil_im = Image.open(image_file_path)
        self.logger.debug("Displaying frame %s of %s (%.1f%%)", self.current_frame + 1, self.frame_count, ((self.current_frame + 1)/self.frame_count)*100)
        if output_directory is not None:
            output_path = os.path.join(output_directory, f"frame_{self.current_frame}.bmp")
            pil_im.save(output_path)
        else:
            self.epd.display(pil_im)

    def play(self):
        """Play the frames."""
        while True:
            image_file_path = os.path.join(self.config["image_folder_path"], self.image_files[self.current_frame])
            self.display_frame(image_file_path)

            self.current_frame += self.config["frame_rate"]
            if self.current_frame >= self.frame_count:
                break

            time.sleep(self.config["frame_rate"] / 1000)

if __name__ == "__main__":
    player = FramePlayer()
    player.play()
