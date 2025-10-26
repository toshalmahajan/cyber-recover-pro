#!/usr/bin/env python3
"""Report generation for forensic operations"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from rich.console import Console

console = Console()

class ReportGenerator:
    def __init__(self):
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_quick_report(self, scan_results: Dict, output_dir: str) -> str:
        """Generate a quick scan report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.report_dir / f"quick_scan_{timestamp}.json"
        
        report = {
            'metadata': {
                'tool': 'CyberRecover Pro',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat(),
                'scan_type': 'quick_scan'
            },
            'scan_parameters': {
                'source': scan_results['source'],
                'size_bytes': scan_results['size_bytes'],
                'output_directory': output_dir
            },
            'results': {
                'total_signatures_found': scan_results['total_signatures'],
                'files_detected': scan_results['files_found']
            },
            'summary': self._generate_summary(scan_results)
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"[green]📊 Report saved: {report_path}[/green]")
        return str(report_path)
    
    def generate_forensic_report(self, forensic_results: Dict, output_dir: str) -> str:
        """Generate comprehensive forensic report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.report_dir / f"forensic_report_{timestamp}.json"
        
        report = {
            'metadata': {
                'tool': 'CyberRecover Pro',
                'version': '2.0.0', 
                'timestamp': datetime.now().isoformat(),
                'scan_type': 'forensic_analysis'
            },
            'system_information': self._get_system_info(),
            'analysis_results': forensic_results,
            'findings': self._analyze_findings(forensic_results),
            'recommendations': self._generate_recommendations(forensic_results)
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also generate YAML version
        yaml_path = report_path.with_suffix('.yaml')
        with open(yaml_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False)
        
        console.print(f"[green]📋 Reports saved:[/green]")
        console.print(f"  JSON: [cyan]{report_path}[/cyan]")
        console.print(f"  YAML: [cyan]{yaml_path}[/cyan]")
        
        return str(report_path)
    
    def _generate_summary(self, scan_results: Dict) -> Dict:
        """Generate summary from scan results"""
        file_types = {}
        
        for file_info in scan_results['files_found']:
            file_type = file_info['type']
            if file_type not in file_types:
                file_types[file_type] = 0
            file_types[file_type] += 1
        
        return {
            'file_type_breakdown': file_types,
            'total_files_detected': len(scan_results['files_found']),
            'confidence_level': 'HIGH' if scan_results['files_found'] else 'LOW',
            'estimated_recovery_potential': f"{len(scan_results['files_found'])} files"
        }
    
    def _get_system_info(self) -> Dict:
        """Get system information for report"""
        import platform
        import psutil
        
        return {
            'operating_system': f"{platform.system()} {platform.release()}",
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 1),
            'disk_free_gb': round(psutil.disk_usage('.').free / (1024**3), 1)
        }
    
    def _analyze_findings(self, results: Dict) -> Dict:
        """Analyze forensic findings"""
        findings = {
            'data_recovery_potential': 'UNKNOWN',
            'disk_condition': 'UNKNOWN', 
            'file_system_integrity': 'UNKNOWN',
            'notable_artifacts': []
        }
        
        if 'source_info' in results:
            source_info = results['source_info']
            if 'size_bytes' in source_info:
                size_mb = source_info['size_bytes'] / (1024 * 1024)
                if size_mb > 1000:
                    findings['data_recovery_potential'] = 'HIGH'
                else:
                    findings['data_recovery_potential'] = 'MODERATE'
        
        return findings
    
    def _generate_recommendations(self, results: Dict) -> list:
        """Generate recommendations based on findings"""
        recommendations = [
            "Maintain chain of custody for forensic evidence",
            "Create multiple backups of recovered data",
            "Verify file integrity using cryptographic hashes",
            "Document all recovery procedures and findings"
        ]
        
        if results.get('deleted_files', {}).get('status') == 'simulated_carving':
            recommendations.append("Consider using specialized carving tools for deleted file recovery")
        
        return recommendations
    
    def display_report_summary(self, report_path: str):
        """Display a summary of the report"""
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            console.print(Panel.fit(
                f"[bold cyan]📋 Report Summary[/bold cyan]\n\n"
                f"Tool: [white]{report['metadata']['tool']}[/white]\n"
                f"Scan Type: [white]{report['metadata']['scan_type']}[/white]\n"
                f"Timestamp: [white]{report['metadata']['timestamp']}[/white]\n"
                f"Files Detected: [green]{report['results']['total_signatures_found']}[/green]",
                border_style="cyan"
            ))
            
        except Exception as e:
            console.print(f"[red]Error reading report: {e}[/red]")
