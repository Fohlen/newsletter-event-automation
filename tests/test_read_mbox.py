from src.message import read_mbox


def test_read_mbox(data_dir):
    messages = list(read_mbox(
        data_dir / "mbox",
        ["schoener-wohnen@lists.mtmedia.org"],
        "[schoener-wohnen-tuebingen] ",
        "___________________________"
    ))
    assert len(messages) == 20
