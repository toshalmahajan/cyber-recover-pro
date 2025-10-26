#!/usr/bin/env python3
"""Advanced disk forensics capabilities"""

import os
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.table import Table

console = Console()

class DiskForensics:
    def __init__(self):
        self.console = console
        
    def deep_scan(self, source_path: str, output_dir: str, carve_deleted: bool = False) -> Dict:
        """Perform comprehensive forensic analysis"""
        self.console.print(f"[bold green]🔬 Starting Deep Forensic Analysis[/bold green]")
        
        results = {
            'source_info': self._get_source_info(source_path),
            'file_system_analysis': self._analyze_file_system(source_path),
            'recovery_results': {},
            'forensic_artifacts': {}
        }
        
        if carve_deleted:
            self.console.print("[yellow]�� Carving deleted files...[/yellow]")
            results['deleted_files'] = self._carve_deleted_files(source_path, output_dir)
        
        return results
    
    def _get_source_info(self, source_path: str) -> Dict:
        """Get detailed information about the source"""
        path = Path(source_path)
        
        if not path.exists():
            return {'error': 'Source path does not exist'}
        
        stats = path.stat()
        
        return {
            'path': str(path.absolute()),
            'size_bytes': stats.st_size,
            'size_human': self._bytes_to_human(stats.st_size),
            'created': stats.st_ctime,
            'modified': stats.st_mtime,
            'is_file': path.is_file(),
            'is_block_device': path.is_block_device()
        }
    
    def _analyze_file_system(self, source_path: str) -> Dict:
        """Analyze file system structure"""
        try:
            # Use file command to detect file system type
            result = subprocess.run(
                ['file', source_path],
                capture_output=True, text=True
            )
            
            file_info = result.stdout.strip()
            
            return {
                'file_type': file_info,
                'analysis': 'Basic file system analysis completed'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _carve_deleted_files(self, source_path: str, output_dir: str) -> Dict:
        """Carve deleted files from disk image"""
        # This would integrate with tools like photorec, scalpel, or foremost
        # For now, we'll simulate this functionality
        
        return {
            'method': 'signature_based_carving',
            'tools_available': self._check_forensic_tools(),
            'status': 'simulated_carving',
            'note': 'Integrate with actual carving tools in production'
        }
    
    def _check_forensic_tools(self) -> List[str]:
        """Check availability of forensic tools"""
        tools = ['file', 'strings', 'hexdump', 'dd']
        available = []
        
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], capture_output=True)
                available.append(tool)
            except:
                pass
                
        return available
    
    def _bytes_to_human(self, size_bytes: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def list_partitions(self) -> List[Dict]:
        """List all available partitions"""
        partitions = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_size': self._bytes_to_human(usage.total),
                    'used': self._bytes_to_human(usage.used),
                    'free': self._bytes_to_human(usage.free),
                    'percent_used': usage.percent
                })
            except PermissionError:
                # Some partitions may not be accessible
                continue
        
        return partitions
    
    def display_partitions(self):
        """Display partitions in a formatted table"""
        partitions = self.list_partitions()
        
        table = Table(title="System Partitions", show_header=True)
        table.add_column("Device", style="cyan")
        table.add_column("Mount Point", style="green")
        table.add_column("File System", style="yellow")
        table.add_column("Total Size", justify="right")
        table.add_column("Free Space", justify="right")
        table.add_column("Used %", justify="right")
        
        for part in partitions:
            table.add_row(
                part['device'],
                part['mountpoint'],
                part['fstype'],
                part['total_size'],
                part['free'],
                f"{part['percent_used']}%"
            )
        
        self.console.print(table)
