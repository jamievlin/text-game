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


def test_ds_andop():
    program_text = """
    let var1;
    let var2;
    let var3;
    let var4;
    
    begin block start
        var1 = 100 and false;
        var2 = true and 25;
        var3 = false && true;
        var4 = true && true;
    end;
    """

    vm = exec_from_text(program_text)
    gvars = vm.context.global_vars
    assert gvars['var1'] is False
    assert gvars['var2'] is 25
    assert gvars['var3'] is False
    assert gvars['var4'] is True


def test_ds_orop():
    program_text = """
    let var1;
    let var2;
    let var3;
    let var4;
    
    begin block start
        var1 = 100 or false;
        var2 = 0 or 0;
        var3 = false || false;
        var4 = true || false;
    end;
    """

    vm = exec_from_text(program_text)
    gvars = vm.context.global_vars
    assert gvars['var1'] is 100
    assert gvars['var2'] is 0
    assert gvars['var3'] is False
    assert gvars['var4'] is True


def test_ds_parentheses():
    program_text = """
    let var1;
    let var2;
    
    begin block start
        var1 = (false && false) || true;
        var2 = false && (false || true);
    end;
    """

    vm = exec_from_text(program_text)
    gvars = vm.context.global_vars
    assert gvars['var1'] is True
    assert gvars['var2'] is False
