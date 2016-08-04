from os.path import dirname, abspath, join

from OpenGL.GL import glCreateProgram, glLinkProgram, glGetProgramiv
from OpenGL.GL import glGenVertexArrays, glBindVertexArray, glGenBuffers
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_LINK_STATUS
from OpenGL.GL import GL_TRUE, GL_STATIC_DRAW, GL_FLOAT, GL_FALSE
from OpenGL.GL import glBindBuffer, glBufferData, glVertexAttribPointer
from OpenGL.GL import glEnableVertexAttribArray, glGetAttribLocation
from OpenGL.GL import glCreateShader, glShaderSource, glCompileShader
from OpenGL.GL import glAttachShader, GL_ARRAY_BUFFER, glUseProgram
from OpenGL.GL import glGetUniformLocation, glUniformMatrix4fv

from OpenGL.arrays.vbo import VBO

from numpy import concatenate


SHADERS_PATH = dirname(abspath(__file__))


class ShadersHelper:
    """Helper class to work with program and shaders."""

    def __init__(self, vertex, fragment, number_of_buffers=0):
        """Initialize program with shaders."""
        self.__program = glCreateProgram()

        self.__load_shader(join(SHADERS_PATH, vertex), GL_VERTEX_SHADER)
        self.__load_shader(join(SHADERS_PATH, fragment), GL_FRAGMENT_SHADER)

        glLinkProgram(self.__program)
        assert glGetProgramiv(self.__program, GL_LINK_STATUS) == GL_TRUE

        self.__vao_id = glGenVertexArrays(1)
        glBindVertexArray(self.__vao_id)
        self.__vbo_id = glGenBuffers(number_of_buffers)

        self.__attributes = []

    def __load_shader(self, shader_filename, shader_type):
        """Load shader of specific type from file."""
        shader_source = ''
        with open(shader_filename) as shader_file:
            shader_source = shader_file.read()
            assert shader_source

        shader_id = glCreateShader(shader_type)
        glShaderSource(shader_id, shader_source)
        glCompileShader(shader_id)
        glAttachShader(self.__program, shader_id)

    def add_attribute(self, vid, data, name):
        """Add array vertex attribute for shaders."""
        if data.ndim > 1:
            data = data.flatten()
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo_id[vid])
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glVertexAttribPointer(glGetAttribLocation(self.__program, name),
                              3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(vid)
        self.__attributes.append(data)

    def use_shaders(self):
        """Switch shaders on."""
        glUseProgram(self.__program)
        glBindVertexArray(self.__vao_id)

    def bind_uniform_matrix(self, data, name):
        """Bind uniform matrix parameter."""
        location = glGetUniformLocation(self.__program, name)
        assert location >= 0
        glUniformMatrix4fv(location, 1, GL_FALSE, data.flatten())

    def bind_buffer(self):
        """Prepare attributes and bind them."""
        VBO(concatenate(self.__attributes)).bind()

    def clear(self):
        """Unbind all bound entities and clear cache."""
        self.__attributes = []
        glUseProgram(0)
        glBindVertexArray(0)
