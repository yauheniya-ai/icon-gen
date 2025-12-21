"""Core icon generation logic using Iconify API and direct URLs."""

import requests
import re
from pathlib import Path
from typing import Optional, Literal
from xml.etree import ElementTree as ET

FormatType = Literal['svg', 'png', 'webp']


class IconGenerator:
    """Generate and customize icons from Iconify or direct URLs."""
    
    ICONIFY_API = "https://api.iconify.design"
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the icon generator.
        
        Args:
            output_dir: Directory where icons will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def modify_svg(
        self, 
        svg_content: str, 
        color: Optional[str] = None, 
        size: Optional[int] = None
    ) -> str:
        """Modify SVG content to apply color and size.
        
        Args:
            svg_content: Original SVG content
            color: Color to apply (e.g., 'white', '#ffffff')
            size: Size in pixels (applies to both width and height)
            
        Returns:
            Modified SVG content
        """
        try:
            # Parse SVG
            root = ET.fromstring(svg_content)
            
            # Apply color
            if color:
                # Set fill attribute on root
                root.set('fill', color)
                
                # Also modify existing fill attributes in paths and other elements
                for elem in root.iter():
                    # Skip elements that should keep their fill
                    if elem.get('fill') and elem.get('fill').lower() != 'none':
                        elem.set('fill', color)
                    # Also handle stroke for outlined icons
                    if elem.get('stroke'):
                        elem.set('stroke', color)
            
            # Apply size
            if size:
                root.set('width', str(size))
                root.set('height', str(size))
                # Preserve viewBox if it exists, otherwise create one
                if not root.get('viewBox'):
                    # Try to get original dimensions
                    orig_width = root.get('width', '24')
                    orig_height = root.get('height', '24')
                    # Remove 'px' or other units
                    orig_width = re.sub(r'[^0-9.]', '', str(orig_width))
                    orig_height = re.sub(r'[^0-9.]', '', str(orig_height))
                    root.set('viewBox', f'0 0 {orig_width} {orig_height}')
            
            # Convert back to string
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            print(f"Warning: Could not modify SVG: {e}")
            return svg_content
    
    def get_icon_from_url(self, url: str) -> Optional[str]:
        """Fetch icon/image from a direct URL.
        
        Args:
            url: Direct URL to the icon/image
            
        Returns:
            Content as string (for SVG) or bytes (for images), or None if request fails
        """
        # Add headers to avoid 403 errors from sites like Wikipedia
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Return text for SVG, bytes for images
            if 'svg' in response.headers.get('Content-Type', '').lower():
                return response.text
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching from URL {url}: {e}")
            return None
    
    def get_icon_svg(self, icon_name: str, color: str = "white") -> Optional[str]:
        """Fetch SVG icon from Iconify API.
        
        Args:
            icon_name: Icon identifier (e.g., 'mdi:github', 'simple-icons:openai')
            color: Color for the icon (default: white)
            
        Returns:
            SVG content as string, or None if request fails
        """
        # Iconify API endpoint for SVG with color
        url = f"{self.ICONIFY_API}/{icon_name}.svg"
        params = {'color': color}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching icon {icon_name}: {e}")
            return None
    
    def save_svg(self, svg_content: str, output_path: Path) -> bool:
        """Save SVG content to file.
        
        Args:
            svg_content: SVG markup as string
            output_path: Path where to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(svg_content, encoding='utf-8')
            print(f"✓ Saved: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving {output_path}: {e}")
            return False
    
    def generate_icon(
        self,
        icon_name: str,
        output_name: Optional[str] = None,
        color: Optional[str] = None,
        size: Optional[int] = None,
        format: FormatType = 'svg',
        direct_url: Optional[str] = None
    ) -> Optional[Path]:
        """Generate and save an icon.
        
        Args:
            icon_name: Icon identifier from Iconify (ignored if direct_url is provided)
            output_name: Custom output filename (without extension)
            color: Icon color (applies to both Iconify and direct URLs)
            size: Icon size in pixels (applies to both Iconify and direct URLs)
            format: Output format (currently only 'svg' supported)
            direct_url: If provided, fetch icon from this URL instead of Iconify
            
        Returns:
            Path to saved file, or None if failed
        """
        if format != 'svg':
            print(f"Warning: Format '{format}' not yet implemented, using SVG")
        
        # Fetch the icon
        if direct_url:
            svg_content = self.get_icon_from_url(direct_url)
            # Apply modifications to direct URL SVGs
            if svg_content and (color or size):
                svg_content = self.modify_svg(svg_content, color, size)
        else:
            # For Iconify, color is handled by API but size needs manual modification
            svg_content = self.get_icon_svg(icon_name, color or "currentColor")
            if svg_content and size:
                svg_content = self.modify_svg(svg_content, None, size)
        
        if not svg_content:
            return None
        
        # Determine output filename
        if output_name is None:
            # Use the icon name, replacing ':' with '_'
            output_name = icon_name.replace(':', '_').replace('/', '_')
        
        output_path = self.output_dir / f"{output_name}.svg"
        
        # Save the file
        if self.save_svg(svg_content, output_path):
            return output_path
        return None
    
    def generate_batch(
        self, 
        icons: dict[str, str | dict], 
        color: Optional[str] = None,
        size: Optional[int] = None
    ) -> list[Path]:
        """Generate multiple icons at once.
        
        Args:
            icons: Dictionary mapping output names to either:
                   - Icon identifiers (string)
                   - Dict with 'icon', 'url', 'color', 'size' keys
            color: Default color for all icons (can be overridden per-icon)
            size: Default size for all icons (can be overridden per-icon)
            
        Returns:
            List of paths to successfully generated icons
        """
        results = []
        for output_name, icon_config in icons.items():
            print(f"\nGenerating {output_name}...")
            
            # Handle different config formats
            if isinstance(icon_config, str):
                # Simple string: treat as icon name
                path = self.generate_icon(icon_config, output_name, color, size)
            elif isinstance(icon_config, dict):
                # Dict: can have 'icon', 'url', 'color', 'size'
                icon_name = icon_config.get('icon', '')
                direct_url = icon_config.get('url')
                icon_color = icon_config.get('color', color)
                icon_size = icon_config.get('size', size)
                path = self.generate_icon(
                    icon_name, 
                    output_name, 
                    icon_color,
                    icon_size,
                    direct_url=direct_url
                )
            else:
                print(f"Invalid config for {output_name}")
                continue
            
            if path:
                results.append(path)
        return results