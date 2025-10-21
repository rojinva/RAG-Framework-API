import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Wedge
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def split_segment_equally(number_of_segments):
    """
    Splits the interval [0, 1] into equal segments and returns the positions of the segment boundaries.
    Args:
        number_of_segments (int): The number of segments to split the interval into.
    Returns:
        list[float]: A list of floats representing the positions of the segment boundaries within [0, 1].
    Notes:
        - The returned list contains `number_of_segments` values, each representing the position of a segment boundary.
        - The boundaries are spaced equally, excluding the endpoints 0 and 1.
        - For example, if `number_of_segments` is 3, the returned list will be [0.25, 0.5, 0.75].
    """
    segments = []

    seg_length = 1 / (number_of_segments + 1)
    for i in range(number_of_segments):
        segments.append(seg_length * (i + 1))
    return segments


def problems_func(
    ax, data: str, problem_x: float, arrow_length: float = 5.0, slope: float = 1.732
):
    """
    Draw each problem section of the Ishikawa plot with consistent angles.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to draw the problems.
    data : str
        The name of the problem category.
    problem_x, problem_y : float
        The starting X and Y positions where problem arrow connects to spine.
    angle_x, angle_y : float
        The offsets for the problem text box position.
    arrow_length : float, optional
        The length of the problem arrow, calculated based on max causes.

    Returns
    -------
    tuple
        The endpoint coordinates of the problem arrow for cause placement.
    """
    # Calculate the endpoint of the problem arrow
    end_y = arrow_length  # Arrow extends vertically

    if len(data) > 15:
        words = data.split()
        wrapped_text = ""
        current_line = ""

        for word in words:
            if len(current_line) + len(word) > 15:
                wrapped_text += current_line.strip() + "\n"
                current_line = word + " "
            else:
                current_line += word + " "

        # Add the last line
        wrapped_text += current_line.strip()
        display_text = wrapped_text.upper()
    else:
        display_text = data.upper()
    print(f"Text box position for problem '{data}' at ({-12}, {end_y})")

    # Draw problem box at the end of the arrow
    ax.annotate(
        display_text,
        xy=(problem_x, 0),  # Arrow points to spine
        xytext=((problem_x - abs(arrow_length / slope)), end_y),  # Text box position
        fontsize=8,
        color="white",
        weight="bold",
        xycoords="data",
        verticalalignment="center",
        horizontalalignment="center",
        textcoords="data",
        arrowprops=dict(arrowstyle="->", facecolor="black"),
        bbox=dict(boxstyle="square", facecolor="tab:blue", pad=0.8),
    )


def causes_func(
    ax,
    data: list,
    start_x: float,
    end_y: float,
    top: bool = True,
    slope: float = 1.732,
    category_spacing: float = 1.5,
):
    """
    Place causes along the problem arrow at regular intervals.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to draw on
    data : list
        The list of causes to display
    start_x, start_y : float
        The start coordinates of the problem arrow (at the spine)
    end_x, end_y : float
        The end coordinates of the problem arrow
    cause_xytext : tuple, optional
        Text offset for cause labels
    top : bool, default: True
        Whether this is a top or bottom branch

    Returns
    -------
    None.
    """
    # Limit to max 20 causes
    causes_to_process = data[:20] if len(data) > 20 else data
    num_causes = len(causes_to_process)

    if num_causes == 0:
        return

    # Calculate the segment length based on problem arrow length
    total_length = abs(end_y)

    # Direction multiplier (1 for top branches, -1 for bottom branches)
    dir_mult = 1 if top else -1
    x_offset = 0
    ratio_to_use = split_segment_equally(num_causes)
    # Place each cause along the problem arrow
    for i, cause in enumerate(causes_to_process):
        # Calculate point on problem arrow
        y_pos = total_length * ratio_to_use[i] * dir_mult

        # Calculate x position of arrow using slope

        x_offset = y_pos / slope
        x_pos = start_x - abs(x_offset)

        x_pos_text = x_pos - (category_spacing / 2)
        print(f"Cause '{cause}' at ({x_pos}, {y_pos})")

        # Draw the cause annotation with arrow pointing to the problem arrow
        ax.annotate(
            cause,
            xy=(x_pos, y_pos),  # Arrow points to problem arrow
            xytext=(x_pos_text, y_pos),  # Text position
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=7,
            xycoords="data",
            textcoords="data",
            arrowprops=dict(arrowstyle="->", facecolor="black"),
        )


def draw_spine(ax, xmin: int, xmax: int):
    """
    Draw main spine, head and tail.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to draw on
    xmin : int
        The default position of the head of the spine's
        x-coordinate.
    xmax : int
        The default position of the tail of the spine's
        x-coordinate.

    Returns
    -------
    None.

    """
    # draw main spine
    ax.plot([xmin - 0.1, xmax], [0, 0], color="tab:blue", linewidth=2)
    # draw fish head
    ax.text(xmax + 0.5, -0.1, "PROBLEM", fontsize=8, weight="bold", color="white")
    semicircle = Wedge((xmax, 0), 3, 270, 90, fc="tab:blue")
    ax.add_patch(semicircle)
    # draw fish tail
    tail_pos = [[xmin - 0.8, 0.8], [xmin - 0.8, -0.8], [xmin, -0.01]]
    triangle = Polygon(tail_pos, fc="tab:blue")
    ax.add_patch(triangle)


