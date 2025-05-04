from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import numpy as np
from PIL import Image

width = 800
height = 800
xmin, xmax = -2.0, 1.0
ymin, ymax = -1.5, 1.5

# Global variables for c value
c_x = 0.0
c_y = 0.0
step_size = 0.01


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


def key_callback(window, key, _scancode, action, _mods):
    global c_x, c_y

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_RIGHT:
            c_x += step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
        elif key == glfw.KEY_LEFT:
            c_x -= step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
        elif key == glfw.KEY_UP:
            c_y += step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
        elif key == glfw.KEY_DOWN:
            c_y -= step_size
            print(f"Current C: ({c_x:.4f}, {c_y:.4f})")
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


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

    texture = create_textures()
    compute_program = create_programs()

    # Initial C value
    print(f"Current C: ({c_x:.4f}, {c_y:.4f})")

    # Main render loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Update uniforms with current c value
        fill_uniforms(
            compute_program,
            {
                "xbounds": [xmin, xmax],
                "ybounds": [ymin, ymax],
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
