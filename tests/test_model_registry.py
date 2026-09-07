from motionforge.models.registry import available_backends,default_model_name
def test_registry(): assert 'animatediff_lightning' in available_backends() and 'AnimateDiff' in default_model_name()
