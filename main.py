from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import numpy as np
from matplotlib import pyplot as plt

width = 800
height = 800
xmin, xmax = -2.0, 1.0
ymin, ymax = -1.5, 1.5


def create_compute_shader_program(compute_src):
    return compileProgram(
        compileShader(compute_src, GL_COMPUTE_SHADER),
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


def create_ssbo(num_samples=10_000_0):
    ssbo = np.zeros((num_samples, 2), dtype=np.float32)
    for i in range(num_samples):
        ssbo[i][0] = np.random.uniform(xmin, xmax)
        ssbo[i][1] = np.random.uniform(ymin, ymax)

    return ssbo


def fill_uniforms(agent_compute_program, input_data):
    ssbo_size_location = glGetUniformLocation(agent_compute_program, "ssboSize")
    glUseProgram(agent_compute_program)
    glUniform1ui(ssbo_size_location, input_data["ssboSize"])

    xbounds_location = glGetUniformLocation(agent_compute_program, "xbounds")
    glUseProgram(agent_compute_program)
    glUniform2f(xbounds_location, input_data["xbounds"][0], input_data["xbounds"][1])

    ybounds_location = glGetUniformLocation(agent_compute_program, "ybounds")
    glUseProgram(agent_compute_program)
    glUniform2f(ybounds_location, input_data["ybounds"][0], input_data["ybounds"][1])

    max_iterrations_location = glGetUniformLocation(
        agent_compute_program, "maxIterations"
    )
    glUseProgram(agent_compute_program)
    glUniform1ui(max_iterrations_location, input_data["maxIterations"])

    return {
        "ssboSize": ssbo_size_location,
        "xbounds": xbounds_location,
        "ybounds": ybounds_location,
        "maxIterations": max_iterrations_location,
    }


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    # TODO: Maybe use a true headless opengl context, right now the window in still created, just not visible
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(
        width, height, "Compute and Fragment Shader Example", None, None
    )
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    ssbo_data = create_ssbo()
    print("Created SSBO")
    ssbo = bind_ssbo(ssbo_data)
    num_groups_x = (ssbo_data.shape[0] + 8 - 1) // 8

    texture = create_textures()

    compute_program = create_programs()

    fill_uniforms(
        compute_program,
        {
            "ssboSize": ssbo_data.shape[0],
            "xbounds": [xmin, xmax],
            "ybounds": [ymin, ymax],
            "maxIterations": 10000,
        },
    )

    # Use compute shader to draw and update agents
    glUseProgram(compute_program)
    glBindImageTexture(1, texture, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_R32UI)
    glDispatchCompute(num_groups_x, 1, 1)
    glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

    # Read texture data back to CPU (slow, for debugging only)
    glBindTexture(GL_TEXTURE_2D, texture)
    texture_data = np.zeros((height, width), dtype=np.uint32)
    glGetTexImage(GL_TEXTURE_2D, 0, GL_RED_INTEGER, GL_UNSIGNED_INT, texture_data)
    print("Max Value in texture:", np.max(texture_data))

    print(texture_data.shape)
    print(texture_data)

    # Cleanup
    glDeleteProgram(compute_program)
    glDeleteTextures(texture)
    glfw.terminate()


if __name__ == "__main__":
    main()
