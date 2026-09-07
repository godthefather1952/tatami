from motionforge.system.environment import is_codespaces, environment_name
def test_codespaces_boolean(): assert isinstance(is_codespaces(), bool)
def test_environment_name(): assert environment_name() in {"GitHub Codespaces","Linux/local"}
