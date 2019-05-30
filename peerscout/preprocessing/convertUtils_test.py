from datetime import datetime
import os
from unittest.mock import Mock

from .convertUtils import (
    sort_relative_filenames_by_file_modified_time,
    process_files_in_directory
)

FILE_1 = 'file1.dummy'
FILE_2 = 'file2.dummy'


def _create_dummy_file(parent, filename, dt):
    p = parent.join(filename)
    p.write('dummy')
    os.utime(p, (dt.timestamp(), dt.timestamp()))
    return p


class TestSortRelativeFilenamesByFileModifiedTime:
    def test_should_return_empty_list_if_filenames_are_empty(self, tmpdir):
        assert sort_relative_filenames_by_file_modified_time(str(tmpdir), []) == []

    def test_should_return_file_with_earlier_timestamp_first(self, tmpdir):
        _create_dummy_file(tmpdir, FILE_1, datetime(2012, 1, 1))
        _create_dummy_file(tmpdir, FILE_2, datetime(2011, 1, 1))

        assert sort_relative_filenames_by_file_modified_time(
            str(tmpdir), [FILE_1, FILE_2]
        ) == [FILE_2, FILE_1]


class TestProcessFilesInDirectory:
    def test_should_return_file_with_earlier_timestamp_first(self, tmpdir):
        _create_dummy_file(tmpdir, FILE_1, datetime(2012, 1, 1))
        _create_dummy_file(tmpdir, FILE_2, datetime(2011, 1, 1))

        process_file = Mock()
        process_files_in_directory(str(tmpdir), process_file)
        filename_args = [a[0][0] for a in process_file.call_args_list]
        assert filename_args == [FILE_2, FILE_1]
