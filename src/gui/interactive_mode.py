#!/usr/bin/env python3
"""Interactive mode with menu-driven interface"""

import questionary
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from core.advanced_carver import AdvancedFileCarver
from core.disk_forensics import DiskForensics
from utils.system_manager import SystemManager

console = Console()

class InteractiveMode:
    def __init__(self):
        self.carver = AdvancedFileCarver()
        self.forensics = DiskForensics()
        self.system = SystemManager()
        
    def run(self):
        """Run the interactive mode"""
        while True:
            choice = self.main_menu()
            
            if choice == "Quick Scan":
                self.quick_scan_flow()
            elif choice == "Deep Forensic Scan":
                self.deep_scan_flow()
            elif choice == "System Information":
                self.system_info_flow()
            elif choice == "File Carving":
                self.file_carving_flow()
            elif choice == "Partition Analysis":
                self.partition_analysis_flow()
            elif choice == "Exit":
                console.print("[green]👋 Thank you for using CyberRecover Pro![/green]")
                break
    
    def main_menu(self):
        """Display main menu"""
        console.print(Panel.fit(
            "[bold cyan]CyberRecover Pro - Main Menu[/bold cyan]",
            border_style="blue"
        ))
        
        return questionary.select(
            "What would you like to do?",
            choices=[
                "Quick Scan",
                "Deep Forensic Scan", 
                "File Carving",
                "Partition Analysis",
                "System Information",
                "Exit"
            ]
        ).ask()
    
    def quick_scan_flow(self):
        """Quick scan workflow"""
        console.print(Panel.fit(
            "[bold green]🚀 Quick File Scan[/bold green]\n"
            "Fast signature-based file detection",
            border_style="green"
        ))
        
        source = questionary.text("Enter source path (disk image or device):").ask()
        if not source:
            return
            
        output = questionary.text("Enter output directory:", default="./recovered").ask()
        
        try:
            results = self.carver.quick_scan(source)
            self.display_quick_scan_results(results)
        except Exception as e:
            console.print(f"[red]Error during quick scan: {e}[/red]")
    
    def deep_scan_flow(self):
        """Deep scan workflow"""
        console.print(Panel.fit(
            "[bold yellow]🔍 Deep Forensic Scan[/bold yellow]\n"
            "Comprehensive forensic analysis with file recovery",
            border_style="yellow"
        ))
        
        source = questionary.text("Enter source path:").ask()
        output = questionary.text("Enter output directory:", default="./forensic_recovery").ask()
        
        carve_deleted = questionary.confirm("Carve deleted files?").ask()
        
        try:
            results = self.forensics.deep_scan(source, output, carve_deleted)
            console.print(Panel.fit(
                f"[green]✅ Deep scan completed![/green]\n"
                f"Recovered files saved to: [cyan]{output}[/cyan]",
                border_style="green"
            ))
        except Exception as e:
            console.print(f"[red]Error during deep scan: {e}[/red]")
    
    def system_info_flow(self):
        """System information workflow"""
        console.print(Panel.fit(
            "[bold blue]💻 System Information[/bold blue]",
            border_style="blue"
        ))
        
        self.forensics.display_partitions()
        
        info = self.system.get_detailed_system_info()
        console.print(Panel.fit(
            f"[bold]Detailed System Info[/bold]\n\n"
            f"OS: [cyan]{info['os']}[/cyan]\n"
            f"Kernel: [cyan]{info['kernel']}[/cyan]\n"
            f"Architecture: [cyan]{info['architecture']}[/cyan]\n"
            f"Python: [cyan]{info['python_version']}[/cyan]\n"
            f"RAM: [cyan]{info['ram_gb']} GB[/cyan]\n"
            f"CPU Cores: [cyan]{info['cpu_cores']}[/cyan]\n"
            f"Disk Free: [cyan]{info['free_disk_gb']} GB[/cyan]",
            title="System Overview"
        ))
    
    def file_carving_flow(self):
        """File carving capabilities display"""
        console.print(Panel.fit(
            "[bold magenta]🛠️ File Carving Capabilities[/bold magenta]",
            border_style="magenta"
        ))
        
        self.carver.display_capabilities()
        
        if questionary.confirm("Perform test carving on sample data?").ask():
            self.test_carving_flow()
    
    def partition_analysis_flow(self):
        """Partition analysis workflow"""
        console.print(Panel.fit(
            "[bold red]💾 Partition Analysis[/bold red]",
            border_style="red"
        ))
        
        self.forensics.display_partitions()
    
    def test_carving_flow(self):
        """Test carving workflow"""
        console.print("[yellow]🧪 Creating test environment...[/yellow]")
        
        from utils.test_environment import TestEnvironment
        test_env = TestEnvironment()
        test_path = test_env.create_test_image()
        
        console.print(f"[green]✅ Test image created: {test_path}[/green]")
        
        if questionary.confirm("Perform quick scan on test image?").ask():
            results = self.carver.quick_scan(test_path)
            self.display_quick_scan_results(results)
    
    def display_quick_scan_results(self, results):
        """Display quick scan results in formatted way"""
        console.print(Panel.fit(
            f"[bold green]📊 Quick Scan Results[/bold green]\n\n"
            f"Source: [cyan]{results['source']}[/cyan]\n"
            f"Size: [cyan]{results['size_bytes']} bytes[/cyan]\n"
            f"Files Found: [cyan]{results['total_signatures']}[/cyan]\n"
            f"Scan Type: [cyan]{results['scan_type']}[/cyan]",
            border_style="green"
        ))
        
        if results['files_found']:
            from rich.table import Table
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Type")
            table.add_column("Extension") 
            table.add_column("Description")
            table.add_column("Position")
            table.add_column("Confidence")
            
            for file_info in results['files_found'][:10]:  # Show first 10
                table.add_row(
                    file_info['type'],
                    file_info['extension'],
                    file_info['description'],
                    hex(file_info['position']),
                    file_info['confidence']
                )
            
            console.print(table)
            
            if len(results['files_found']) > 10:
                console.print(f"[dim]... and {len(results['files_found']) - 10} more files[/dim]")
        else:
            console.print("[yellow]No file signatures found in the source.[/yellow]")
