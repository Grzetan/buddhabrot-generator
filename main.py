from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import numpy as np
from PIL import Image

local_size_x = 16
local_size_y = 16
width = 800
height = 800
num_groups_x = (width + local_size_x - 1) // local_size_x
num_groups_y = (height + local_size_y - 1) // local_size_y


def create_compute_shader_program(compute_src):
    return compileProgram(
        compileShader(compute_src, GL_COMPUTE_SHADER),
    )


def create_shader_program(vertex_src, fragment_src):
    return compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER),
    )


def bind_ssbo(ssbo_data):
    ssbo = glGenBuffers(1)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
    glBufferData(GL_SHADER_STORAGE_BUFFER, ssbo_data.nbytes, ssbo_data, GL_DYNAMIC_COPY)
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssbo)
    return ssbo


def create_textures():
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, None
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture


def create_programs():
    with open("shaders/buddhabrot_compute_shader.glsl") as f:
        compute_program = create_compute_shader_program(f.read())

    with open("shaders/vertex_shader.glsl") as vertex:
        with open("shaders/fragment_shader.glsl") as fragment:
            render_program = create_shader_program(vertex.read(), fragment.read())

    return compute_program, render_program


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    # Create a GLFW window
    window = glfw.create_window(
        width, height, "Compute and Fragment Shader Example", None, None
    )
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    texture = create_textures()

    compute_program, render_program = create_programs()

    while not glfw.window_should_close(window):
        # Use compute shader to draw and update agents
        glUseProgram(compute_program)
        glBindImageTexture(1, texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)
        glDispatchCompute(num_groups_x, num_groups_y, 1)
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        # Render the texture to the screen
        glUseProgram(render_program)
        glBindTexture(GL_TEXTURE_2D, texture)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        glfw.swap_buffers(window)
        glfw.poll_events()

    # Cleanup
    glDeleteProgram(compute_program)
    glDeleteProgram(render_program)
    glDeleteTextures(texture)
    glfw.terminate()


if __name__ == "__main__":
    main()
