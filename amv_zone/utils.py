"""Utility functions for AMV Zone operations"""

from ..tools.utils import get_list_item


def get_selected_amv_zone(context):
    """Get the currently selected AMV Zone item from the scene"""
    return get_list_item(context.scene.amv_zones, context.scene.amv_zone_index)
