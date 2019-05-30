from io import BytesIO

import numpy as np
import pandas as pd

from .convertEditorsCsv import (
    extract_distinct_emails_from_data_frame,
    convert_csv_file_to
)

EMAIL_1 = 'email1@test.ci'
EMAIL_2 = 'email2@test.ci'

CSV_HEADER = '\n'.join([
    "Description",
    "Generated on ...",
    ""
])


class TestExtractDistinctEmailsFromDataFrame:
    def test_should_extract_single_primary_email_address(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': EMAIL_1
        }])) == {EMAIL_1}

    def test_should_extract_multiple_primary_email_addresses(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': EMAIL_1
        }, {
            'email': EMAIL_2
        }])) == {EMAIL_1, EMAIL_2}

    def test_should_extract_primary_email_address_only_once(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': EMAIL_1
        }, {
            'email': EMAIL_1
        }])) == {EMAIL_1}

    def test_should_extract_secondary_email_address_if_column_present(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': EMAIL_1,
            'secondary_email': EMAIL_2
        }])) == {EMAIL_1, EMAIL_2}

    def test_should_ignore_blank_primary_email_address(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': '',
            'secondary_email': EMAIL_2
        }])) == {EMAIL_2}

    def test_should_ignore_blank_secondary_email_address(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': EMAIL_1,
            'secondary_email': ''
        }])) == {EMAIL_1}

    def test_should_strip_spaces_and_ignore_blank(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': ' ',
            'secondary_email': ' %s ' % EMAIL_2
        }])) == {EMAIL_2}

    def test_should_ignore_nan_secondary_email_address(self):
        assert extract_distinct_emails_from_data_frame(pd.DataFrame([{
            'email': np.nan,
            'secondary_email': np.nan
        }])) == set()


class TestConvertCsvFileTo:
    def test_should_convert_email_addresses(self, tmpdir):
        output_file = tmpdir.join('emails.lst')
        content = '\n'.join([
            CSV_HEADER,
            "email",
            EMAIL_1,
            EMAIL_2
        ])
        convert_csv_file_to(
            'dummy.csv',
            BytesIO(content.encode('utf-8')),
            str(output_file)
        )
        assert output_file.read() == '\n'.join([EMAIL_1, EMAIL_2])
