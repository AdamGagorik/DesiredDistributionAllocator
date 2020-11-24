"""
Serve the main dashboard for debugging.
"""
import panel as pn
import traceback
import pathlib
import io

from .dashboard import Dashboard


if __name__ == '__main__':
    ROOT = str(pathlib.Path(__file__).parent.parent.parent.parent.absolute())
    # noinspection PyBroadException
    try:
        dashboard = Dashboard(parent=None)
        dashboard.connect()
        dashboard.serve()
    except Exception:
        stream = io.StringIO()
        traceback.print_exc(file=stream)
        widget = pn.pane.Markdown(fr"```python{stream.getvalue().replace(ROOT, '')}```", sizing_mode='stretch_width')
        pn.serve(widget)
