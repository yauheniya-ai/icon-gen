"""Export animated SVGs to animated WebP by rasterizing frames.

This module samples simple Animator presets over time and produces
an animated WebP using Pillow + cairosvg. It supports the same
animation presets as `Animator`: `spin`, `pulse`, `flip-h`, `flip-v`.

Note: requires `Pillow` and `cairosvg` (the project already guards
for these as `RASTER_AVAILABLE` in `generator.py`).
"""
from __future__ import annotations

from typing import Optional, Union
from xml.etree import ElementTree as ET
from io import BytesIO

from .animator import _parse_duration_part, _dur_to_seconds

try:
    import cairosvg
    from PIL import Image, ImageColor
except Exception as e:
    cairosvg = None  # type: ignore
    Image = None  # type: ignore
    ImageColor = None  # type: ignore


def _find_or_wrap_target(root: ET.Element) -> ET.Element:
    ns = 'http://www.w3.org/2000/svg'
    tag_g = f'{{{ns}}}g'

    target = None
    for child in list(root):
        if child.tag == f'{{{ns}}}defs':
            continue
        if child.tag == tag_g:
            target = child
            break
        if target is None:
            target = child

    if target is None:
        return None

    if target.tag != tag_g:
        new_group = ET.Element(tag_g)
        for child in list(root):
            if child.tag == f'{{{ns}}}defs':
                continue
            root.remove(child)
            new_group.append(child)
        root.append(new_group)
        target = new_group

    return target


def _select_anim_target(root: ET.Element) -> Optional[ET.Element]:
    """Choose the best element to apply per-frame transforms to.

    Prefer a nested `<g>` that contains visual elements so we don't
    overwrite wrapper transforms (background, sizing, etc.).
    """
    ns = 'http://www.w3.org/2000/svg'
    visual_tags = { 'path', 'circle', 'rect', 'polygon', 'ellipse', 'polyline', 'line', 'text', 'image' }

    # Find any group that directly contains visual elements
    for g in root.findall('.//{http://www.w3.org/2000/svg}g'):
        for child in list(g):
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag in visual_tags:
                return g

    # Fallback: the top-level non-def group
    return _find_or_wrap_target(root)


