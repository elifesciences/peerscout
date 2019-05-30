from os.path import basename, splitext

from .convertUtils import\
    TableOutput, process_files_in_directory_or_zip,\
    parse_xml_file, write_tables_to_csv

from .preprocessingUtils import get_data_path, get_db_path


def join_text(a, b):
    if a != '' and b != '':
        return a + ' ' + b
    return a + b


def get_deep_text(element):
    text = element.text or ''
    for subelement in element:
        text = join_text(text, get_deep_text(subelement))
    text = join_text(text, element.tail or '')
    return text


def convert_xml(doc, tables, manuscript_no, version_no):
    for body in doc.findall('body'):
        body_text = get_deep_text(body)
        tables['article-content'].append({
            'manuscript-no': manuscript_no,
            'version-no': version_no,
            'content': body_text
        })


def filename_to_basename(filename):
    return splitext(basename(filename))[0]


def filename_to_manuscript_no(filename):
    return filename_to_basename(filename).split('-')[1]


def filename_to_version_no(filename):
    return filename_to_basename(filename).split('-')[-1][1:]


def convert_xml_file_contents(filename, stream, tables):
    doc = parse_xml_file(stream)
    manuscript_no = filename_to_manuscript_no(filename)
    version_no = filename_to_version_no(filename)
    convert_xml(doc, tables, manuscript_no, version_no)


def main():

    table_names = set([
        'article-content'
    ])
    tables = dict((table_name, TableOutput(name=table_name)) for table_name in table_names)

    def process_file(filename, content):
        return convert_xml_file_contents(filename, content, tables)

    csv_path = get_db_path()
    source = get_data_path('articles-xml')

    process_files_in_directory_or_zip(source, process_file, ext='.xml')

    write_tables_to_csv(csv_path, tables)

    print("done")


if __name__ == "__main__":
    main()
