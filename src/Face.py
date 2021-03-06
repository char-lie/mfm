import logging

from numpy import array, zeros, ones, concatenate, sin, cos, arcsin

ERROR_TEXT = {
    '3D_VECTOR': "{} should be represented by 3D vector, "
                 "but array of shape {} provided",
    'NUMPY_ARRAY': "{} should be represented by flat array, "
                   "but array of shape {} with {} dimensions provided"
}


def process_vector3d(value, name):
    value = array(value, dtype='f')
    if value.shape != (3,):
        raise ValueError(ERROR_TEXT['3D_VECTOR'].format(name, value.shape))
    return value


def spherical_to_cartesian(phi, theta, radius=1.0):
    """Convert spherical coordinates to cartesian.

    Given sinus of polar and azimuthal angle, and radial distance,
    calculate cartesian coordinates of the point.
    """
    sin_phi = sin(phi)
    sin_theta = sin(theta)

    cos_phi = cos(phi)
    cos_theta = cos(theta)

    return array([
        radius * sin_theta * cos_phi,
        radius * sin_theta * sin_phi,
        radius * cos_theta
    ])


class Face(object):
    """Class to represent Face instances."""

    LIGHT_COMPONENTS_COUNT = 3
    DIRECTION_COMPONENTS_COUNT = 3
    SCALE_COMPONENTS_COUNT = 3
    NON_PCS_COUNT = (
        LIGHT_COMPONENTS_COUNT + DIRECTION_COMPONENTS_COUNT
        + SCALE_COMPONENTS_COUNT)

    DIRECTION_COMPONENTS_START = - NON_PCS_COUNT
    DIRECTION_COMPONENTS_END = (DIRECTION_COMPONENTS_START
                                + DIRECTION_COMPONENTS_COUNT)
    SCALE_COMPONENTS_START = DIRECTION_COMPONENTS_END
    SCALE_COMPONENTS_END = SCALE_COMPONENTS_START + SCALE_COMPONENTS_COUNT
    LIGHT_COMPONENTS_START = SCALE_COMPONENTS_END
    LIGHT_COMPONENTS_END = LIGHT_COMPONENTS_START + LIGHT_COMPONENTS_COUNT

    NON_PCS_SLICE = slice(-NON_PCS_COUNT, None)
    PCS_SLICE = slice(0, -NON_PCS_COUNT)
    LIGHT_COMPONENTS_SLICE = slice(LIGHT_COMPONENTS_START,
                                   LIGHT_COMPONENTS_END or None)
    DIRECTION_COMPONENTS_SLICE = slice(DIRECTION_COMPONENTS_START,
                                       DIRECTION_COMPONENTS_END or None)
    SCALE_COMPONENTS_SLICE = slice(SCALE_COMPONENTS_START,
                                   SCALE_COMPONENTS_END or None)

    __initial_phi = 0.0
    __initial_theta = 0.0

    def __init__(self, ambient_light=0, directed_light=(0, 0, 0),
                 position=(0, 0, 1), scale=(1, 1, 1), coefficients=()):
        """Create new Face."""
        self.__directed_light = None
        self.__ambient_light = None
        self.__position = None
        self.__scale = None

        self.ambient_light = ambient_light
        self.directed_light = directed_light
        self.position = position
        self.scale = scale

        self.__coefficients = array(coefficients, dtype='f')
        if self.__coefficients.ndim != 1:
            raise ValueError(ERROR_TEXT['NUMPY_ARRAY'].format(
                'Coefficients', self.__coefficients.shape,
                self.__coefficients.ndim))

    @property
    def position(self):
        """Get position."""
        return self.__position

    @property
    def position_cartesian(self):
        """Get directed light vector from spherical coordinates."""
        phi = arcsin(self.__position[0]) + Face.__initial_phi
        theta = arcsin(self.__position[1]) + Face.__initial_theta
        return spherical_to_cartesian(phi, theta)

    @position.setter
    def position(self, position):
        """Set position vector."""
        self.__position = process_vector3d(position, 'Position')

    @property
    def scale(self):
        """Get scale."""
        return self.__scale

    @scale.setter
    def scale(self, scale):
        """Set scales for axes."""
        self.__scale = process_vector3d(scale, 'Shape')

    @property
    def directed_light(self):
        """Get directed light vector."""
        return self.__directed_light

    @property
    def directed_light_cartesian(self):
        """Get directed light vector from spherical coordinates."""
        phi = arcsin(self.__directed_light[0]) + Face.__initial_phi
        theta = arcsin(self.__directed_light[1]) + Face.__initial_theta
        return spherical_to_cartesian(phi, theta)

    @directed_light.setter
    def directed_light(self, directed_light):
        """Set directed light vector."""
        self.__directed_light = process_vector3d(directed_light, 'Light')

    @property
    def ambient_light(self):
        """Get ambient light."""
        return self.__ambient_light

    @ambient_light.setter
    def ambient_light(self, ambient_light):
        """Set ambient light."""
        self.__ambient_light = ambient_light

    @property
    def light(self):
        """Get light vector."""
        return concatenate((self.directed_light, [self.ambient_light]))

    @property
    def light_cartesian(self):
        """Get light from spherical coordinates."""
        return concatenate((self.directed_light_cartesian,
                            [self.directed_light[2]]))

    @property
    def coefficients(self):
        """Get array of Face coefficients."""
        return self.__coefficients

    @property
    def as_array(self):
        """Get NumPy array representation of the Face."""
        result = zeros(self.coefficients.size + Face.NON_PCS_COUNT, dtype='f')
        result[Face.PCS_SLICE] = self.coefficients
        result[Face.DIRECTION_COMPONENTS_SLICE] = self.position
        result[Face.LIGHT_COMPONENTS_SLICE] = self.directed_light
        result[Face.SCALE_COMPONENTS_SLICE] = self.scale
        return result

    @staticmethod
    def set_initial_rotation(phi=0.0, theta=0.0):
        """Set initial rotation of Face.

        Given angles will be added to light and rotation vector.
        """
        Face.__initial_phi = phi
        Face.__initial_theta = theta

    @staticmethod
    def from_array(parameters):
        """Create Face from array of parameters."""
        coefficients = parameters[Face.PCS_SLICE]
        position = parameters[Face.DIRECTION_COMPONENTS_SLICE]
        directed_light = parameters[Face.LIGHT_COMPONENTS_SLICE]
        scale = parameters[Face.SCALE_COMPONENTS_SLICE]

        float_format = '{:>6.04}'
        vector_3d_format = ', '.join([float_format] * 3)
        coefficients_format = ', '.join([float_format] * len(coefficients))

        format_str = ''
        format_str += 'Light: <' + vector_3d_format + '>;'
        format_str += ' Direction: <' + vector_3d_format + '>;'
        format_str += ' Scale: <' + vector_3d_format + '>;'
        format_str += ' Coefficients: <' + coefficients_format + '>'

        components = (directed_light.tolist() + position.tolist()
                      + scale.tolist() + coefficients.tolist())
        logging.debug(format_str.format(*components))

        return Face(coefficients=coefficients,
                    directed_light=directed_light,
                    scale=scale,
                    position=position)
