"""
Pre-load numpy and scikit-learn to avoid macOS Gatekeeper verification pop-ups.
This prevents the "Verifying _isfinite.cpython-313-darwin.so..." dialog from appearing repeatedly.
"""
import warnings

# Suppress warnings during import
with warnings.catch_warnings():
    warnings.filterwarnings('ignore')
    # Pre-load numpy (used by scikit-learn and our inference module)
    import numpy as np
    # Pre-load scikit-learn (used by our ML model)
    import sklearn

# This ensures the modules are loaded once at startup
# instead of being verified repeatedly during runtime
__all__ = []

