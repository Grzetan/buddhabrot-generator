from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import numpy as np
from PIL import Image

width = 800
height = 800
xmin, xmax = -4.0, 4.0
ymin, ymax = -4.0, 4.0

# Global variables for c value
c_x = 0.0
c_y = 0.0
step_size = 0.01

# Global variables for view control
zoom_level = 1.0
center_x = 0.0
center_y = 0.0
mouse_dragging = False
last_drag_x = 0
last_drag_y = 0


def calculate_bounds():
    # Calculate view bounds based on center point and zoom level
    range_x = (xmax - xmin) / zoom_level
    range_y = (ymax - ymin) / zoom_level

    new_xmin = center_x - range_x / 2
    new_xmax = center_x + range_x / 2
    new_ymin = center_y - range_y / 2
    new_ymax = center_y + range_y / 2

    return new_xmin, new_xmax, new_ymin, new_ymax


def create_compute_shader_program(compute_src):
    return compileProgram(
        compileShader(compute_src, GL_COMPUTE_SHADER),
    )


def create_textures():
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_R32UI,
        width,
        height,
        0,
        GL_RED_INTEGER,
        GL_UNSIGNED_INT,
        None,
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture


def create_programs():
    with open("shaders/buddhabrot_compute_shader.glsl") as f:
        compute_program = create_compute_shader_program(f.read())

    return compute_program


def fill_uniforms(compute_program, input_data):
    glUseProgram(compute_program)

    xbounds_location = glGetUniformLocation(compute_program, "xbounds")
    glUniform2f(xbounds_location, input_data["xbounds"][0], input_data["xbounds"][1])

    ybounds_location = glGetUniformLocation(compute_program, "ybounds")
    glUniform2f(ybounds_location, input_data["ybounds"][0], input_data["ybounds"][1])

    max_iterations_location = glGetUniformLocation(compute_program, "maxIterations")
    glUniform1ui(max_iterations_location, input_data["maxIterations"])

    c_location = glGetUniformLocation(compute_program, "c")
    glUniform2f(c_location, input_data["c"][0], input_data["c"][1])

    return {
        "xbounds": xbounds_location,
        "ybounds": ybounds_location,
        "maxIterations": max_iterations_location,
        "c": c_location,
    }


def key_callback(window, key, _scancode, action, mods):
    global c_x, c_y, zoom_level, center_x, center_y

    if action == glfw.PRESS or action == glfw.REPEAT:
        # C value navigation (normal arrow keys)
        if key == glfw.KEY_RIGHT and mods == 0:
            c_x += step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
        elif key == glfw.KEY_LEFT and mods == 0:
            c_x -= step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
        elif key == glfw.KEY_UP and mods == 0:
            c_y += step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
        elif key == glfw.KEY_DOWN and mods == 0:
            c_y -= step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")

        # Pan view with SHIFT + arrow keys
        elif key == glfw.KEY_RIGHT and mods == glfw.MOD_SHIFT:
            pan_amount = 0.1 / zoom_level
            center_x += pan_amount
            print(f"Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x")
        elif key == glfw.KEY_LEFT and mods == glfw.MOD_SHIFT:
            pan_amount = 0.1 / zoom_level
            center_x -= pan_amount
            print(f"Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x")
        elif key == glfw.KEY_UP and mods == glfw.MOD_SHIFT:
            pan_amount = 0.1 / zoom_level
            center_y += pan_amount
            print(f"Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x")
        elif key == glfw.KEY_DOWN and mods == glfw.MOD_SHIFT:
            pan_amount = 0.1 / zoom_level
            center_y -= pan_amount
            print(f"Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x")

        # Zoom controls
        elif key == glfw.KEY_EQUAL:  # '=' key for zoom in
            zoom_level *= 1.2
            print(f"Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x")
        elif key == glfw.KEY_MINUS:  # '-' key for zoom out
            zoom_level /= 1.2
            print(f"Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x")

        # Reset view
        elif key == glfw.KEY_R:
            center_x = 0.0
            center_y = 0.0
            zoom_level = 1.0
            print(
                f"View reset: Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x"
            )

        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def mouse_button_callback(window, button, action, _mods):
    global mouse_dragging, last_drag_x, last_drag_y

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_dragging = True
            last_drag_x, last_drag_y = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            mouse_dragging = False


def cursor_position_callback(window, xpos, ypos):
    global center_x, center_y, last_drag_x, last_drag_y, mouse_dragging

    if mouse_dragging:
        dx = xpos - last_drag_x
        dy = ypos - last_drag_y

        # Convert screen movement to complex plane movement
        current_xmin, current_xmax, current_ymin, current_ymax = calculate_bounds()
        scale_x = (current_xmax - current_xmin) / width
        scale_y = (current_ymax - current_ymin) / height

        # Move in opposite direction of drag and flip y-axis
        center_x -= dx * scale_x
        center_y += dy * scale_y  # Flip y-axis

        last_drag_x = xpos
        last_drag_y = ypos


