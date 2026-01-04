"""Generate AI model icons with custom backgrounds and gradients (one by one)."""
from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from icon_gen_ai.generator import IconGenerator


def main():
    """Generate AI icons with custom backgrounds and colors."""
    # Initialize generator
    generator = IconGenerator(output_dir="output")
    
    print("=" * 70)
    print("AI Model Icon Generator - Individual Icon Generation")
    print("=" * 70)
    print(f"Output directory: {generator.output_dir.absolute()}")
    print()
    
    generated = []
    
    # 1. Claude: White icon on mediumslateblue square background
    print("Generating Claude...")
    result = generator.generate_icon(
        direct_url='https://upload.wikimedia.org/wikipedia/commons/b/b0/Claude_AI_symbol.svg',
        output_name='claude_white_mediumslateblue_bg',
        color='white',
        bg_color='mediumslateblue',
        border_radius=0,  # Square
        size=256
    )
    if result:
        generated.append(result)
        print(f"  ✓ {result.name}")
    
    # 2. Gemini: White icon on deeppink circular background
    print("\nGenerating Gemini...")
    result = generator.generate_icon(
        icon_name='simple-icons:googlegemini',
        output_name='gemini_white_deeppink_bg',
        color='white',
        bg_color='deeppink',
        border_radius=128,  # Circle (half of size)
        size=256
    )
    if result:
        generated.append(result)
        print(f"  ✓ {result.name}")
    
    # 3. Mistral: White icon on gradient rounded background
    print("\nGenerating Mistral...")
    result = generator.generate_icon(
        icon_name='simple-icons:mistralai',
        output_name='mistral_white_gradient_bg',
        color='white',
        bg_color=('mediumslateblue', 'deeppink'),  # Gradient
        border_radius=48,  # Rounded corners
        size=256
    )
    if result:
        generated.append(result)
        print(f"  ✓ {result.name}")
    
    # 4. OpenAI: Gradient icon on transparent background
    print("\nGenerating OpenAI...")
    result = generator.generate_icon(
        icon_name='simple-icons:openai',
        output_name='openai_gradient_transparent_bg',
        color=('mediumslateblue', 'deeppink'),  # Gradient icon
        bg_color=None,  # Transparent background
        size=256
    )
    if result:
        generated.append(result)
        print(f"  ✓ {result.name}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✓ Successfully generated {len(generated)}/4 icons")
    print("=" * 70)


if __name__ == "__main__":
    main()
    