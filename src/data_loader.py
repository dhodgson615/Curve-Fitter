"""
Data loading and parsing utilities for curve fitting.
"""

from re import findall
from pandas import read_csv


class DataLoader:
    """
    A class for loading and parsing data from various sources.
    
    Supports loading points from CSV files and parsing coordinate strings.
    """
    
    COORD_REGEX = r"\(\s*([^,]+)\s*,\s*([^)]+)\s*\)"
    
    def __init__(self):
        """Initialize the DataLoader."""
        pass
    
    def parse_coordinates(self, coord_string):
        """
        Parse coordinate string into list of (x, y) tuples.
        
        Args:
            coord_string (str): String containing coordinates like "(1, 2), (3, 4)"
            
        Returns:
            List of (x, y) tuples
            
        Example:
            >>> loader = DataLoader()
            >>> loader.parse_coordinates("(1, 2), (3, 4)")
            [(1.0, 2.0), (3.0, 4.0)]
        """
        matches = findall(self.COORD_REGEX, coord_string)
        return [(float(x), float(y)) for x, y in matches]
    
    def load_from_csv(self, filename, x_column=None, y_column=None):
        """
        Load points from a CSV file.
        
        Args:
            filename (str): Path to the CSV file
            x_column (str, optional): Name of the x-coordinate column. 
                                    If None, uses the first column.
            y_column (str, optional): Name of the y-coordinate column.
                                    If None, uses the second column.
                                    
        Returns:
            Tuple of (points, x_column_name, y_column_name) where points
            is a list of (x, y) tuples
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV file doesn't have enough columns
        """
        df = read_csv(filename)
        
        if len(df.columns) < 2:
            raise ValueError(f"CSV file must have at least 2 columns, found {len(df.columns)}")
        
        x_col = x_column or df.columns[0]
        y_col = y_column or df.columns[1]
        
        if x_col not in df.columns:
            raise ValueError(f"Column '{x_col}' not found in CSV file")
        if y_col not in df.columns:
            raise ValueError(f"Column '{y_col}' not found in CSV file")
        
        points = list(zip(df[x_col], df[y_col]))
        return points, x_col, y_col
    
    def validate_points(self, points):
        """
        Validate that points is a proper list of coordinate tuples.
        
        Args:
            points: List of points to validate
            
        Returns:
            bool: True if points are valid
            
        Raises:
            ValueError: If points are not in the correct format
        """
        if not isinstance(points, list):
            raise ValueError("Points must be a list")
        
        if len(points) < 2:
            raise ValueError("At least 2 points are required for interpolation")
        
        for i, point in enumerate(points):
            if not isinstance(point, (tuple, list)) or len(point) != 2:
                raise ValueError(f"Point {i} must be a tuple or list of length 2")
            
            try:
                float(point[0])
                float(point[1])
            except (ValueError, TypeError):
                raise ValueError(f"Point {i} contains non-numeric values: {point}")
        
        return True