"""
Test warning filter configuration for third-party library deprecation warnings
"""
import warnings
import pytest


class TestWarningFilters:
    """Test that warning filters are properly configured"""
    
    def test_sre_constants_warning_filter(self) -> None:
        """Test that sre_constants deprecation warning from pyparsing is filtered"""
        # This test verifies that the pytest.ini configuration properly filters
        # the 'sre_constants' deprecation warning that appears in Python 3.13+
        # when importing pyparsing (which is a dependency of matplotlib)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Import pyparsing which triggers the warning in Python 3.13+
            import pyparsing
            
            # Check that no sre_constants warnings are recorded
            # (they should be filtered by pytest.ini configuration)
            sre_warnings = [
                warning for warning in w 
                if 'sre_constants' in str(warning.message) and 'deprecated' in str(warning.message)
            ]
            
            # In Python < 3.13, the warning doesn't exist
            # In Python 3.13+, it should be filtered by pytest.ini
            # Either way, we should have 0 sre_constants warnings
            assert len(sre_warnings) == 0, f"sre_constants warnings should be filtered: {sre_warnings}"
    
    def test_matplotlib_import_clean(self) -> None:
        """Test that matplotlib can be imported without triggering filtered warnings"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Import matplotlib which depends on pyparsing
            import matplotlib.pyplot as plt
            
            # Check that no sre_constants warnings are recorded
            sre_warnings = [
                warning for warning in w 
                if 'sre_constants' in str(warning.message) and 'deprecated' in str(warning.message)
            ]
            
            assert len(sre_warnings) == 0, f"sre_constants warnings should be filtered: {sre_warnings}"