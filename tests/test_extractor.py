from unittest.mock import Mock

from src.extractor import Extractor


def test_extract_file_delegates_to_device_client():
    device_client = Mock()
    device_client.read_file.return_value = b"contents"

    result = Extractor(device_client).extract_file("/data/file.txt")

    assert result == b"contents"
    device_client.read_file.assert_called_once_with("/data/file.txt")


def test_extract_all_reads_every_listed_file():
    device_client = Mock()
    device_client.list_files.return_value = ["/a", "/b"]
    device_client.read_file.side_effect = [b"A", b"B"]

    result = Extractor(device_client).extract_all()

    assert result == {"/a": b"A", "/b": b"B"}
