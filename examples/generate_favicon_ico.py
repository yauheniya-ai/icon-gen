"""Generate a favicon ICO from an Iconify icon."""

from pathlib import Path
import sys

# Add project root to path for local development
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from icon_gen_ai.generator import IconGenerator


def main():
    generator = IconGenerator(output_dir="output")

    size = 256
    border_radius = 48

    # Gradient background
    bg_color = ("deeppink", "mediumslateblue")

    print("Generating SVG source...")

    svg_path = generator.generate_icon(
        icon_name="gis:drone",
        output_name="favicon",
        color="white",
        size=size,
        bg_color=bg_color,
        border_radius=border_radius,
    )

    if not svg_path:
        raise RuntimeError("SVG generation failed")

    print(f"✓ SVG created: {svg_path}")

    print("Generating favicon.ico...")

    ico_path = generator.generate_ico(
        svg_content=svg_path.read_text(encoding="utf-8"),
        output_path=svg_path.with_suffix(".ico"),
    )

    print(f"✓ ICO created: {ico_path}")


if __name__ == "__main__":
    main()
