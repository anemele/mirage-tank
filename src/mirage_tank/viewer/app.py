import os.path as osp
from itertools import chain
from pathlib import Path

from flask import Flask, render_template, send_file, send_from_directory
from flask_socketio import SocketIO
from watchdog.events import (
    DirModifiedEvent,
    DirMovedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

IMAGES_PATH = Path.cwd() / "viewer-images"
if not IMAGES_PATH.exists():
    IMAGES_PATH.mkdir()
if not (gitignore_path := IMAGES_PATH / ".gitignore").exists():
    gitignore_path.write_text("*")

THIS_PATH = Path(__file__).parent
app = Flask(
    __name__,
    template_folder=THIS_PATH,
    static_folder=THIS_PATH / "static",
)
socketio = SocketIO(app)

SUPPORTED_EXTENSIONS = ("png", "jpg", "jpeg", "gif", "svg", "webp")

imgs = {
    f"img/{path.name}"
    for path in chain.from_iterable(
        IMAGES_PATH.glob(f"*.{ext}") for ext in SUPPORTED_EXTENSIONS
    )
}


class MyHandler(FileSystemEventHandler):
    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        src_pth = str(event.src_path)
        dest_pth = str(event.dest_path)
        # print(f"Moved: from {src_pth} to {dest_pth}")
        if src_pth.endswith(".png"):
            name = osp.basename(src_pth)
            imgs.discard(f"img/{name}")
        if dest_pth.endswith(".png"):
            name = osp.basename(dest_pth)
            imgs.add(f"img/{name}")
            socketio.emit("created", dict(src=f"img/{name}", name=name))
        # print(imgs)

    def on_created(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        # print(f"Created: {path}")
        if pth.endswith(".png"):
            name = osp.basename(pth)
            imgs.add(f"img/{name}")
            socketio.emit("created", dict(src=f"img/{name}", name=name))
        # print(imgs)

    def on_deleted(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        # print(f"Deleted: {path}")
        if pth.endswith(".png"):
            name = osp.basename(pth)
            imgs.discard(f"img/{name}")
        # print(imgs)


event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, str(IMAGES_PATH), recursive=False)
observer.start()


@app.route("/")
def index():
    return render_template("index.html", imgs=imgs)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(THIS_PATH / "static", "favicon.ico")


@app.route("/img/<name>")
def get_img(name: str):
    img_pth = IMAGES_PATH / name
    return send_file(str(img_pth))


def main():
    app.run(debug=False, host="localhost")
