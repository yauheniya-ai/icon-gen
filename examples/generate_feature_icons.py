"""Generate AI model icons: Claude, OpenAI, Gemini, and DeepSeek."""
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from icon_gen_ai.generator import IconGenerator

def main():
    """Generate colored SVG icons for package features."""
    # Initialize generator
    generator = IconGenerator(output_dir="output")

    # Configuration
    color = 'white' 
    size = 24
    border_radius = 12
    bg_color = 'navy'
    category = 'feat'

    feature_icons = {
        f'{category}_ai': 'mingcute:search-2-ai-fill',
        f'{category}_python': 'devicon-plain:python',
        f'{category}_iconify': 'simple-icons:iconify',
        f'{category}_image': 'prime:image',
        f'{category}_customize': 'gridicons:customize',
        f'{category}_gradient': 'carbon:gradient',
        f'{category}_save': 'heroicons-outline:save-as',
    }
    
    # Generate all icons with specified parameters
    generated = generator.generate_batch(feature_icons, color=color, size=size, bg_color=bg_color, border_radius=border_radius)
    
    # Summary
    print(f"Successfully generated {len(generated)}/{len(feature_icons)} icons:")
    for path in generated:
        print(f"  ✓ {path.name}")
    
    if len(generated) < len(feature_icons):
        print(f"\n⚠ Failed to generate {len(feature_icons) - len(generated)} icon(s)")


if __name__ == "__main__":
    main()