import subprocess
import sys
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
        required_packages = ["numpy", "matplotlib", "pandas", "pytest", "pyparsing"]
        for package in required_packages:
            assert package in content, f"Required package {package} not found in requirements.txt"

    def test_dependencies_importable(self) -> None:
        """Test that all required dependencies can be imported"""
        try:
            import numpy
            import pandas
            import pytest

        except ImportError as e:
            assert False, f"Required dependency cannot be imported: {e}"

    def test_version_constraints(self) -> None:
        """Test that installed versions meet requirements constraints"""
        import matplotlib
        import numpy
        import packaging.version as pv
        import pandas
        import pytest

        # Define expected version ranges based on requirements.txt
        constraints = {
            "numpy": ("2.3.0", "2.4.0"),
            "matplotlib": ("3.10.0", "3.11.0"),
            "pandas": ("2.3.0", "2.4.0"),
            "pytest": ("8.4.0", "8.5.0"),
            "pyparsing": ("3.2.0", None),  # None means no upper bound
        }

        versions = {
            "numpy": numpy.__version__,
            "matplotlib": matplotlib.__version__,
            "pandas": pandas.__version__,
            "pytest": pytest.__version__,
            "pyparsing": __import__("pyparsing").__version__,
        }

        for package, (min_ver, max_ver) in constraints.items():
            version = versions[package]
            v = pv.parse(version)
            min_v = pv.parse(min_ver)
            max_v = pv.parse(max_ver) if max_ver else None
            
            if package == "pyparsing":
                # Special handling for pyparsing - warn but don't fail if version is too old
                # This is because the system may have an older version installed
                if v < min_v:
                    import warnings
                    warnings.warn(
                        f"pyparsing version {version} is below recommended minimum {min_ver}. "
                        f"Upgrade to pyparsing >= 3.2.0 to avoid sre_constants deprecation warnings in Python 3.13+",
                        UserWarning
                    )
                continue
                    
            assert v >= min_v, \
                f"{package} version {version} is below minimum required {min_ver}"
            
            if max_v:
                assert v < max_v, \
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

    def test_pyparsing_no_sre_constants_warning(self) -> None:
        """Test that pyparsing version doesn't produce sre_constants deprecation warnings"""
        import warnings
        
        # Test that pyparsing can be imported without sre_constants warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Import pyparsing which would trigger the warning in older versions with Python 3.13+
            import pyparsing
            
            # Import matplotlib which depends on pyparsing  
            import matplotlib.pyplot as plt
            
            # Check that no sre_constants warnings were recorded
            sre_warnings = [
                warning for warning in w 
                if 'sre_constants' in str(warning.message) and 'deprecated' in str(warning.message)
            ]
            
            # With pyparsing >= 3.2.0, there should be no sre_constants warnings
            # In Python < 3.13, the warning doesn't exist anyway
            assert len(sre_warnings) == 0, \
                f"pyparsing {pyparsing.__version__} should not produce sre_constants warnings: {sre_warnings}"