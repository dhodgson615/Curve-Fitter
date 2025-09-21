"""
Test installation and dependency verification
"""
import subprocess
import sys
import tempfile
from pathlib import Path


class TestInstallation:
    """Test that installation instructions work correctly"""

    def test_requirements_file_exists(self) -> None:
        """Test that requirements.txt exists and is readable"""
        requirements_file = Path("requirements.txt")
        assert requirements_file.exists(), "requirements.txt file not found"
        assert requirements_file.is_file(), "requirements.txt is not a file"
        
        # Check that file is not empty
        content = requirements_file.read_text()
        assert len(content.strip()) > 0, "requirements.txt is empty"

    def test_requirements_file_format(self) -> None:
        """Test that requirements.txt has proper format and comments"""
        requirements_file = Path("requirements.txt")
        content = requirements_file.read_text()
        
        # Check for install instructions
        assert "pip install -r requirements.txt" in content, \
            "Install instructions not found in requirements.txt"
        
        # Check for Python version requirement
        assert "Python 3.12" in content, \
            "Python version requirement not specified"
        
        # Check that core dependencies are present
        required_packages = ["numpy", "matplotlib", "pandas", "pytest"]
        for package in required_packages:
            assert package in content, f"Required package {package} not found in requirements.txt"

    def test_dependencies_importable(self) -> None:
        """Test that all required dependencies can be imported"""
        try:
            import numpy
            import matplotlib
            import pandas
            import pytest
        except ImportError as e:
            assert False, f"Required dependency cannot be imported: {e}"

    def test_version_constraints(self) -> None:
        """Test that installed versions meet requirements constraints"""
        import numpy
        import matplotlib
        import pandas
        import pytest
        import packaging.version as pv

        # Define expected version ranges based on requirements.txt
        constraints = {
            "numpy": ("2.3.0", "2.4.0"),
            "matplotlib": ("3.10.0", "3.11.0"),
            "pandas": ("2.3.0", "2.4.0"),
            "pytest": ("8.4.0", "8.5.0"),
        }

        versions = {
            "numpy": numpy.__version__,
            "matplotlib": matplotlib.__version__,
            "pandas": pandas.__version__,
            "pytest": pytest.__version__,
        }

        for package, (min_ver, max_ver) in constraints.items():
            version = versions[package]
            v = pv.parse(version)
            min_v = pv.parse(min_ver)
            max_v = pv.parse(max_ver)
            
            assert min_v <= v < max_v, \
                f"{package} version {version} is not within required range [{min_ver}, {max_ver})"

    def test_data_generation_functionality(self) -> None:
        """Test that data generation works as expected"""
        import subprocess
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_output.csv")
            
            # Run data generation
            result = subprocess.run([
                sys.executable, "data/data_gen.py",
                "--points", "5",
                "--output", output_file
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"Data generation failed: {result.stderr}"
            assert os.path.exists(output_file), "Output CSV file was not created"
            
            # Check file content
            with open(output_file, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 1, "CSV file should have header and data"
                assert "Time" in lines[0] and "Temperature" in lines[0], \
                    "CSV header should contain Time and Temperature columns"

    def test_pytest_functionality(self) -> None:
        """Test that pytest works correctly with the current setup"""
        result = subprocess.run([
            sys.executable, "-m", "pytest", "--version"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"pytest command failed: {result.stderr}"
        assert "pytest" in result.stdout, "pytest version info not found"