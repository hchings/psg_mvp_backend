"""
This file contains a standalone signal to trigger cache warmup.
"""

import django.dispatch


# signal to trigger a cache warm up
warmup_cache = django.dispatch.Signal()
