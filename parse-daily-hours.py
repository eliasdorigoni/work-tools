import re
import sys
from datetime import datetime
from math import floor
from zlib import crc32
import os


DAILY_FILEPATH_FORMAT = os.environ["DAILY_FILEPATH_FORMAT"]
PARSED_HEADER = '## Horas calculadas'
CURRENT_DAILY_FILEPATH = None
VALID_TIME_LOG = re.compile(r'([0-2]?[0-9])[\.:]([0-9]{2})')
VALID_JIRA_TICKET = re.compile(r'([A-Z0-9]{2,4}-[0-9]{2,4})')


def remove_accents(text: str) -> str:
    return text.replace('á', 'a').replace('Á', 'A')\
        .replace('é', 'e').replace('É', 'E')\
        .replace('í', 'i').replace('Í', 'I')\
        .replace('ó', 'o').replace('Ó', 'O')\
        .replace('ú', 'u').replace('Ú', 'U')


def get_filepath() -> str:
    global CURRENT_DAILY_FILEPATH
    if CURRENT_DAILY_FILEPATH is not None:
        return CURRENT_DAILY_FILEPATH

    filename = sys.argv[1]
    path = DAILY_FILEPATH_FORMAT.format(filename)
    if os.path.isfile(path):
        CURRENT_DAILY_FILEPATH = path
        return path

    match = re.match(r'(\d{4})(\d{2})(\d{2})', filename)
    if match:
        filename = "{}-{}-{}".format(match.group(1), match.group(2), match.group(3))
        path = DAILY_FILEPATH_FORMAT.format(filename)
        if os.path.isfile(path):
            CURRENT_DAILY_FILEPATH = path
            return path

    print("Daily file does not exist.")
    return ""


def validate_parameters() -> None:
    if not len(sys.argv[1:]) >= 1:
        print("One parameter is required")
        quit(1)

    filepath = get_filepath()
    if not os.path.isfile(filepath):
        print("Daily file does not exist as:")
        print("  {}".format(filepath))
        quit(1)


def warn_if_file_has_been_parsed() -> None:
    with open(get_filepath()) as f:
        content = [x.strip() for x in f.readlines()]

    for line in content:
        if line == PARSED_HEADER:
            print("Ya existe un detalle guardado en el archivo.")
            break


def guess_description_prefix(description: str) -> str:
    desc = remove_accents(description).lower()

    if VALID_JIRA_TICKET.match(description):
        return description

    if "daily" in desc:
        return "SAN-2406 - " + description

    if "organizacion" in desc or "carga de horas" in desc:
        return "SAN-2399 - " + description

    if "refinamiento" in desc and "backlog" in desc:
        return "SAN-2406 - " + description

    if ("pre" in desc and "planning" in desc) or "planning" in desc:
        return "SAN-2406 - " + description

    if desc == "retro" or desc == "retrospectiva":
        return "SAN-2406 - " + description

    if "tareas varias" in desc or "tickets varios" in desc:
        return "SAN-2399 - " + description

    if "capacitacion" in desc:
        return "SAN-2403 - " + description

    return description


def extract_hours_from_file() -> list:
    title_found = False
    hours = []

    with open(get_filepath()) as f:
        content = [x.strip() for x in f.readlines()]
        content = list(filter(None, content))

    for line in content:
        if not title_found:
            match = re.search('# Horas', line)
            if match:
                title_found = True
            else:
                continue

        m = VALID_TIME_LOG.match(line)
        if m is None:
            continue

        task_time = datetime(2000, 1, 1, int(m.group(1)), int(m.group(2)))

        description = line[5:].strip()
        if not description:
            description = '** Sin descripción **'
        elif is_break(description):
            continue

        description = guess_description_prefix(description)

        m = VALID_JIRA_TICKET.search(description)
        if m:
            key = m.group(1)
        else:
            key = crc32(bytes(description, 'UTF-8'))

        hours.append({
            'time': task_time,
            'description': description,
            'key': key,
            'key_is_ticket': m is not None
        })
    return hours


