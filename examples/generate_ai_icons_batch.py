"""Generate AI model icons: Claude, OpenAI, Gemini, and DeepSeek."""
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from icon_gen.generator import IconGenerator


def main():
    """Generate colored SVG icons for major AI models."""
    # Initialize generator
    generator = IconGenerator(output_dir="output")

    # Configuration
    color = 'deepskyblue'  # Blue color
    size = 256

    # Define the AI model icons we want
    ai_icons = {
        f'llama_{color}': 'simple-icons:meta',
        f'deepseek_{color}': {
            'local_file': 'input/deepseek-icon.png'
        },
        f'nemotron_{color}': {
            'url': 'https://companieslogo.com/img/orig/NVDA-df4c2377.svg'
        },
        f'grok_{color}': {
            'url': 'https://unpkg.com/@lobehub/icons-static-svg@latest/icons/grok.svg'
        }
    }
    

    
    print("=" * 60)
    print("AI Model Icon Generator")
    print("=" * 60)
    print(f"Output directory: {generator.output_dir.absolute()}")
    print(f"Color: {color}")
    print(f"Size: {size}px")
    print(f"Format: SVG")
    print()
    
    # Generate all icons with specified color and size
    generated = generator.generate_batch(ai_icons, color=color, size=size, outline_color=color, outline_width=8, border_radius=48)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Successfully generated {len(generated)}/{len(ai_icons)} icons:")
    for path in generated:
        print(f"  ✓ {path.name}")
    
    if len(generated) < len(ai_icons):
        print(f"\n⚠ Failed to generate {len(ai_icons) - len(generated)} icon(s)")
    
    print("=" * 60)


if __name__ == "__main__":
    main()