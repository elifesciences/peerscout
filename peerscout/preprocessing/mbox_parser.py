'''
specialised mbox file parser that can handle large file sizes
'''

MESSAGE_START_PREFIX = b'From '


def split_messages_skip_content(line_generator):
    lines = []
    seen_message_start = False
    seen_content_separator = False
    for line in line_generator:
        if line.startswith(MESSAGE_START_PREFIX):
            if len(lines) > 0:
                yield lines
            lines = []
            seen_message_start = True
            seen_content_separator = False
        elif seen_message_start and not seen_content_separator:
            trimmed_line = line.rstrip()
            if len(trimmed_line) == 0:
                seen_content_separator = True
            else:
                lines.append(trimmed_line)
    if seen_message_start:
        yield lines


def parse_header_properties(header_lines, required_keys=None, encoding='utf-8'):
    current_name = None
    current_value = None
    for line in header_lines:
        if len(line) > 0:
            if chr(line[0]).isalpha():
                sep_index = line.index(b':')
                if sep_index > 0:
                    if current_name is not None and current_value is not None:
                        yield current_name, current_value
                    current_name = line[:sep_index].decode(encoding)
                    if required_keys is None or current_name in required_keys:
                        current_value = line[sep_index + 1:].decode(encoding).strip()
                    else:
                        current_value = None
                else:
                    if current_value is not None:
                        current_value += '\n' + line.decode(encoding).strip()
    if current_name is not None and current_value is not None:
        yield current_name, current_value
