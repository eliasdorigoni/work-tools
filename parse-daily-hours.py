import re
import sys
from datetime import datetime
from math import floor
from zlib import crc32
import os

DAILY_FILE_PATH = '/Users/elias.dorigoni/Documents/Laboral/Daily/{}.md'
PARSED_HEADER = '## Horas calculadas'


def get_filepath():
    return DAILY_FILE_PATH.format(sys.argv[1])


def validate_parameters():
    if not len(sys.argv[1:]) >= 1:
        print("One parameter is required")
        quit(1)

    filepath = get_filepath()
    if not os.path.isfile(filepath):
        print("Daily file does not exist as:")
        print("  {}".format(filepath))
        quit(1)


def file_has_been_parsed():
    with open(get_filepath()) as f:
        content = [x.strip() for x in f.readlines()]
        for line in content:
            if line == PARSED_HEADER:
                return True
    return False


def extract_hours_from_file():
    title_found = False
    hours = []
    valid_time_log = re.compile(r'([0-2]?[0-9])[\.:]([0-9]{2})')
    valid_jira_ticket = re.compile(r'([A-Z0-9]{2,4}-[0-9]{2,4})')

    with open(get_filepath()) as f:
        content = [x.strip() for x in f.readlines()]
        content = list(filter(None, content))

    for line in content:
        if not title_found:
            match = re.search('#+ *Horas', line)
            if match:
                title_found = True
            else:
                continue

        m1 = valid_time_log.match(line)
        if m1 is None:
            continue

        description = line[5:].replace('(cont)', '').strip()
        if not description:
            description = '** Sin descripción **'

        m2 = valid_jira_ticket.search(description)
        if m2:
            key = m2.group(1)
        else:
            key = crc32(bytes(description, 'UTF-8'))

        hours.append({
            'time': datetime(2000, 1, 1, int(m1.group(1)), int(m1.group(2))),
            'description': description,
            'key': key,
            'key_is_ticket': True if m2 else False
        })
    return hours


def seconds_to_text(seconds):
    text = []
    minutes = seconds / 60
    hours = 0
    if minutes > 59:
        hours = floor(minutes / 60)
        minutes = minutes % 60

    if hours > 0:
        text.append(str(hours) + "h")

    if minutes > 0:
        text.append(str(int(minutes)) + "m")

    return ' '.join(text)


def get_total_duration_summary(activities):
    # activities == contents from key 'all'

    if len(activities) == 1:
        return seconds_to_text(activities[0]['duration_in_seconds'])

    all_durations = [x['duration_in_seconds'] for x in activities]

    return '{} ({})'.format(
        seconds_to_text(sum(all_durations)),
        " + ".join(seconds_to_text(x) for x in all_durations)
    )


def get_total_duration(activities):
    # activities = contents from key 'all'
    return seconds_to_text(sum([x['duration_in_seconds'] for x in activities]))


def calculate_activities_duration(lines):
    activities = []
    registered_lines = {}
    total_lines = len(lines)
    for index, line in enumerate(lines):
        if index + 1 == total_lines:
            # Last line has no duration
            break

        next_line = lines[index + 1]
        key = crc32(bytes(line['description'], 'UTF-8'))
        description = line['description']
        duration_in_seconds = int((next_line['time'] - line['time']).total_seconds())

        if key in registered_lines:
            found_index = registered_lines[key]
            activities[found_index]['duration_in_seconds'].append(duration_in_seconds)
        else:
            registered_lines[key] = index
            activities.append({
                'description': description,
                'duration_in_seconds': [duration_in_seconds],
            })

    for index, activity in enumerate(activities):
        summary = []
        if len(activity['duration_in_seconds']) > 1:
            total_duration_in_seconds = 0
            for duration in activity['duration_in_seconds']:
                summary.append(seconds_to_text(duration))
                total_duration_in_seconds += duration
        else:
            total_duration_in_seconds = activity['duration_in_seconds'][0]

        activities[index]['duration'] = seconds_to_text(total_duration_in_seconds)
        if len(summary) > 0:
            activities[index]['duration'] += ' ({})'.format(" + ".join(summary))

    return activities


def make_final_detail(lines):
    text = [PARSED_HEADER]
    for line in lines:
        text.append("{} - {}".format(line['duration'], line['description']))
    total_duration_in_seconds = sum([sum(x['duration_in_seconds']) for x in lines])
    text.append("")
    text.append("Total: {}".format(seconds_to_text(total_duration_in_seconds)))
    return text


def show_detail_for_console(lines):
    for line in lines:
        print(line)
    print("------")


def ask_confirmation_to_append_to_file():
    print("¿Guardar? [s/n]")
    answer = input()
    return answer.upper() in ["S"]


def write_detail_to_file(lines):
    with open(get_filepath(), 'a') as f:
        for x in lines:
            f.write(x + "\n")


def exclude_breaks(lines):
    for index, line in enumerate(lines):
        if re.match(r'(almuerzo|break)', line['description'], re.IGNORECASE):
            del lines[index]
    return lines


def run():
    validate_parameters()
    lines = extract_hours_from_file()
    lines = calculate_activities_duration(lines)
    lines = exclude_breaks(lines)
    lines = make_final_detail(lines)
    show_detail_for_console(lines)

    if file_has_been_parsed():
        print("Ya existe un detalle guardado en el archivo.")

    confirm = ask_confirmation_to_append_to_file()
    if confirm:
        write_detail_to_file(lines)
        print("Reporte guardado en {}.".format(get_filepath()))
    else:
        print("Sin cambios.")


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        pass