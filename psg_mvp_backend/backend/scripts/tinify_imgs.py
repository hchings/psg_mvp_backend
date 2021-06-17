"""
CLI to tinify image size.

> python tinify_imgs

"""
import os
from pathlib import Path


import typer
import tinify


tinify.key = "SC9JFT8nrbvD8Gfl2GWbFlXyct2FN1Bb"
MEDIA_ROOT = "../../media"


def tinify_imgs(dir_names=["cases", "CACHE"]):
    file_types = ('*.jpg', '*.png', '*.JPG', '*.jpeg')  # the tuple of file types

    for name in dir_names:
        root_dir = os.path.join(MEDIA_ROOT, name)

        for file_type in file_types:
            for path in Path(root_dir).rglob(file_type):
                print(path)
                source = tinify.from_file(path)
                # if not bool(dry_run):
                print("comporess")
                source.to_file(path)


if __name__ == "__main__":
    typer.run(tinify_imgs)
