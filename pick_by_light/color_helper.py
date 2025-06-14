from rpi_ws281x import Color

def get_color_by_name(color_name):
    """
    Returns a Color object based on the given color name.

    Args:
        color_name (str): Name of the color to retrieve

    Returns:
        Color: Color object matching the given name, or a default gray color
    """
    if color_name == "red":
        color = Color(255, 0, 0)
    elif color_name == "green":
        color = Color(0, 255, 0)
    elif color_name == "blue":
        color = Color(0, 0, 255)
    elif color_name == "yellow":
        color = Color(255, 255, 0)
    elif color_name == "purple":
        color = Color(255, 0, 255)
    elif color_name == "cyan":
        color = Color(0, 255, 255)
    elif color_name == "white":
        color = Color(255, 255, 255)
    else:
        color = Color(100, 100, 100)

    return color
    """
    return None
    """
