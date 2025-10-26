#!/usr/bin/env python3
"""System management and monitoring utilities"""

import platform
import psutil
import sys
import os
from typing import Dict
from rich.console import Console

console = Console()

class SystemManager:
    def __init__(self):
        self.console = console
    
    def get_detailed_system_info(self) -> Dict:
        """Get comprehensive system information"""
        try:
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # CPU information
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            
            # System information
            system_info = {
                'os': f"{platform.system()} {platform.release()}",
                'kernel': platform.version(),
                'architecture': platform.machine(),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'ram_gb': round(memory.total / (1024 ** 3), 2),
                'ram_used_gb': round(memory.used / (1024 ** 3), 2),
                'ram_free_gb': round(memory.available / (1024 ** 3), 2),
                'swap_total_gb': round(swap.total / (1024 ** 3), 2),
                'swap_used_gb': round(swap.used / (1024 ** 3), 2),
                'disk_total_gb': round(disk.total / (1024 ** 3), 2),
                'disk_used_gb': round(disk.used / (1024 ** 3), 2),
                'free_disk_gb': round(disk.free / (1024 ** 3), 2),
                'cpu_cores': cpu_cores,
                'cpu_threads': cpu_threads,
                'cpu_usage': psutil.cpu_percent(interval=1),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'
            }
            
            return system_info
            
        except Exception as e:
            return {'error': f"Could not gather system info: {e}"}
    
    def check_forensic_readiness(self) -> Dict:
        """Check if system is ready for forensic operations"""
        checks = {
            'root_privileges': self._check_root_privileges(),
            'disk_space': self._check_disk_space(),
            'memory_available': self._check_memory(),
            'essential_tools': self._check_essential_tools(),
            'python_dependencies': self._check_python_deps()
        }
        
        return checks
    
    def _check_root_privileges(self) -> Dict:
        """Check if running with appropriate privileges"""
        try:
            is_root = os.geteuid() == 0
            return {
                'status': 'PASS' if is_root else 'WARNING',
                'message': 'Root privileges available' if is_root else 'Running as non-root user'
            }
        except:
            return {'status': 'UNKNOWN', 'message': 'Could not determine privileges'}
    
    def _check_disk_space(self) -> Dict:
        """Check available disk space"""
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024 ** 3)
            
            if free_gb > 10:
                return {'status': 'PASS', 'message': f'{free_gb:.1f} GB free space available'}
            elif free_gb > 1:
                return {'status': 'WARNING', 'message': f'Low disk space: {free_gb:.1f} GB free'}
            else:
                return {'status': 'FAIL', 'message': f'Critical disk space: {free_gb:.1f} GB free'}
                
        except Exception as e:
            return {'status': 'ERROR', 'message': f'Could not check disk space: {e}'}
    
    def _check_memory(self) -> Dict:
        """Check available memory"""
        try:
            memory = psutil.virtual_memory()
            free_gb = memory.available / (1024 ** 3)
            
            if free_gb > 2:
                return {'status': 'PASS', 'message': f'{free_gb:.1f} GB RAM available'}
            elif free_gb > 0.5:
                return {'status': 'WARNING', 'message': f'Low memory: {free_gb:.1f} GB available'}
            else:
                return {'status': 'FAIL', 'message': f'Critical memory: {free_gb:.1f} GB available'}
                
        except Exception as e:
            return {'status': 'ERROR', 'message': f'Could not check memory: {e}'}
    
    def _check_essential_tools(self) -> Dict:
        """Check essential command line tools"""
        essential_tools = ['file', 'dd', 'lsblk']
        available = []
        missing = []
        
        for tool in essential_tools:
            try:
                subprocess.run([tool, '--version'], capture_output=True, check=True)
                available.append(tool)
            except:
                missing.append(tool)
        
        if not missing:
            return {'status': 'PASS', 'message': 'All essential tools available'}
        else:
            return {
                'status': 'WARNING', 
                'message': f'Missing tools: {", ".join(missing)}'
            }
    
    def _check_python_deps(self) -> Dict:
        """Check Python dependencies"""
        deps_to_check = ['psutil', 'rich', 'questionary', 'magic']
        available = []
        missing = []
        
        for dep in deps_to_check:
            try:
                __import__(dep)
                available.append(dep)
            except ImportError:
                missing.append(dep)
        
        if not missing:
            return {'status': 'PASS', 'message': 'All Python dependencies available'}
        else:
            return {
                'status': 'FAIL',
                'message': f'Missing dependencies: {", ".join(missing)}'
            }
