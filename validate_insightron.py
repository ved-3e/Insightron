#!/usr/bin/env python3
"""
Comprehensive Validation Script for Insightron
Validates all optimizations and ensures smooth operation.
"""

import sys
import os
import time
import tempfile
import subprocess
from pathlib import Path
import logging
from typing import List, Dict, Tuple, Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InsightronValidator:
    """Comprehensive validator for Insightron installation and functionality."""
    
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {},
            'overall_status': 'unknown',
            'recommendations': []
        }
        self.errors = []
        self.warnings = []
    
    def validate_python_version(self) -> bool:
        """Validate Python version compatibility."""
        logger.info("Validating Python version...")
        
        version = sys.version_info
        min_version = (3, 8)
        
        if version[:2] < min_version:
            self.errors.append(f"Python {min_version[0]}.{min_version[1]}+ required, got {version.major}.{version.minor}")
            return False
        
        self.results['tests']['python_version'] = {
            'status': 'pass',
            'version': f"{version.major}.{version.minor}.{version.micro}",
            'required': f"{min_version[0]}.{min_version[1]}+"
        }
        return True
    
    def validate_dependencies(self) -> bool:
        """Validate all required dependencies are installed."""
        logger.info("Validating dependencies...")
        
        required_modules = [
            'whisper',
            'librosa',
            'soundfile',
            'tqdm',
            'pydub',
            'numpy',
            'scipy',
            'tkinter'
        ]
        
        missing_modules = []
        installed_modules = []
        
        for module in required_modules:
            try:
                if module == 'whisper':
                    import whisper
                elif module == 'librosa':
                    import librosa
                elif module == 'soundfile':
                    import soundfile
                elif module == 'tqdm':
                    import tqdm
                elif module == 'pydub':
                    import pydub
                elif module == 'numpy':
                    import numpy
                elif module == 'scipy':
                    import scipy
                elif module == 'tkinter':
                    import tkinter
                
                installed_modules.append(module)
                logger.debug(f"✓ {module} is available")
                
            except ImportError as e:
                missing_modules.append(module)
                logger.warning(f"✗ {module} is missing: {e}")
        
        if missing_modules:
            self.errors.append(f"Missing modules: {', '.join(missing_modules)}")
            self.results['tests']['dependencies'] = {
                'status': 'fail',
                'installed': installed_modules,
                'missing': missing_modules
            }
            return False
        
        self.results['tests']['dependencies'] = {
            'status': 'pass',
            'installed': installed_modules,
            'missing': []
        }
        return True
    
    def validate_project_structure(self) -> bool:
        """Validate project file structure."""
        logger.info("Validating project structure...")
        
        required_files = [
            'main.py',
            'gui.py',
            'cli.py',
            'transcribe.py',
            'text_formatter.py',
            'utils.py',
            'config.py',
            'setup.py',
            'requirements.txt',
            'requirements-minimal.txt',
            'troubleshoot.py'
        ]
        
        missing_files = []
        present_files = []
        
        for file_path in required_files:
            if Path(file_path).exists():
                present_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        if missing_files:
            self.errors.append(f"Missing files: {', '.join(missing_files)}")
            self.results['tests']['project_structure'] = {
                'status': 'fail',
                'present': present_files,
                'missing': missing_files
            }
            return False
        
        self.results['tests']['project_structure'] = {
            'status': 'pass',
            'present': present_files,
            'missing': []
        }
        return True
    
    def validate_imports(self) -> bool:
        """Validate all module imports work correctly."""
        logger.info("Validating module imports...")
        
        import_tests = [
            ('transcribe', 'AudioTranscriber'),
            ('text_formatter', 'TextFormatter', 'format_transcript'),
            ('utils', 'create_markdown', 'format_time'),
            ('config', 'WHISPER_MODEL', 'TRANSCRIPTION_FOLDER')
        ]
        
        failed_imports = []
        successful_imports = []
        
        for module_name, *attributes in import_tests:
            try:
                module = __import__(module_name)
                for attr in attributes:
                    if not hasattr(module, attr):
                        failed_imports.append(f"{module_name}.{attr}")
                    else:
                        successful_imports.append(f"{module_name}.{attr}")
            except ImportError as e:
                failed_imports.append(f"{module_name}: {e}")
        
        if failed_imports:
            self.errors.append(f"Import failures: {', '.join(failed_imports)}")
            self.results['tests']['imports'] = {
                'status': 'fail',
                'successful': successful_imports,
                'failed': failed_imports
            }
            return False
        
        self.results['tests']['imports'] = {
            'status': 'pass',
            'successful': successful_imports,
            'failed': []
        }
        return True
    
    def validate_text_formatter(self) -> bool:
        """Validate text formatter functionality."""
        logger.info("Validating text formatter...")
        
        try:
            from text_formatter import TextFormatter, format_transcript
            
            formatter = TextFormatter()
            
            # Test basic functionality
            test_text = "hello world this is a test"
            cleaned = formatter.clean_text(test_text)
            formatted = formatter.format_text(test_text)
            
            # Test convenience function
            auto_formatted = format_transcript(test_text, "auto")
            paragraph_formatted = format_transcript(test_text, "paragraphs")
            minimal_formatted = format_transcript(test_text, "minimal")
            
            # Validate results
            if not all([cleaned, formatted, auto_formatted, paragraph_formatted, minimal_formatted]):
                self.errors.append("Text formatter returned empty results")
                return False
            
            self.results['tests']['text_formatter'] = {
                'status': 'pass',
                'functions_tested': ['clean_text', 'format_text', 'format_transcript']
            }
            return True
            
        except Exception as e:
            self.errors.append(f"Text formatter validation failed: {e}")
            self.results['tests']['text_formatter'] = {
                'status': 'fail',
                'error': str(e)
            }
            return False
    
    def validate_utils(self) -> bool:
        """Validate utility functions."""
        logger.info("Validating utility functions...")
        
        try:
            from utils import create_markdown, format_time
            
            # Test format_time
            time_tests = [
                (0, "00:00"),
                (60, "01:00"),
                (125, "02:05"),
                (3661, "61:01")
            ]
            
            for seconds, expected in time_tests:
                result = format_time(seconds)
                if result != expected:
                    self.errors.append(f"format_time({seconds}) returned '{result}', expected '{expected}'")
                    return False
            
            # Test create_markdown
            markdown = create_markdown(
                filename="test",
                text="Hello world",
                date="2024-01-01 12:00:00",
                duration="1:23",
                model="medium",
                duration_seconds=83.0,
                file_size_mb=1.5,
                language="en"
            )
            
            if not markdown or "test" not in markdown:
                self.errors.append("create_markdown returned invalid result")
                return False
            
            self.results['tests']['utils'] = {
                'status': 'pass',
                'functions_tested': ['format_time', 'create_markdown']
            }
            return True
            
        except Exception as e:
            self.errors.append(f"Utils validation failed: {e}")
            self.results['tests']['utils'] = {
                'status': 'fail',
                'error': str(e)
            }
            return False
    
    def validate_config(self) -> bool:
        """Validate configuration settings."""
        logger.info("Validating configuration...")
        
        try:
            from config import WHISPER_MODEL, TRANSCRIPTION_FOLDER, OBSIDIAN_VAULT_PATH
            
            # Validate model setting
            valid_models = ['tiny', 'base', 'small', 'medium', 'large']
            if WHISPER_MODEL not in valid_models:
                self.warnings.append(f"Invalid WHISPER_MODEL: {WHISPER_MODEL}")
            
            # Validate paths
            if not isinstance(TRANSCRIPTION_FOLDER, Path):
                self.errors.append("TRANSCRIPTION_FOLDER is not a Path object")
                return False
            
            if not isinstance(OBSIDIAN_VAULT_PATH, Path):
                self.errors.append("OBSIDIAN_VAULT_PATH is not a Path object")
                return False
            
            # Check if transcription folder can be created
            try:
                TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.warnings.append(f"Cannot create transcription folder: {e}")
            
            self.results['tests']['config'] = {
                'status': 'pass',
                'whisper_model': WHISPER_MODEL,
                'transcription_folder': str(TRANSCRIPTION_FOLDER),
                'obsidian_vault_path': str(OBSIDIAN_VAULT_PATH)
            }
            return True
            
        except Exception as e:
            self.errors.append(f"Config validation failed: {e}")
            self.results['tests']['config'] = {
                'status': 'fail',
                'error': str(e)
            }
            return False
    
    def validate_cli_interface(self) -> bool:
        """Validate CLI interface functionality."""
        logger.info("Validating CLI interface...")
        
        try:
            # Test CLI help
            result = subprocess.run(
                [sys.executable, 'cli.py', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.errors.append(f"CLI help failed: {result.stderr}")
                return False
            
            if 'Insightron' not in result.stdout:
                self.warnings.append("CLI help output doesn't contain expected content")
            
            self.results['tests']['cli_interface'] = {
                'status': 'pass',
                'help_output_length': len(result.stdout)
            }
            return True
            
        except subprocess.TimeoutExpired:
            self.errors.append("CLI help command timed out")
            return False
        except Exception as e:
            self.errors.append(f"CLI validation failed: {e}")
            return False
    
    def validate_gui_import(self) -> bool:
        """Validate GUI can be imported (without actually running it)."""
        logger.info("Validating GUI import...")
        
        try:
            import tkinter as tk
            from gui import InsightronGUI
            
            # Test GUI class can be instantiated (but don't run mainloop)
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            try:
                app = InsightronGUI(root)
                root.destroy()
                
                self.results['tests']['gui_import'] = {
                    'status': 'pass',
                    'class_instantiated': True
                }
                return True
            except Exception as e:
                self.errors.append(f"GUI instantiation failed: {e}")
                return False
                
        except Exception as e:
            self.errors.append(f"GUI import failed: {e}")
            return False
    
    def validate_setup_script(self) -> bool:
        """Validate setup script functionality."""
        logger.info("Validating setup script...")
        
        try:
            # Test setup script can be imported and basic functions exist
            import setup
            
            required_functions = ['check_python_version', 'install_dependencies', 'create_directories']
            missing_functions = []
            
            for func_name in required_functions:
                if not hasattr(setup, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.errors.append(f"Setup script missing functions: {', '.join(missing_functions)}")
                return False
            
            # Test Python version check
            if not setup.check_python_version():
                self.errors.append("Python version check failed")
                return False
            
            self.results['tests']['setup_script'] = {
                'status': 'pass',
                'functions_available': required_functions
            }
            return True
            
        except Exception as e:
            self.errors.append(f"Setup script validation failed: {e}")
            return False
    
    def run_performance_test(self) -> bool:
        """Run basic performance tests."""
        logger.info("Running performance tests...")
        
        try:
            from text_formatter import TextFormatter
            from utils import create_markdown
            
            # Test text formatter performance
            formatter = TextFormatter()
            large_text = "This is a test sentence. " * 1000
            
            start_time = time.time()
            formatted = formatter.format_text(large_text)
            formatter_time = time.time() - start_time
            
            # Test markdown creation performance
            start_time = time.time()
            markdown = create_markdown(
                filename="perf_test",
                text=large_text,
                date="2024-01-01 12:00:00",
                duration="10:00",
                model="medium",
                duration_seconds=600.0,
                file_size_mb=5.0,
                language="en"
            )
            markdown_time = time.time() - start_time
            
            # Performance thresholds
            if formatter_time > 5.0:
                self.warnings.append(f"Text formatter is slow: {formatter_time:.2f}s")
            
            if markdown_time > 2.0:
                self.warnings.append(f"Markdown creation is slow: {markdown_time:.2f}s")
            
            self.results['tests']['performance'] = {
                'status': 'pass',
                'formatter_time': formatter_time,
                'markdown_time': markdown_time,
                'total_time': formatter_time + markdown_time
            }
            return True
            
        except Exception as e:
            self.errors.append(f"Performance test failed: {e}")
            return False
    
    def run_all_validations(self) -> bool:
        """Run all validation tests."""
        logger.info("Starting comprehensive validation...")
        
        validation_tests = [
            ("Python Version", self.validate_python_version),
            ("Dependencies", self.validate_dependencies),
            ("Project Structure", self.validate_project_structure),
            ("Module Imports", self.validate_imports),
            ("Text Formatter", self.validate_text_formatter),
            ("Utility Functions", self.validate_utils),
            ("Configuration", self.validate_config),
            ("CLI Interface", self.validate_cli_interface),
            ("GUI Import", self.validate_gui_import),
            ("Setup Script", self.validate_setup_script),
            ("Performance", self.run_performance_test)
        ]
        
        passed_tests = 0
        total_tests = len(validation_tests)
        
        for test_name, test_func in validation_tests:
            logger.info(f"Running {test_name} validation...")
            try:
                if test_func():
                    passed_tests += 1
                    logger.info(f"✓ {test_name} validation passed")
                else:
                    logger.error(f"✗ {test_name} validation failed")
            except Exception as e:
                logger.error(f"✗ {test_name} validation crashed: {e}")
                self.errors.append(f"{test_name} validation crashed: {e}")
        
        # Determine overall status
        if self.errors:
            self.results['overall_status'] = 'fail'
        elif self.warnings:
            self.results['overall_status'] = 'warn'
        else:
            self.results['overall_status'] = 'pass'
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'errors': self.errors,
            'warnings': self.warnings
        }
        
        return len(self.errors) == 0
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("INSIGHTRON VALIDATION SUMMARY")
        print("=" * 60)
        
        summary = self.results['summary']
        print(f"Tests: {summary['passed_tests']}/{summary['total_tests']} passed ({summary['success_rate']:.1f}%)")
        print(f"Status: {self.results['overall_status'].upper()}")
        
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\nAll validations passed! Insightron is ready to use.")
        elif not self.errors:
            print("\nValidation completed with warnings. Check recommendations above.")
        else:
            print("\nValidation failed. Please fix the errors above.")
    
    def save_results(self, filename: str = "validation_results.json"):
        """Save validation results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Validation results saved to: {filename}")

def main():
    """Main validation function."""
    print("Insightron Comprehensive Validation")
    print("=" * 60)
    
    validator = InsightronValidator()
    
    try:
        success = validator.run_all_validations()
        validator.print_summary()
        validator.save_results()
        
        if success:
            print("\nValidation completed successfully!")
            return 0
        else:
            print("\nValidation failed. Please check the errors above.")
            return 1
            
    except Exception as e:
        print(f"\nValidation crashed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
