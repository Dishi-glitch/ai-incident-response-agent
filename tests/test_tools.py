from src.tools.mock_tools import TOOL_REGISTRY
from src.agents.investigator import validate_tool_arguments

def test_registry_has_expected_tools():
    assert len(TOOL_REGISTRY) >= 25
    assert 'get_model_metrics' in TOOL_REGISTRY
    assert 'check_data_drift' in TOOL_REGISTRY

def test_valid_tool_arguments():
    ok,err=validate_tool_arguments('get_model_metrics',{'metric':'accuracy'})
    assert ok and err is None

def test_invalid_tool_arguments_are_blocked():
    ok,err=validate_tool_arguments('get_model_metrics',{'metric':'made_up'})
    assert not ok

def test_unknown_tool_is_blocked():
    ok,err=validate_tool_arguments('does_not_exist',{})
    assert not ok
