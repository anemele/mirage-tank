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
IMAGES_PATH.mkdir(exist_ok=True)
IMAGES_PATH.joinpath(".gitignore").write_text("*")

THIS_PATH = Path(__file__).parent
app = Flask(
    __name__,
    template_folder=THIS_PATH,
    static_folder=THIS_PATH / "static",
)
socketio = SocketIO(app)

img_names = {
    path.name
    for path in chain.from_iterable(
        map(
            IMAGES_PATH.glob,
            ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp"),
        )
    )
}


class MyHandler(FileSystemEventHandler):
    @staticmethod
    def _op(event: str, src: str) -> None:
        if not src.endswith(".png"):
            return

        name = osp.basename(src)
        if event == "delete":
            img_names.discard(name)
        else:
            img_names.add(name)

        socketio.emit(event, {"src": f"img/{name}", "name": name})

    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None:
        src_pth = str(event.src_path)
        dst_pth = str(event.dest_path)
        self._op("deleted", src_pth)
        self._op("created", dst_pth)

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        self._op("modified", pth)

    def on_created(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        self._op("created", pth)

    def on_deleted(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        pth = str(event.src_path)
        self._op("deleted", pth)


observer = Observer()
observer.schedule(MyHandler(), str(IMAGES_PATH), recursive=False)
observer.start()


@app.route("/")
def index():
    return render_template(
        "index.html",
        imgs=[{"src": f"img/{name}", "name": name} for name in img_names],
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(THIS_PATH / "static", "favicon.ico")


@app.route("/img/<name>")
def get_img(name: str):
    return send_from_directory(IMAGES_PATH, name)


def main():
    import argparse
    import webbrowser

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False)
    args = parser.parse_args()

    webbrowser.open_new("http://127.0.0.1:5000/")

    app.run(debug=args.debug, host="127.0.0.1", port=5000)
