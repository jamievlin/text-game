import os

from dialog_script_vm.vm import DialogScriptVM
from instgen.ds_compiler import program_from_text

TEST_RESOURCES_DIR = 'test_resources'


def from_test_resources(filename: str) -> os.PathLike:
    # noinspection PyTypeChecker
    return os.path.join(TEST_RESOURCES_DIR, filename)


def exec_from_text(text: str) -> DialogScriptVM:
    prog, _ = program_from_text(text)
    vm = DialogScriptVM(prog)
    vm.execute()
    return vm