def scroll_callback(window, _xoffset, yoffset):
    global zoom_level, center_x, center_y

    # Get mouse position
    mouse_x, mouse_y = glfw.get_cursor_pos(window)

    # Current bounds
    current_xmin, current_xmax, current_ymin, current_ymax = calculate_bounds()

    # Map mouse position to complex plane coordinates
    mouse_complex_x = current_xmin + (current_xmax - current_xmin) * ((mouse_x / width))
    mouse_complex_y = current_ymin + (current_ymax - current_ymin) * (
        (height - mouse_y) / height
    )

    # Store position before zoom
    zoom_factor = 1.2
    old_zoom = zoom_level

    # Apply zoom
    if yoffset > 0:
        zoom_level *= zoom_factor
    else:
        zoom_level /= zoom_factor

    # Ensure reasonable zoom bounds
    zoom_level = max(0.1, zoom_level)

    # Adjust center to zoom towards mouse position
    if zoom_level != old_zoom:
        center_x = mouse_complex_x - (mouse_complex_x - center_x) * (
            old_zoom / zoom_level
        )
        center_y = mouse_complex_y - (mouse_complex_y - center_y) * (
            old_zoom / zoom_level
        )

        print(f"Pan: ({center_x:.4f}, {center_y:.4f}), Zoom: {zoom_level:.2f}x")


def render(compute_program, texture):
    # Clear texture before rendering
    glBindTexture(GL_TEXTURE_2D, texture)
    clear_data = np.zeros((height, width), dtype=np.uint32)
    glTexSubImage2D(
        GL_TEXTURE_2D,
        0,
        0,
        0,
        width,
        height,
        GL_RED_INTEGER,
        GL_UNSIGNED_INT,
        clear_data,
    )

    # Use compute shader
    glUseProgram(compute_program)
    glBindImageTexture(1, texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_R32UI)
    glDispatchCompute(50, 50, 1)
    glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)


def display_texture(texture):
    # Read texture data back to CPU
    glBindTexture(GL_TEXTURE_2D, texture)
    texture_data = np.zeros((height, width), dtype=np.uint32)
    glGetTexImage(GL_TEXTURE_2D, 0, GL_RED_INTEGER, GL_UNSIGNED_INT, texture_data)

    if np.max(texture_data) > 0:
        normalized_data = ((texture_data / np.max(texture_data)) * 255).astype(np.uint8)
    else:
        normalized_data = np.zeros((height, width), dtype=np.uint8)

    rgb_data = np.stack([normalized_data] * 3, axis=2)
    img = Image.fromarray(rgb_data, "RGB")
    img.show()


def main():
    global c_x, c_y

    # Initialize GLFW
    if not glfw.init():
        return

    # Create a visible window
    window = glfw.create_window(width, height, "Buddhabrot Explorer", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    texture = create_textures()
    compute_program = create_programs()

    # Initial C value
    print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
    print(f"Controls: Arrow keys - change C | Shift+Arrow keys - pan")
    print(
        f"          Mouse drag - pan | Scroll wheel - zoom | +/- - zoom | R - reset view"
    )

    # Main render loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Calculate current bounds based on zoom and center
        current_xmin, current_xmax, current_ymin, current_ymax = calculate_bounds()

        # Update uniforms with current c value and bounds
        fill_uniforms(
            compute_program,
            {
                "xbounds": [current_xmin, current_xmax],
                "ybounds": [current_ymin, current_ymax],
                "maxIterations": 1000,
                "c": [c_x, c_y],
            },
        )

        # Render the Buddhabrot
        render(compute_program, texture)

        # Display the texture on screen
        glBindTexture(GL_TEXTURE_2D, texture)
        texture_data = np.zeros((height, width), dtype=np.uint32)
        glGetTexImage(GL_TEXTURE_2D, 0, GL_RED_INTEGER, GL_UNSIGNED_INT, texture_data)

        if np.max(texture_data) > 0:
            max_val = np.max(texture_data)
            normalized_data = (texture_data / max_val * 255).astype(np.uint8)
        else:
            normalized_data = np.zeros((height, width), dtype=np.uint8)

        rgb_data = np.stack([normalized_data] * 3, axis=2)

        # Convert to OpenGL texture for displaying
        img_data = rgb_data.tobytes()
        glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glfw.swap_buffers(window)

    # Cleanup
    glDeleteProgram(compute_program)
    glDeleteTextures(texture)
    glfw.terminate()


if __name__ == "__main__":
    main()