def svg_animation_to_webp(
    svg_content: str,
    output_path,
    animation_spec: Union[str, dict],
    size: int = 256,
    fps: int = 20,
    loop: int = 0,
    quality: int = 95,
    bg_color: Optional[Union[str, tuple]] = None,
    border_radius: int = 0,
    outline_width: int = 0,
    outline_color: Optional[str] = None,
    bg_direction: str = 'horizontal',
) -> Optional[str]:
    """Rasterize `svg_content` across frames for `animation_spec` and save animated WebP.

    Returns the output path string on success, else None.
    """
    if cairosvg is None or Image is None:
        print("Error: cairosvg/Pillow not available for animated WebP export")
        return None

    # Normalize spec
    if isinstance(animation_spec, dict):
        anim_type = animation_spec.get('type')
        dur_part = _parse_duration_part(animation_spec.get('dur'))
    else:
        if isinstance(animation_spec, str) and ':' in animation_spec:
            anim_type, dur_raw = animation_spec.split(':', 1)
            dur_part = _parse_duration_part(dur_raw)
        else:
            anim_type = str(animation_spec)
            dur_part = None

    anim_type = (anim_type or '').strip().lower()

    # Default durations from Animator (keep consistent)
    defaults = {
        'spin': '4s',
        'pulse': '1.5s',
        'flip-h': '1s',
        'flip-v': '1s',
    }

    if anim_type in ('flip-h', 'flip-v'):
        # Animator uses flip dur as base and builds a 10x total cycle
        base_dur = dur_part or defaults.get(anim_type, '1s')
        flip_dur = _dur_to_seconds(base_dur)
        total_seconds = flip_dur * 10.0
    else:
        dur = dur_part or defaults.get(anim_type, '2s')
        total_seconds = _dur_to_seconds(dur)

    frames_count = max(1, int(fps * total_seconds))

    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError:
        print("Error: invalid SVG provided for webp export")
        return None

    # Determine center (cx,cy) from the SVG viewBox (works for original, unwrapped SVG)
    vb = root.get('viewBox')
    if vb:
        parts = vb.split()
        try:
            x, y, w, h = map(float, parts)
            cx = x + w / 2
            cy = y + h / 2
        except Exception:
            cx = cy = None
    else:
        try:
            w = float(root.get('width', '24'))
            h = float(root.get('height', '24'))
            cx = w / 2
            cy = h / 2
        except Exception:
            cx = cy = None

    if cx is None or cy is None:
        cx = cy = 0

    anim_target = _select_anim_target(root)
    if anim_target is None:
        print("Error: nothing to animate in SVG")
        return None

    # Remove existing SVG animation elements (we'll emulate them per-frame)
    for el in list(root.findall('.//')):
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        if tag in ('animate', 'animateTransform', 'animateMotion', 'set'):
            # remove from its parent by iterating potential parents
            for p in root.iter():
                if el in list(p):
                    p.remove(el)
                    break

    # We'll rasterize the base (non-animated) icon once, then apply
    # per-frame transforms (rotate/scale/flip) in PIL and composite
    # onto a generated background. This avoids SVG transform ordering
    # issues and keeps the visual center stable.
    original_anim_transform = (anim_target.get('transform') or '').strip()
    # Ensure anim_target has only the layout transform
    anim_target.set('transform', original_anim_transform)

    # Compute icon pixel size to match the inner scale used by wrap_with_background
    try:
        # Determine vb w/h (we may have set them earlier)
        if vb:
            # parts x,y,w,h already parsed above
            icon_vw = w
            icon_vh = h
        else:
            icon_vw = float(root.get('width', '24') or 24)
            icon_vh = float(root.get('height', '24') or 24)

        inner_scale = (size / max(icon_vw, icon_vh)) * 0.7
        icon_pixel_size = max(1, int(round(max(icon_vw, icon_vh) * inner_scale)))

        # Rasterize the icon at the scaled pixel size (so it matches SVG output)
        base_png = cairosvg.svg2png(bytestring=ET.tostring(root, encoding='unicode').encode('utf-8'), output_width=icon_pixel_size, output_height=icon_pixel_size)
        base_icon = Image.open(BytesIO(base_png)).convert('RGBA')
    except Exception as e:
        print(f"Error rasterizing base icon: {e}")
        return None

    pil_frames = []

    # Prepare background image (if requested) or transparent canvas
    from PIL import ImageDraw
    def make_background_image():
        base = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(base)

        if isinstance(bg_color, tuple):
            left = bg_color[0]
            right = bg_color[1]
            left_rgb = tuple(ImageColor.getrgb(left))
            right_rgb = tuple(ImageColor.getrgb(right))
            for y in range(size):
                for x in range(size):
                    if bg_direction == 'vertical':
                        ratio = y / (size - 1) if size > 1 else 0
                    elif bg_direction == 'diagonal':
                        ratio = (x + y) / (2 * (size - 1)) if size > 1 else 0
                    else:
                        ratio = x / (size - 1) if size > 1 else 0
                    r = int(left_rgb[0] * (1 - ratio) + right_rgb[0] * ratio)
                    g = int(left_rgb[1] * (1 - ratio) + right_rgb[1] * ratio)
                    b = int(left_rgb[2] * (1 - ratio) + right_rgb[2] * ratio)
                    draw.point((x, y), fill=(r, g, b, 255))
        else:
            from PIL import ImageColor as _IC
            fill = _IC.getrgb(bg_color) if bg_color else (0, 0, 0, 0)
            draw.rectangle([0, 0, size, size], fill=fill)

        if border_radius > 0:
            mask = Image.new('L', (size, size), 0)
            mdraw = ImageDraw.Draw(mask)
            mdraw.rounded_rectangle([0, 0, size, size], radius=border_radius, fill=255)
            base.putalpha(mask)

        if outline_width > 0 and outline_color:
            draw = ImageDraw.Draw(base)
            draw.rounded_rectangle([outline_width/2, outline_width/2, size - outline_width/2, size - outline_width/2], radius=max(0, border_radius - outline_width/2), outline=outline_color, width=int(outline_width))

        return base

    bg_img = make_background_image() if (bg_color or border_radius or outline_width) else Image.new('RGBA', (size, size), (0,0,0,0))

    # Helper for flip timing used by original Animator logic
    def flip_scale_at_time_func(tt_local, base):
        flip_dur = base
        stay = flip_dur * 4.0
        total = flip_dur * 10.0
        if tt_local < stay:
            return 1.0
        elif tt_local < stay + flip_dur:
            local = (tt_local - stay) / flip_dur
            if local <= 0.5:
                return 1.0 + (-1.0 - 1.0) * (local / 0.5)
            else:
                local2 = (local - 0.5) / 0.5
                return -1.0 + (1.0 - -1.0) * local2
        elif tt_local < stay + flip_dur + stay:
            return 1.0
        else:
            local = (tt_local - (stay + flip_dur + stay)) / flip_dur
            if local <= 0.5:
                return 1.0 + (-1.0 - 1.0) * (local / 0.5)
            else:
                local2 = (local - 0.5) / 0.5
                return -1.0 + (1.0 - -1.0) * local2

    for i in range(frames_count):
        t = (i / frames_count) if frames_count > 0 else 0.0
        abs_time = t * total_seconds

        frame = bg_img.copy()

        if anim_type == 'spin':
            angle = 360.0 * t
            # PIL rotates counter-clockwise for positive angles, SVG positive is clockwise
            rotated = base_icon.rotate(-angle, resample=Image.BICUBIC, expand=False)
            fw, fh = rotated.size
            px = (size - fw) // 2
            py = (size - fh) // 2
            frame.paste(rotated, (px, py), rotated)

        elif anim_type == 'pulse':
            if t <= 0.5:
                local = t / 0.5
                s = 1.0 + (0.1 - 1.0) * local
            else:
                local = (t - 0.5) / 0.5
                s = 0.1 + (1.0 - 0.1) * local
            new_w = max(1, int(base_icon.width * s))
            new_h = max(1, int(base_icon.height * s))
            resized = base_icon.resize((new_w, new_h), resample=Image.LANCZOS)
            px = (size - new_w) // 2
            py = (size - new_h) // 2
            frame.paste(resized, (px, py), resized)

        elif anim_type in ('flip-h', 'flip-v'):
            base_flip = _dur_to_seconds(dur_part or defaults.get(anim_type, '1s'))
            tt = abs_time % (base_flip * 10.0)
            s_val = flip_scale_at_time_func(tt, base_flip)
            if anim_type == 'flip-h':
                if s_val < 0:
                    flipped = base_icon.transpose(Image.FLIP_LEFT_RIGHT)
                else:
                    flipped = base_icon
            else:
                if s_val < 0:
                    flipped = base_icon.transpose(Image.FLIP_TOP_BOTTOM)
                else:
                    flipped = base_icon
            fw, fh = flipped.size
            px = (size - fw) // 2
            py = (size - fh) // 2
            frame.paste(flipped, (px, py), flipped)

        else:
            # static
            fw, fh = base_icon.size
            px = (size - fw) // 2
            py = (size - fh) // 2
            frame.paste(base_icon, (px, py), base_icon)

        pil_frames.append(frame)

    if not pil_frames:
        print("No frames generated for animated WebP")
        return None

    # Background was already composed per-frame earlier; no further action required here.

    # Save animated WebP
    try:
        # Compute per-frame duration so the total animation length matches
        # the calculated `total_seconds`.
        if frames_count > 0:
            duration_ms = max(1, int((total_seconds * 1000) / frames_count))
        else:
            duration_ms = max(1, int(1000 / fps))
        pil_frames[0].save(
            output_path,
            format='WEBP',
            save_all=True,
            append_images=pil_frames[1:],
            duration=duration_ms,
            loop=loop,
            quality=quality,
        )
        for im in pil_frames:
            try:
                im.close()
            except Exception:
                pass
        return str(output_path)
    except Exception as e:
        print(f"Error saving animated WebP: {e}")
        return None
