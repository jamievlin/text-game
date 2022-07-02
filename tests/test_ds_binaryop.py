from utils.utils import exec_from_text


def test_ds_equality():
    program_text = """
    let var1;
    let var2;
    
    begin block start
        var1 = 50 == 200;
        var2 = 100 == 100;
    end;
    """

    vm = exec_from_text(program_text)
    gvars = vm.context.global_vars
    assert gvars['var1'] is False
    assert gvars['var2'] is True
