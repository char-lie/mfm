from numpy import array, nonzero, zeros, ndarray

from src import Face


class ModelFitter:
    """Abstract class for Face fitting procedure.

    Should call Face rendering and wait for response.
    """
    def __init__(self, image, dimensions=199, model=None, initial_face=None,
                 callback=None):
        """Initializes fitter for given image.

        Fits provided number of dimensions of given model to the image.
        """
        self.__image = array(image)
        self.__model = model
        self.__pcs = dimensions
        self._dimensions = (dimensions
                            + Face.LIGHT_COMPONENTS_COUNT
                            + Face.DIRECTION_COMPONENTS_COUNT
                            + Face.SCALE_COMPONENTS_COUNT)
        self.__callback = callback

        self._initial_face = initial_face
        if self._initial_face is None:
            self._initial_face = Face(
                coefficients=zeros(self.__pcs, dtype='f')
            )
        coefficients = self._initial_face.coefficients
        if len(coefficients) != self.__pcs:
            correct_coefficients = zeros(self.__pcs, dtype='f')
            count = min(len(coefficients), self.__pcs)
            correct_coefficients[:count] = coefficients[:count]
            self._initial_face = Face(
                coefficients=correct_coefficients,
                directed_light=self._initial_face.directed_light,
                ambient_light=self._initial_face.ambient_light,
                scale=self._initial_face.scale
            )

    def start(self):
        """Start fitting procedure.

        Should be called by host.
        """
        raise NotImplementedError()

    def finish(self, face):
        """Finish fitting procedure.

        Should be called by Fitter when fitting is finished.
        """
        if self.__callback:
            self.__callback(face)

    def request_face(self, face, label=None):
        """Requests rendered face with given parameters.

        Label will be provided with callback for Fitter to identify
        request, which provoked this response.
        """
        self.__model.request_image(
            face, lambda image: self.receive_image(image, label))

    def receive_image(self, image, index=None):
        """Callback for host on renderer.

        Provides normal vectors and label of Face which was requested.
        """
        raise NotImplementedError()

    def get_face(self, face):
        """Get face image by face object.

        Accepts both `Face` instance
        and Face representation as `NumPy` `array`.
        """
        if isinstance(face, ndarray):
            face = Face.from_array(face)
        return self.__model.get_image(face)

    def get_face_deviation(self, face):
        """Cost function for current face."""
        return self.get_image_deviation(self.get_face(face))

    def get_image_deviation(self, image):
        """Cost function for fitting result."""
        indices = nonzero(image[:, -1])
        if len(image.shape) > 1:
            image = image[:, 0]
        diff = image - self.__image
        return (diff[indices] ** 2).mean()
