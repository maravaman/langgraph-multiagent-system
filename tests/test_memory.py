from core.memory import MemoryManager

def test_stm():
    mm = MemoryManager()
    mm.set_stm("u1", "a1", "hello")
    assert mm.get_stm("u1", "a1") == "hello"

def test_ltm_insert():
    mm = MemoryManager()
    mm.store_ltm("u1", "a1", "Q", "A")
    data = mm.get_ltm_by_user("u1")
    assert len(data) > 0
