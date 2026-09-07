class MotionForgeError(RuntimeError):
    """Base application error."""

class HardwareError(MotionForgeError):
    pass

class MemorySafetyError(HardwareError):
    pass

class ModelDownloadError(MotionForgeError):
    pass

class ModelLoadError(MotionForgeError):
    pass

class GenerationError(MotionForgeError):
    pass

class EncodingError(MotionForgeError):
    pass

class ConfigurationError(MotionForgeError):
    pass
