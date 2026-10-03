"""Minimal SVG -> PNG renderer using the system librsvg + cairo via ctypes."""
import ctypes

_rsvg = ctypes.CDLL("librsvg-2.so.2")
_cairo = ctypes.CDLL("libcairo.so.2")

class _Rect(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double),
                ("width", ctypes.c_double), ("height", ctypes.c_double)]

_rsvg.rsvg_handle_new_from_data.restype = ctypes.c_void_p
_rsvg.rsvg_handle_new_from_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_void_p]
_rsvg.rsvg_handle_render_document.restype = ctypes.c_int
_rsvg.rsvg_handle_render_document.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(_Rect), ctypes.c_void_p]
_cairo.cairo_image_surface_create.restype = ctypes.c_void_p
_cairo.cairo_image_surface_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
_cairo.cairo_create.restype = ctypes.c_void_p
_cairo.cairo_create.argtypes = [ctypes.c_void_p]
_cairo.cairo_surface_write_to_png.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_cairo.cairo_destroy.argtypes = [ctypes.c_void_p]
_cairo.cairo_surface_destroy.argtypes = [ctypes.c_void_p]

def render(svg_text: str, out_png: str, width: int, height: int) -> None:
    data = svg_text.encode("utf-8")
    handle = _rsvg.rsvg_handle_new_from_data(data, len(data), None)
    if not handle:
        raise RuntimeError("librsvg could not parse SVG for " + out_png)
    surf = _cairo.cairo_image_surface_create(0, width, height)  # ARGB32
    cr = _cairo.cairo_create(surf)
    vp = _Rect(0, 0, width, height)
    if not _rsvg.rsvg_handle_render_document(handle, cr, ctypes.byref(vp), None):
        raise RuntimeError("librsvg failed to render " + out_png)
    _cairo.cairo_surface_write_to_png(surf, out_png.encode())
    _cairo.cairo_destroy(cr)
    _cairo.cairo_surface_destroy(surf)
