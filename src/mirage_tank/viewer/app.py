import os.path as osp
from itertools import chain
from pathlib import Path

from flask import Flask, render_template, send_from_directory
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

SUPPORTED_EXTENSIONS = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp")

img_names = {
    path.name
    for path in chain.from_iterable(map(IMAGES_PATH.glob, SUPPORTED_EXTENSIONS))
}


class MyHandler(FileSystemEventHandler):
    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        src_pth = str(event.src_path)
        dest_pth = str(event.dest_path)
        print(f"Moved: from {src_pth} to {dest_pth}")
        if src_pth.endswith(".png"):
            name = osp.basename(src_pth)
            img_names.discard(name)
            socketio.emit("deleted", dict(src=f"img/{name}", name=name))
        if dest_pth.endswith(".png"):
            name = osp.basename(dest_pth)
            img_names.add(name)
            socketio.emit("created", dict(src=f"img/{name}", name=name))

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        print(f"Modified: {pth}")
        if pth.endswith(".png"):
            name = osp.basename(pth)
            img_names.add(name)
            socketio.emit("modified", dict(src=f"img/{name}", name=name))

    def on_created(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        print(f"Created: {pth}")
        if pth.endswith(".png"):
            name = osp.basename(pth)
            img_names.add(name)
            socketio.emit("created", dict(src=f"img/{name}", name=name))

    def on_deleted(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        print(f"Deleted: {pth}")
        if pth.endswith(".png"):
            name = osp.basename(pth)
            img_names.discard(name)
            socketio.emit("deleted", dict(src=f"img/{name}", name=name))


event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, str(IMAGES_PATH), recursive=False)
observer.start()


@app.route("/")
def index():
    return render_template(
        "index.html",
        imgs=[dict(src=f"img/{name}", name=name) for name in img_names],
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(THIS_PATH / "static", "favicon.ico")


@app.route("/img/<name>")
def get_img(name: str):
    return send_from_directory(IMAGES_PATH, name)


def main():
    import webbrowser

    webbrowser.open_new("http://localhost:5000/")

    app.run(debug=False, host="localhost", port=5000)


if __name__ == "__main__":
    main()
