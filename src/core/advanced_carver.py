#!/usr/bin/env python3
"""Advanced file carving with multiple techniques"""

import os
import struct
import magic
from pathlib import Path
from typing import Dict, List, Tuple
from rich.console import Console
from rich.progress import track
import hashlib

console = Console()

class AdvancedFileCarver:
    def __init__(self):
        self.signatures = self._load_signatures()
        self.mime = magic.Magic(mime=True)
        
    def _load_signatures(self) -> Dict[bytes, Dict]:
        """Load comprehensive file signatures database"""
        return {
            # Images
            b'\xFF\xD8\xFF\xE0': {'ext': 'jpg', 'type': 'image', 'description': 'JPEG Image'},
            b'\xFF\xD8\xFF\xE1': {'ext': 'jpg', 'type': 'image', 'description': 'JPEG Image (EXIF)'},
            b'\x89\x50\x4E\x47': {'ext': 'png', 'type': 'image', 'description': 'PNG Image'},
            b'\x47\x49\x46\x38': {'ext': 'gif', 'type': 'image', 'description': 'GIF Image'},
            b'\x42\x4D': {'ext': 'bmp', 'type': 'image', 'description': 'BMP Image'},
            b'\x49\x49\x2A\x00': {'ext': 'tif', 'type': 'image', 'description': 'TIFF Image'},
            
            # Documents
            b'\x25\x50\x44\x46': {'ext': 'pdf', 'type': 'document', 'description': 'PDF Document'},
            b'\x50\x4B\x03\x04': {'ext': 'zip', 'type': 'archive', 'description': 'ZIP Archive'},
            b'\x50\x4B\x05\x06': {'ext': 'zip', 'type': 'archive', 'description': 'ZIP Archive (empty)'},
            b'\x50\x4B\x07\x08': {'ext': 'zip', 'type': 'archive', 'description': 'ZIP Archive (spanned)'},
            b'\x52\x61\x72\x21': {'ext': 'rar', 'type': 'archive', 'description': 'RAR Archive'},
            b'\x37\x7A\xBC\xAF': {'ext': '7z', 'type': 'archive', 'description': '7-Zip Archive'},
            b'\xD0\xCF\x11\xE0': {'ext': 'doc', 'type': 'document', 'description': 'Microsoft Office'},
            b'\x50\x4B\x03\x04': {'ext': 'docx', 'type': 'document', 'description': 'Microsoft Office (new)'},
            
            # Audio/Video
            b'\x49\x44\x33': {'ext': 'mp3', 'type': 'audio', 'description': 'MP3 Audio'},
            b'\xFF\xFB': {'ext': 'mp3', 'type': 'audio', 'description': 'MP3 Audio (no ID3)'},
            b'\x52\x49\x46\x46': {'ext': 'avi', 'type': 'video', 'description': 'AVI Video'},
            b'\x66\x74\x79\x70': {'ext': 'mp4', 'type': 'video', 'description': 'MP4 Video'},
            b'\x1A\x45\xDF\xA3': {'ext': 'mkv', 'type': 'video', 'description': 'Matroska Video'},
            
            # Executables
            b'\x7F\x45\x4C\x46': {'ext': 'elf', 'type': 'executable', 'description': 'ELF Executable'},
            b'\x4D\x5A': {'ext': 'exe', 'type': 'executable', 'description': 'Windows Executable'},
            b'\xCA\xFE\xBA\xBE': {'ext': 'class', 'type': 'executable', 'description': 'Java Class'},
            
            # Database
            b'\x53\x51\x4C\x69': {'ext': 'sqlite', 'type': 'database', 'description': 'SQLite Database'},
            
            # Text files with BOM
            b'\xEF\xBB\xBF': {'ext': 'txt', 'type': 'text', 'description': 'UTF-8 Text'},
            b'\xFF\xFE': {'ext': 'txt', 'type': 'text', 'description': 'UTF-16 LE Text'},
            b'\xFE\xFF': {'ext': 'txt', 'type': 'text', 'description': 'UTF-16 BE Text'},
        }
    
    def quick_scan(self, source_path: str) -> Dict:
        """Perform quick signature-based scan"""
        console.print(f"[bold blue]🔍 Quick Scanning: {source_path}[/bold blue]")
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source_path}")
        
        file_size = os.path.getsize(source_path)
        found_files = []
        
        with open(source_path, 'rb') as f:
            # Read first 1MB for quick scan
            data = f.read(1024 * 1024)
            
            for signature, info in self.signatures.items():
                if signature in data:
                    positions = self._find_all_occurrences(data, signature)
                    for pos in positions:
                        found_files.append({
                            'signature': signature.hex(),
                            'type': info['type'],
                            'extension': info['ext'],
                            'description': info['description'],
                            'position': pos,
                            'confidence': 'high'
                        })
        
        return {
            'source': source_path,
            'size_bytes': file_size,
            'files_found': found_files,
            'scan_type': 'quick',
            'total_signatures': len(found_files)
        }
    
    def deep_carve(self, source_path: str, output_dir: str) -> Dict:
        """Perform deep file carving with actual file extraction"""
        console.print(f"[bold red]🔄 Deep Carving: {source_path}[/bold red]")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        recovered_files = []
        file_size = os.path.getsize(source_path)
        
        with open(source_path, 'rb') as source_file:
            data = source_file.read()
            
            for signature, info in track(self.signatures.items(), description="Carving files..."):
                positions = self._find_all_occurrences(data, signature)
                
                for i, pos in enumerate(positions):
                    file_data = self._extract_file_data(data, pos, signature, info['ext'])
                    if file_data:
                        # Create unique filename
                        filename = f"carved_{info['ext']}_{pos:08x}_{i}.{info['ext']}"
                        filepath = output_path / filename
                        
                        # Save file
                        with open(filepath, 'wb') as f:
                            f.write(file_data)
                        
                        # Calculate hashes
                        file_hash = hashlib.sha256(file_data).hexdigest()
                        
                        recovered_files.append({
                            'filename': filename,
                            'type': info['type'],
                            'extension': info['ext'],
                            'size': len(file_data),
                            'hash_sha256': file_hash,
                            'original_position': pos,
                            'description': info['description']
                        })
        
        return {
            'recovered_files': recovered_files,
            'total_recovered': len(recovered_files),
            'output_directory': str(output_path)
        }
    
    def _find_all_occurrences(self, data: bytes, pattern: bytes) -> List[int]:
        """Find all occurrences of a pattern in data"""
        positions = []
        start = 0
        while True:
            pos = data.find(pattern, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        return positions
    
    def _extract_file_data(self, data: bytes, position: int, signature: bytes, extension: str) -> bytes:
        """Extract file data based on signature and file type"""
        # Simple extraction - in real implementation, you'd use proper file boundaries
        if extension in ['jpg', 'png', 'gif']:
            # For images, extract reasonable chunk
            return data[position:position + 1024 * 1024]  # 1MB max for demo
        
        elif extension in ['pdf', 'docx']:
            return data[position:position + 10 * 1024 * 1024]  # 10MB max
        
        elif extension in ['zip', 'rar']:
            return data[position:position + 5 * 1024 * 1024]  # 5MB max
        
        else:
            return data[position:position + 512 * 1024]  # 512KB default
    
    def display_capabilities(self):
        """Display all supported file types"""
        table = Table(title="Supported File Types", show_header=True)
        table.add_column("Extension", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Description", style="white")
        table.add_column("Signature", style="yellow")
        
        for sig, info in self.signatures.items():
            table.add_row(
                info['ext'],
                info['type'],
                info['description'],
                sig.hex().upper()
            )
        
        console.print(table)
