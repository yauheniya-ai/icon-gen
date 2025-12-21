# icon-gen

Generate customizable icons from Iconify with easy export to PNG, SVG, WebP formats.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Features

- 🎨 Access 200,000+ icons from Iconify
- 🎯 Customize colors and sizes
- 📦 Export to SVG format
- 🚀 Simple and intuitive API
- 🔧 CLI support (coming soon)

## Installation
```bash
pip install icon-gen
```

## Quick Start
```python
from icon_gen import IconGenerator

# Initialize generator
generator = IconGenerator(output_dir="output")

# Generate a single icon
generator.generate_icon(
    'simple-icons:openai',
    output_name='openai',
    color='white',
    size=256
)

# Generate multiple icons at once
icons = {
    'github': 'mdi:github',
    'twitter': 'mdi:twitter',
    'python': 'mdi:language-python',
}
generator.generate_batch(icons, color='white', size=256)

# Use direct URLs for icons not in Iconify
custom_icons = {
    'custom': {
        'url': 'https://example.com/icon.svg',
        'color': 'blue',
        'size': 512
    }
}
generator.generate_batch(custom_icons)
```

## Finding Icons

Browse available icons at [Iconify](https://icon-sets.iconify.design/)

Icon naming format: `collection:icon-name`
- `simple-icons:openai` - Company logos
- `mdi:github` - Material Design Icons
- `fa6-solid:scale-balanced` - Font Awesome icons
- `heroicons:scale` - HeroIcons

## Examples

Check out the `examples/` directory for more use cases:
- `generate_ai_icons.py` - Generate AI model icons (Claude, OpenAI, Gemini)
- `generate_judge_icon.py` - Generate legal/law icons

## Development
```bash
# Clone the repository
git clone https://github.com/yauheniya-ai/icon-gen.git
cd icon-gen

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see LICENSE file for details

## Author

Yauheniya Varabyova (yauheniya.ai@gmail.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.