import json
import os
import urllib.request
from datetime import datetime

TOKEN = os.environ["GITHUB_TOKEN"]

QUERY = """
query {
  user(login: "ayushjain510") {
    login
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-activity-graph",
    },
)

with urllib.request.urlopen(request) as response:
    data = json.loads(response.read().decode("utf-8"))

if "errors" in data:
    raise RuntimeError(data["errors"])

calendar = (data["data"]["user"]["contributionsCollection"]["contributionCalendar"])

weeks = calendar["weeks"]
total = calendar["totalContributions"]

cell = 12
gap = 4
step = cell + gap

left = 42
top = 48

graph_width = len(weeks) * step
width = left + graph_width + 18
height = top + (7 * step) + 45

levels = [
    "#161B22",
    "#0E2A47",
    "#124A78",
    "#1769A6",
    "#2563EB",
]

max_count = max(
    day["contributionCount"]
    for week in weeks
    for day in week["contributionDays"]
)


def get_level(count):
    if count == 0:
        return 0

    if max_count <= 1:
        return 1

    ratio = count / max_count

    if ratio <= 0.25:
        return 1
    elif ratio <= 0.50:
        return 2
    elif ratio <= 0.75:
        return 3
    else:
        return 4


svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}">'
)

svg.append(
    '<rect width="100%" height="100%" rx="12" fill="#0D1117"/>'
)

svg.append(
    '<rect x="0.5" y="0.5" '
    f'width="{width - 1}" height="{height - 1}" '
    'rx="12" fill="none" stroke="#21262D"/>'
)

svg.append("""
<defs>
    <filter id="blueGlow">
        <feGaussianBlur stdDeviation="2.5" result="blur"/>
        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
</defs>
""")

svg.append(
    '<text x="15" y="23" '
    'fill="#8B949E" '
    'font-family="Arial, sans-serif" '
    'font-size="12">'
    f'GitHub Activity · {total} contributions'
    '</text>'
)

weekdays = ["Mon", "", "Wed", "", "Fri", "", ""]

for row, label in enumerate(weekdays):
    if not label:
        continue

    y = top + row * step + 10

    svg.append(
        f'<text x="6" y="{y}" '
        'fill="#6E7681" '
        'font-family="Arial, sans-serif" '
        'font-size="9">'
        f'{label}'
        '</text>'
    )

previous_month = None

for col, week in enumerate(weeks):

    if not week["contributionDays"]:
        continue

    first_day = datetime.strptime(
        week["contributionDays"][0]["date"],
        "%Y-%m-%d"
    )

    month = first_day.strftime("%b")

    if month != previous_month:

        x = left + col * step

        svg.append(
            f'<text x="{x}" y="{top - 13}" '
            'fill="#6E7681" '
            'font-family="Arial, sans-serif" '
            'font-size="9">'
            f'{month}'
            '</text>'
        )

        previous_month = month

for col, week in enumerate(weeks):

    for day in week["contributionDays"]:

        date = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        )

        row = date.weekday()

        x = left + col * step
        y = top + row * step

        count = day["contributionCount"]
        level = get_level(count)

        svg.append(
            f'<rect '
            f'x="{x}" '
            f'y="{y}" '
            f'width="{cell}" '
            f'height="{cell}" '
            f'rx="3" '
            f'fill="{levels[level]}">'
            f'<title>{day["date"]}: '
            f'{count} contributions</title>'
            f'</rect>'
        )

bot_start = left
bot_end = left + graph_width - 20
bot_y = top + (7 * step) + 23

bug_x = bot_start + (bot_end - bot_start) * 0.52

svg.append(
    f'''
    <g>

        <g opacity="0">
            <animate
                attributeName="opacity"
                values="0;0;1;1;0"
                keyTimes="0;0.38;0.42;0.62;0.68"
                dur="9s"
                repeatCount="indefinite"/>
            <text
                x="{bug_x}"
                y="{bot_y - 4}"
                fill="#F59E0B"
                font-family="monospace"
                font-size="15">
                🐛
            </text>
        </g>

        <g>

            <animateTransform
                attributeName="transform"
                type="translate"
                values="
                    0 0;
                    {bug_x - bot_start - 28} 0;
                    {bug_x - bot_start - 28} 0;
                    {bug_x - bot_start - 28} 0;
                    {bot_end - bot_start} 0;
                    0 0
                "
                keyTimes="
                    0;
                    0.38;
                    0.43;
                    0.58;
                    0.72;
                    1
                "
                dur="9s"
                repeatCount="indefinite"/>

            <rect
                x="{bot_start}"
                y="{bot_y - 14}"
                width="28"
                height="20"
                rx="6"
                fill="#2563EB"
                opacity="0.25"/>

            <rect
                x="{bot_start}"
                y="{bot_y - 12}"
                width="28"
                height="18"
                rx="5"
                fill="#2563EB"/>

            <rect
                x="{bot_start + 5}"
                y="{bot_y - 8}"
                width="18"
                height="10"
                rx="2"
                fill="#0D1117"/>

            <circle
                cx="{bot_start + 10}"
                cy="{bot_y - 3}"
                r="1.5"
                fill="#FFFFFF"/>

            <circle
                cx="{bot_start + 18}"
                cy="{bot_y - 3}"
                r="1.5"
                fill="#FFFFFF"/>

            <line
                x1="{bot_start + 14}"
                y1="{bot_y - 12}"
                x2="{bot_start + 14}"
                y2="{bot_y - 17}"
                stroke="#2563EB"
                stroke-width="2"/>

            <circle
                cx="{bot_start + 14}"
                cy="{bot_y - 19}"
                r="2"
                fill="#60A5FA"/>

        </g>

        <text
            x="{bug_x + 18}"
            y="{bot_y - 2}"
            fill="#3FB950"
            font-family="monospace"
            font-size="13"
            opacity="0">
            ✓
            <animate
                attributeName="opacity"
                values="0;0;0;1;1;0"
                keyTimes="0;0.55;0.60;0.64;0.72;0.78"
                dur="9s"
                repeatCount="indefinite"/>
        </text>

    </g>
    '''
)

svg.append(
    f'''
    <text
        x="{left + 25}"
        y="{bot_y}"
        fill="#2563EB"
        font-family="monospace"
        font-size="10">

        &gt; building...

        <animate
            attributeName="opacity"
            values="1;1;0;0;0;1"
            keyTimes="0;0.37;0.40;0.63;0.70;0.75"
            dur="9s"
            repeatCount="indefinite"/>

    </text>

    <text
        x="{left + 25}"
        y="{bot_y}"
        fill="#F59E0B"
        font-family="monospace"
        font-size="10"
        opacity="0">

        &gt; bug detected!

        <animate
            attributeName="opacity"
            values="0;0;1;1;0"
            keyTimes="0;0.38;0.42;0.58;0.63"
            dur="9s"
            repeatCount="indefinite"/>

    </text>

    <text
        x="{left + 25}"
        y="{bot_y}"
        fill="#3FB950"
        font-family="monospace"
        font-size="10"
        opacity="0">

        &gt; bug fixed ✓

        <animate
            attributeName="opacity"
            values="0;0;0;1;1;0"
            keyTimes="0;0.58;0.63;0.68;0.75;0.80"
            dur="9s"
            repeatCount="indefinite"/>

    </text>
    '''
)

svg.append("</svg>")

with open(
    "github-activity-v2.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(svg))

print(
    f"Generated GitHub activity graph "
    f"with {total} contributions."
)
