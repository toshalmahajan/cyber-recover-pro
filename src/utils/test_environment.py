#!/usr/bin/env python3
"""Test environment creation for development and demonstration"""

import os
import random
from pathlib import Path
from rich.console import Console

console = Console()

class TestEnvironment:
    def __init__(self):
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
    
    def create_test_image(self) -> str:
        """Create a test disk image with various file signatures"""
        test_path = self.test_dir / "forensic_test.img"
        
        # Create a mix of file signatures and random data
        signatures = [
            b'\xFF\xD8\xFF\xE0' + b'JPEG' * 100,  # JPEG
            b'\x89\x50\x4E\x47' + b'PNG_' * 100,   # PNG
            b'\x25\x50\x44\x46' + b'PDF_' * 100,   # PDF
            b'\x50\x4B\x03\x04' + b'ZIP_' * 100,   # ZIP
            b'\x49\x44\x33' + b'MP3_' * 100,       # MP3
            b'\x52\x61\x72\x21' + b'RAR_' * 100,   # RAR
        ]
        
        # Add some random data between signatures
        with open(test_path, 'wb') as f:
            for i, signature in enumerate(signatures):
                # Add random data before signature
                f.write(os.urandom(random.randint(100, 1000)))
                # Add the file signature
                f.write(signature)
                # Add more random data
                f.write(os.urandom(random.randint(500, 2000)))
            
            console.print(f"[green]✅ Created test image: {test_path}[/green]")
            console.print(f"[dim]Size: {test_path.stat().st_size} bytes[/dim]")
        
        return str(test_path)
    
    def create_complete_test_environment(self) -> list:
        """Create multiple test images for comprehensive testing"""
        test_images = []
        
        # Small test image
        small_test = self.test_dir / "small_test.img"
        self._create_simple_test_image(small_test, 1024 * 1024)  # 1MB
        test_images.append(str(small_test))
        
        # Medium test image  
        medium_test = self.test_dir / "medium_test.img"
        self._create_simple_test_image(medium_test, 5 * 1024 * 1024)  # 5MB
        test_images.append(str(medium_test))
        
        # Complex test image with various signatures
        complex_test = self.test_dir / "complex_test.img"
        self._create_complex_test_image(complex_test, 10 * 1024 * 1024)  # 10MB
        test_images.append(str(complex_test))
        
        console.print(Panel.fit(
            f"[bold green]🧪 Test Environment Created[/bold green]\n\n"
            f"Test images available:\n"
            f"• [cyan]{small_test.name}[/cyan] - 1MB (Basic)\n"
            f"• [cyan]{medium_test.name}[/cyan] - 5MB (Standard)\n"  
            f"• [cyan]{complex_test.name}[/cyan] - 10MB (Advanced)",
            border_style="green"
        ))
        
        return test_images
    
    def _create_simple_test_image(self, path: Path, size: int):
        """Create a simple test image with basic signatures"""
        with open(path, 'wb') as f:
            # Write some file signatures at random positions
            signatures = [
                b'\xFF\xD8\xFF\xE0',  # JPEG
                b'\x89\x50\x4E\x47',   # PNG
                b'\x25\x50\x44\x46',   # PDF
            ]
            
            data = bytearray(size)
            
            # Insert signatures at random positions
            for signature in signatures:
                pos = random.randint(0, size - len(signature) - 1)
                data[pos:pos+len(signature)] = signature
            
            f.write(data)
    
    def _create_complex_test_image(self, path: Path, size: int):
        """Create a complex test image with multiple file types"""
        with open(path, 'wb') as f:
            current_pos = 0
            
            # Add different file types in sequence
            file_structures = [
                (b'\xFF\xD8\xFF\xE0', b'JPEG_DATA', 50 * 1024),  # JPEG - 50KB
                (b'\x89\x50\x4E\x47', b'PNG_DATA_', 100 * 1024), # PNG - 100KB
                (b'\x25\x50\x44\x46', b'PDF_CONTENT', 200 * 1024), # PDF - 200KB
                (b'\x50\x4B\x03\x04', b'ZIP_ARCHIVE', 150 * 1024), # ZIP - 150KB
                (b'\x52\x61\x72\x21', b'RAR_FILE__', 80 * 1024),  # RAR - 80KB
            ]
            
            for signature, pattern, file_size in file_structures:
                if current_pos + file_size > size:
                    break
                    
                # Write signature
                f.write(signature)
                current_pos += len(signature)
                
                # Write file content pattern
                pattern_repeats = file_size // len(pattern)
                for _ in range(pattern_repeats):
                    if current_pos + len(pattern) > size:
                        break
                    f.write(pattern)
                    current_pos += len(pattern)
                
                # Add some random data between files
                gap_size = random.randint(1024, 10 * 1024)
                if current_pos + gap_size < size:
                    f.write(os.urandom(gap_size))
                    current_pos += gap_size
            
            # Fill remaining space with random data
            remaining = size - current_pos
            if remaining > 0:
                f.write(os.urandom(remaining))
    
    def cleanup_test_environment(self):
        """Clean up test files"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
            console.print("[yellow]🧹 Test environment cleaned up[/yellow]")
