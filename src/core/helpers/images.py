import sys, discord, typing, os
sys.dont_write_bytecode = True
import src.connector as con

class Images:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.image_path: str = f"{self.shared.path}/images"
        self.load_images()

    def load_images(self) -> None:
        for image_name in os.listdir(self.image_path):
            file = discord.File(f"{self.image_path}/{image_name}", image_name)
            setattr(self, image_name.split(".")[0], file)