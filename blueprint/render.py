import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64

def draw_brick(ax, x, y, width, height, color, alpha=1.0):
    ax.add_patch(patches.Rectangle((x, y), width, height, edgecolor='black', facecolor=color, alpha=alpha))

def render_step(ax, step_number, bricks):
    ax.text(0.5, 1.05, f'Step {step_number}', transform=ax.transAxes, ha='center', fontsize=16)
    for brick in bricks[:-1]:
        draw_brick(ax, *brick, alpha=0.5)
    draw_brick(ax, *bricks[-1])

def render_blueprint(steps):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.clear()
    render_step(ax, 1, steps)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return img
