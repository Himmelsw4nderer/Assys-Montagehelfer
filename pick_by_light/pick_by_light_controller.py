from rpi_ws281x import PixelStrip
from typing import Dict, Optional, Any, Tuple
from pick_by_light.color_helper import get_color_by_name

class PickByLightController:
    def __init__(self, led_pin: int = 12, num_pixels: int = 26) -> None:
        """Initialize the light controller with the GPIO pin for the LED strip."""
        self.led_pin = led_pin
        self.num_pixels = num_pixels
        self.blocks: Dict[int, Tuple[str, float, float, int]] = {} # location (key), color, length, width, count
        self.currently_highlighted: Optional[Any] = None

        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10          # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 128  # Set to 0 for darkest and 255 for brightest
        LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.pixels = PixelStrip(self.num_pixels, self.led_pin, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                              LED_BRIGHTNESS, LED_CHANNEL)
        self.pixels.begin()

        self.cleanup()

    def add_block_to_location(self, location: Any, length: float, width: float, color: str, count: int = 1) -> None:
        """Add a block to a specific location with its properties."""
        if location in self.blocks:
            raise ValueError(f"Block already exists at location {location}.")
        if location > self.num_pixels or location < 0:
            raise ValueError(f"Location {location} is out of range.")

        # Make sure length is always longer than width
        if length > width:
            length, width = width, length

        self.blocks[location] = (color, length, width, count)

    def get_block_location(self, length: float, width: float, color: str) -> Optional[int]:
        """Get the location of a block with the specified properties."""
        # Make sure length is always longer than width
        if length > width:
            length, width = width, length

        for location, (block_color, block_length, block_width, count) in self.blocks.items():
            if block_length == length and block_width == width and block_color == color:
                return location
        return None

    def show_block(self, location: int) -> None:
        """Highlight the block at the specified location by turning on the LED."""
        if location not in self.blocks:
            raise ValueError(f"No block found at location {location}")

        color_name = self.blocks[location][0]  # Color is the first element in the tuple
        color = get_color_by_name(color_name)

        self.cleanup()
        self.pixels.setPixelColor(location, color)
        self.pixels.show()
        self.currently_highlighted = location

    def get_currently_highlighted_block(self) -> Optional[int]:
        """Return the location of the currently highlighted block."""
        if not self.currently_highlighted:
            raise ValueError("No block is currently highlighted")
        return self.currently_highlighted

    def remove_block(self, location: Any, count: int = 1) -> None:
        """Remove a highlighted block from the specified location."""
        if location not in self.blocks:
            raise ValueError(f"No block found at location {location}")

        color, length, width, current_count = self.blocks[location]

        if count < 0 or count >= current_count:
            del self.blocks[location]

            if self.currently_highlighted == location:
                """for i in range(self.num_pixels):
                    self.pixels.setPixelColor(i, Color(0, 0, 0))
                self.pixels.show()"""
                self.currently_highlighted = None
        else:
            new_count = current_count - count
            self.blocks[location] = (color, length, width, new_count)

    def cleanup(self) -> None:
        """Clean up resources when done."""
        """for i in range(self.num_pixels):
            self.pixels.setPixelColor(i, Color(0, 0, 0))
        self.pixels.show()"""


if __name__ == "__main__":
    light_controller = PickByLightController(led_pin=12, num_pixels=30)

    light_controller.add_block_to_location(10, length=2.0, width=4.0, color="red", count=2)
    light_controller.add_block_to_location(15, length=2.0, width=4.0, color="blue", count=1)
    light_controller.add_block_to_location(20, length=2.0, width=4.0, color="green", count=3)

    print("\nTesting block highlighting:")
    light_controller.show_block(10)
    input("Press Enter to continue to next block...")

    try:
        light_controller.show_block(15)
    except ValueError as e:
        print(e)
    input("Press Enter to continue to next block...")

    try:
        light_controller.show_block(20)
    except ValueError as e:
        print(e)
    input("Press Enter to continue...")

    try:
        current = light_controller.get_currently_highlighted_block()
        print(f"Currently highlighted block: {current}")
    except ValueError as e:
        print(e)

    print("\nTesting block removal:")
    light_controller.remove_block(5)

    light_controller.show_block(1)
    input("Press Enter to finish...")

    print(light_controller.blocks)
    light_controller.cleanup()
