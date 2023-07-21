import unittest
import os
from slowmovie import MockDisplayDriver, FramePlayer

class TestFramePlayer(unittest.TestCase):
    """
    A class for testing the FramePlayer.
    """

    def setUp(self):
        """
        Set up the FramePlayer instance with some test configuration.
        """
        self.mock_display_driver = MockDisplayDriver()
        self.player = FramePlayer(display_driver=self.mock_display_driver)
        self.player.config["image_folder_path"] = "images"
        self.player.config["current_frame_file"] = "current_frame.txt"
        
        # Ensure the current frame file has a valid integer
        if not os.path.isfile(self.player.config["current_frame_file"]) or not open(self.player.config["current_frame_file"], "r").read().strip():
            with open(self.player.config["current_frame_file"], "w") as file:
                file.write("0")

        self.player.frame_count, self.player.image_files = self.player.load_frame_data()
        self.player.current_frame = self.player.load_current_frame()
        self.output_directory = "imagetestoutput"

    def test_display_frame(self):
        current_frame = self.player.current_frame
        image_file_path = os.path.join(self.player.config["image_folder_path"], self.player.image_files[current_frame])
        self.player.display_frame(image_file_path, self.output_directory)

        # Check if the frame has been saved correctly
        output_file_path = os.path.join(self.output_directory, f"frame_{current_frame}.bmp")
        self.assertTrue(os.path.isfile(output_file_path))

if __name__ == '__main__':
    unittest.main()