def draw_body(ax, data: dict, spine_length: float):
    """
    Draw the fishbone diagram with consistent angles and spacing.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes object to draw on
    data : dict
        The input data dictionary with categories and their causes
    spine_length : float
        Length of spine

    Returns
    -------
    None.
    """

    slope = 2.5
    # Find the category with the maximum number of causes
    max_causes = max(len(causes) for causes in data.values()) if data else 0

    # Calculate arrow length based on max causes
    # This ensures all problem arrows have the same length
    base_arrow_length = 3.0  # Base arrow length
    arrow_length = base_arrow_length + (0.8 * max(0, max_causes))
    print(f"Arrow length set to {arrow_length} for max causes {max_causes}")

    # Set the length of the spine according to the actual number of categories
    # Use a more compact layout - just enough for the categories
    num_categories = len(data)
    if num_categories % 2 == 1:
        num_categories += 1
    draw_spine(ax, -spine_length, spine_length)

    # Calculate spacing between category branches along the spine
    # Make the spacing more compact
    category_spacing = ((spine_length * 2) - (spine_length * 0.2)) / max(
        1, num_categories / 2
    )
    # Position for the first category - start closer to the left end
    current_x = -spine_length + (category_spacing)
    # Process each category
    for index, (category, causes) in enumerate(data.items()):
        # Alternate between top and bottom of spine
        is_top = index % 2 == 0

        # Y direction based on top/bottom
        dir_mult = 1 if is_top else -1

        # Calculate problem arrow start position
        problem_x = current_x
        problem_y = 0  # On the spine

        # Draw the problem category and get arrow endpoint
        problems_func(
            ax=ax,
            data=category,
            problem_x=problem_x,
            arrow_length=arrow_length * dir_mult,
            slope=slope,
        )

        # Draw causes along the problem arrow
        causes_func(
            ax=ax,
            data=causes,
            start_x=problem_x,
            end_y=arrow_length * 0.8,
            top=is_top,
            slope=slope,
            category_spacing=category_spacing,
        )

        # Move to next position along spine - more compact spacing
        current_x += category_spacing if not is_top else 0


def resize_image(image_bytes, max_width=800):
    """
    Resize the image to the specified width while maintaining aspect ratio.

    Parameters
    ----------
    image_bytes : bytes
        The image bytes to resize
    max_width : int, optional
        Maximum width of the resized image

    Returns
    -------
    bytes
        The resized image bytes
    """
    image = Image.open(BytesIO(image_bytes))
    aspect_ratio = image.height / image.width

    if image.width > max_width:
        new_width = max_width
        new_height = int(max_width * aspect_ratio)
        resized_image = image.resize((new_width, new_height))

        buffer = BytesIO()
        resized_image.save(buffer, format="PNG")
        return buffer.getvalue()
    return image_bytes


def create_fishbone_diagram(categories, dpi=300):
    """
    Create a fishbone diagram from the given categories and causes.

    Parameters
    ----------
    categories : dict
        Dictionary with categories as keys and lists of causes as values
    dpi : int, optional
        DPI for the output image

    Returns
    -------
    bytes
        The image bytes
    """

    slope = 2.5
    num_categories = len(categories)
    if num_categories % 2 == 1:
        num_categories += 1
    max_causes = max(len(causes) for causes in categories.values()) if categories else 0
    # Adjust size based on data
    width = 8 + (num_categories * 0.8)  # Reduced width scaling
    height = 6 + (max_causes * 0.4)  # Slightly reduced height scaling
    figsize = (width, height)

    fig, ax = plt.subplots(figsize=figsize, layout="constrained")

    # Calculate appropriate axis limits based on data size
    spine_length = max(2, num_categories * 2) + (
        max(2, num_categories) * 0.4
    )  # Same as in draw_body
    print(
        f"Max causes: {max_causes}, Num categories: {num_categories}, Spine length: {spine_length}"
    )

    x_limit = 4 + spine_length  # Wider for more categories
    y_limit = 10 + (max_causes)  # Taller for more causes

    ax.set_xlim(-x_limit, x_limit)
    ax.set_ylim(-y_limit, y_limit)
    ax.axis("off")

    # Draw the fishbone diagram
    draw_body(ax=ax, data=categories, spine_length=spine_length)

    # Save to BytesIO
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=dpi)
    buf.seek(0)
    img_bytes = buf.getvalue()
    plt.close(fig)  # Close the figure to free memory

    return img_bytes


def format_image_for_chat(img_bytes, max_width=1980):
    """
    Format image bytes for chat display by resizing if needed and
    converting to base64 for markdown embedding.

    Parameters
    ----------
    img_bytes : bytes
        The image bytes
    max_width : int, optional
        Maximum width for the image

    Returns
    -------
    str
        Markdown-formatted image string for embedding in chat
    """
    # Resize image if needed
    resized_bytes = resize_image(img_bytes, max_width)

    # Convert to base64
    base64_image = base64.b64encode(resized_bytes).decode("utf-8")

    # Return markdown image format
    return f"![Fishbone Diagram](data:image/png;base64,{base64_image})"


def generate_fishbone_markdown(categories):
    """
    Generate a fishbone diagram and return it as markdown for embedding in chat.

    Parameters
    ----------
    categories : dict
        Dictionary with categories as keys and lists of causes as values

    Returns
    -------
    str
        Markdown-formatted image string for embedding in chat
    """
    num_categories = len(categories)
    max_causes = max(len(causes) for causes in categories.values()) if categories else 0

    img_bytes = create_fishbone_diagram(categories)
    return format_image_for_chat(img_bytes)
