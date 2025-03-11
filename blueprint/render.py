import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from typing import List, Tuple, Any

STUD_RADIUS: float = 0.3
STUD_SPACING: float = 1.0

def draw_studs(ax: Any, x: float, y: float, width: float, height: float, color: str, alpha: float = 1.0) -> None:
    for i_j in [(i, j) for i in range(int(width/STUD_SPACING)) for j in range(int(height/STUD_SPACING))]:
        stud_x = x + (i_j[0] + 0.5) * STUD_SPACING
        stud_y = y + (i_j[1] + 0.5) * STUD_SPACING
        ax.add_patch(patches.Circle((stud_x, stud_y), STUD_RADIUS, edgecolor='black',
                                 facecolor=color, alpha=alpha))

def draw_brick(ax: Any, x: float, y: float, width: float, height: float, color: str, alpha: float = 1.0) -> None:
    ax.add_patch(patches.Rectangle((x, y), width, height, edgecolor='black', facecolor=color, alpha=alpha))

def render_step(ax: Any, step_number: int, bricks: List[Tuple]) -> None:
    draw_studs(ax, 0, 0, 10, 10, 'gray', alpha=0.1)
    for brick in bricks[:-1]:
        draw_brick(ax, *brick, alpha=0.2)
    draw_brick(ax, *bricks[-1])
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
    img = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return img

def render_blueprint(steps: List[Tuple]) -> str:
    fig, ax = setup_axes()
    render_step(ax, 1, steps)
    return convert_to_base64(fig)
