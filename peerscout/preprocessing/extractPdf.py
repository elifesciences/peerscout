import PyPDF2  # pylint: disable=import-error


from .convertUtils import\
    get_basename, process_files_in_directory_or_zip, TableOutput, write_tables_to_csv

from .preprocessingUtils import get_data_path, get_db_path


def filename_to_manuscript_no(filename):
    return get_basename(filename).split('-')[-1]


def convert_pdf_file_contents(filename, stream, tables):
    manuscript_no = filename_to_manuscript_no(filename)
    min_line_length = 10
    pdf_reader = PyPDF2.PdfFileReader(stream)
    text = '\n'.join([
        pdf_reader.getPage(page_no).extractText()
        for page_no in range(pdf_reader.numPages)
    ])
    text = '\n'.join([
        line
        for line in text.split('\n')
        if len(line) >= min_line_length
    ])
    tables['article-pdf-content'].append({
        'manuscript-no': manuscript_no,
        'content': text
    })


def main():

    table_names = set([
        'article-pdf-content'
    ])
    tables = dict((table_name, TableOutput(name=table_name)) for table_name in table_names)

    def process_file(filename, content):
        return convert_pdf_file_contents(filename, content, tables)

    csv_path = get_db_path()
    source = get_data_path('articles-pdf')

    process_files_in_directory_or_zip(source, process_file, ext='.pdf')

    write_tables_to_csv(csv_path, tables)

    print("done")


if __name__ == "__main__":
    main()
