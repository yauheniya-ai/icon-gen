"""Generate animated icons"""
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from icon_gen_ai.generator import IconGenerator


def main():
    """Generate animated SVG icons"""
    # Initialize generator
    generator = IconGenerator(output_dir="output")

    # Configuration
    cat1 = 'ani_embedded'
    cat2 = 'ani_custom'
    size = 256
    border_radius=48

    # Icons with embedded animations
    icons_with_embedded_ani = {
        f'{cat1}_blocks': 'svg-spinners:blocks-wave',
        f'{cat1}_upload': 'line-md:upload-outline-loop',
        f'{cat1}_location': 'line-md:my-location-loop',
        f'{cat1}_bars': 'svg-spinners:bars-scale'
    }
    
    # Generate all icons with specified color and size
    generated = generator.generate_batch(
        icons_with_embedded_ani, 
        color='mediumslateblue', 
        size=size, 
        outline_color='springgreen', 
        bg_color='snow', 
        outline_width=8, 
        border_radius=border_radius)
    
    # Summary
    print(f"Successfully generated {len(generated)}/{len(icons_with_embedded_ani)} icons:")
    for path in generated:
        print(f"  ✓ {path.name}")
    
    if len(generated) < len(icons_with_embedded_ani):
        print(f"\n⚠ Failed to generate {len(icons_with_embedded_ani) - len(generated)} icon(s)")

    # Create custom animations
    icons_with_custom_ani = {
        f'{cat2}_disk': {'icon':'qlementine-icons:disk-16',"animation":"spin:4s"},
        f'{cat2}_circle': {'icon':'clarity:dot-circle-line',"animation":"pulse:1s"},
        f'{cat2}_coffee': {'icon':'gg:coffee',"animation":"flip-h:1s"},
        f'{cat2}_card': {'icon':'famicons:card-outline',"animation":"flip-v:1s"},
    }
    
    # Generate all icons with specified color and size
    generated = generator.generate_batch(
        icons_with_custom_ani, 
        color='white', 
        size=size,  
        bg_color=('deeppink','deepskyblue'), 
        border_radius=border_radius)
    
    # Summary
    print(f"Successfully generated {len(generated)}/{len(icons_with_custom_ani)} icons:")
    for path in generated:
        print(f"  ✓ {path.name}")
    
    if len(generated) < len(icons_with_custom_ani):
        print(f"\n⚠ Failed to generate {len(icons_with_custom_ani) - len(generated)} icon(s)")

if __name__ == "__main__":
    main()