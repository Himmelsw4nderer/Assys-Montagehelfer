import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from typing import List, Tuple, Any, Optional
import numpy as np

STUD_RADIUS: float = 0.3
STUD_SPACING: float = 1.0
STUD_HEIGHT: float = 0.177

BRICK_HEIGHT: float = 1.211

def draw_studs(ax: Any, x: float, y: float, width: float, height: float, color: str, alpha: float = 1.0) -> None:
    for i_j in [(i, j) for i in range(int(width/STUD_SPACING)) for j in range(int(height/STUD_SPACING))]:
        stud_x = x + (i_j[0] + 0.5) * STUD_SPACING
        stud_y = y + (i_j[1] + 0.5) * STUD_SPACING
        ax.add_patch(patches.Circle((stud_x, stud_y), STUD_RADIUS, edgecolor='black',
                                 facecolor=color, alpha=alpha))

def draw_rectangle(ax: Any, x: float, y: float, width: float, height: float, color: str, alpha: float = 1.0, line_width=1.0) -> None:
    ax.add_patch(patches.Rectangle((x, y), width, height, edgecolor='black', facecolor=color, alpha=alpha, linewidth=line_width))

def render_step(ax: Any, step_number: int, bricks: List[Tuple]) -> None:
    draw_studs(ax, 0, 0, 10, 10, 'gray', alpha=0.1)
    for brick in bricks[:-1]:
        draw_rectangle(ax, *brick, alpha=0.2)
    draw_rectangle(ax, *bricks[-1])
    draw_studs(ax, *bricks[-1])

def draw_border(ax: Any) -> None:
    ax.add_patch(patches.Rectangle((0, 0), 10, 10, edgecolor='black', facecolor='none'))

def setup_axes() -> Tuple[Any, Any]:
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.clear()
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10.5)
    ax.set_aspect('equal')
    draw_border(ax)
    ax.axis('off')
    return fig, ax

def convert_to_base64(fig: Any) -> str:
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return image

def render_blueprint(steps: List[Tuple]) -> str:
    fig, ax = setup_axes()
    render_step(ax, 1, steps)
    return convert_to_base64(fig)

def create_new_layer(old_layer: Optional[np.ndarray] = None) -> np.ndarray:
    layer = np.full((10, 10), "stud", dtype=object)
    if old_layer is not None:
        layer[(old_layer == "stud") | (old_layer == None)] = None
    return layer

def can_place_brick(layer: np.ndarray, x: int, y: int, width: int, height: int) -> bool:
    sub_layer = layer[y:y+height, x:x+width]
    return bool(np.all((sub_layer == None) | (sub_layer == "stud")))

def place_brick_on_layer(layer: np.ndarray, x: int, y: int, width: int, height: int, color: str) -> np.ndarray:
    layer[y:y+height, x:x+width] = color
    return layer

def blueprint_to_cube(steps: List[Tuple]) -> np.ndarray:
    layers = []
    layer = create_new_layer()
    for step in steps:
        x, y, width, height, color = step
        if not can_place_brick(layer, x, y, width, height):
            layers.append(np.copy(layer))
            layer = create_new_layer(old_layer=layer)
        place_brick_on_layer(layer, x, y, width, height, color)
    layers.append(layer)
    layers.append(create_new_layer(old_layer=layer))
    return np.array(layers)

def draw_stud_on_layer(ax: Any, x: float, y: float, color: str, alpha: float) -> None:
    x_offset = x + ((STUD_SPACING - (STUD_RADIUS*2)) / 2)
    draw_rectangle(ax, x_offset, y, STUD_RADIUS*2, STUD_HEIGHT, color, alpha=alpha)

def process_cell(ax: Any, cell: Any, i: int, j: int, k: int, cube_representation: np.ndarray) -> None:
    if cell is not None and not cell == "stud":
        draw_rectangle(ax, k, j*BRICK_HEIGHT, STUD_SPACING, BRICK_HEIGHT, cell)
    elif cell == "stud":
        color = "gray" if i <= 0 else cube_representation[i][j-1][k]
        if color is None or color == "stud":
            return
        alpha = 0.1 if i <= 0 else 1.0
        draw_stud_on_layer(ax, k, j*BRICK_HEIGHT, color, alpha)

def render_cube_view(cube_representation: np.ndarray) -> str:
    fig, ax = setup_axes()
    for i, layer in enumerate(cube_representation):
        for j in range(layer.shape[0]):
            for k in range(layer.shape[1]):
                process_cell(ax, layer[j,k], i, j, k, cube_representation)
    return convert_to_base64(fig)

def render_control_views(steps: List[Tuple]) -> Tuple[str, str, str, str]:
    cube_representation = blueprint_to_cube(steps)
    cube_representation_flipped_back = np.transpose(cube_representation, axes=(1, 0, 2))
    back_view = render_cube_view(cube_representation_flipped_back)
    cube_representation_flipped_front = np.flip(np.flip(cube_representation_flipped_back, axis=0), axis=2)
    front_view = render_cube_view(cube_representation_flipped_front)
    cube_representation_flipped_right = np.transpose(cube_representation, axes=(2, 0, 1))
    right_view = render_cube_view(cube_representation_flipped_right)
    cube_representation_flipped_left = np.flip(np.flip(cube_representation_flipped_right, axis=0), axis=2)
    left_view = render_cube_view(cube_representation_flipped_left)

    return front_view, back_view, right_view, left_view
