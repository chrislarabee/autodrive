from ._conn import Connection
from ._view import GSheetView


View = GSheetView
"""Supertype for Ranges, Tabs, and GSheets."""

Connection = Connection
"""Supertype for SheetsConnections and DriveConnections."""