def seconds_to_text(seconds: int) -> str:
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


def get_total_duration_summary(activities: list) -> str:
    # activities == contents from key 'all'

    if len(activities) == 1:
        return seconds_to_text(activities[0]['duration_in_seconds'])

    all_durations = [x['duration_in_seconds'] for x in activities]

    return '{} ({})'.format(
        seconds_to_text(sum(all_durations)),
        " + ".join(seconds_to_text(x) for x in all_durations)
    )


def get_total_duration(activities: list) -> str:
    # activities = contents from key 'all'
    return seconds_to_text(sum([x['duration_in_seconds'] for x in activities]))


def calculate_activities_duration(lines: list) -> list:
    activities = []
    registered_lines = {}

    for index, line in enumerate(lines):
        try:
            next_line = lines[index + 1]
        except IndexError:
            break # This is the last line and has no duration.

        key = line['key']
        description = line['description']
        duration_in_seconds = int((next_line['time'] - line['time']).total_seconds())

        if key not in registered_lines:
            registered_lines[key] = len(activities)
            activities.append({
                'key': key,
                'key_is_ticket': line['key_is_ticket'],
                'all': [{
                    'description': description,
                    'duration_in_seconds': duration_in_seconds,
                }]
            })
        else:
            index = registered_lines[key]
            activities[index]['all'].append({
                'description': description,
                'duration_in_seconds': duration_in_seconds,
            })

    return activities


def make_final_detail(lines: list) -> list:
    text = [PARSED_HEADER]
    total_duration_in_seconds = 0
    for line in lines:
        if len(line['all']) > 1:
            if line['key_is_ticket']:
                text.append("{} -> {}".format(
                    get_total_duration(line['all']),
                    line['key']
                ))
            else:
                text.append("{} ->".format(get_total_duration(line['all'])))

            for item in line['all']:
                text.append("    + {} - {}".format(
                    seconds_to_text(item['duration_in_seconds']),
                    item['description'])
                )
        else:
            text.append(
                "{} - {}".format(
                    get_total_duration_summary(line['all']),
                    ". ".join([x['description'] for x in line['all'] ])
                )
            )
        total_duration_in_seconds += sum([x['duration_in_seconds'] for x in line['all']])

    text.append("")
    text.append("Total: {}".format(seconds_to_text(total_duration_in_seconds)))
    return text


def show_detail_for_console(lines: list) -> None:
    for line in lines:
        print(line)
    print("------")


def ask_confirmation_to_append_to_file() -> bool:
    print("Enter (vacío) para guardar reporte:")
    answer = input()
    return len(answer) == 0


def write_detail_to_file(lines: list) -> None:
    prev_notes = [
        "\n\n```\n",
        "---- https://geopagos.atlassian.net/issues/?filter=14277\n",
        "2406 Meeting Admin\n",
        "2403 Capacitación/Training\n",
        "2415 Soporte a otros equipos\n",
        "2399 Unassigned time\n",
        "2444 Soporte getnet\n",
        "2404 Team building\n",
        "2401 Feriados\n",
        "2402 Vacaciones\n",
        "```\n\n",
    ]
    with open(get_filepath(), 'a') as f:
        f.writelines(prev_notes)
        for x in lines:
            f.write(x + "\n")


def is_break(description: str) -> bool:
    return re.match(r'(almuerzo|break)', description, re.IGNORECASE) is not None


def dd(lines: list) -> None:
    for line in lines:
        print(line)
    exit()


def run() -> None:
    validate_parameters()
    lines = extract_hours_from_file()
    lines = calculate_activities_duration(lines)
    lines = make_final_detail(lines)
    show_detail_for_console(lines)
    warn_if_file_has_been_parsed()

    confirm = ask_confirmation_to_append_to_file()
    if confirm:
        write_detail_to_file(lines)
        print("Reporte guardado en {}.".format(get_filepath()))


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        pass
