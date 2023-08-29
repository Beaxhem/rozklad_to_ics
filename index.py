from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta, timezone

with open("input.html") as f:
    soup = BeautifulSoup(f, "html.parser")

element = soup.find("div", {"class": "sc-bXCLTC hICujh"})
children = element.findChildren("div", recursive=False)[8:]

WEEK_NUMBER = 1
START_DAY = 4 if WEEK_NUMBER == 1 else 11
DAYS = 6
TIME = [
  {
    "hour": 8,
    "minute": 30
  },
  {
    "hour": 10,
    "minute": 25
  },
  {
    "hour": 12,
    "minute": 20
  },
  {
    "hour": 14,
    "minute": 15
  },
  {
    "hour": 16,
    "minute": 10
  },
  {
    "hour": 18,
    "minute": 30
  }
]
DAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def parseBlock(markup):
  children = markup.findChildren("div", recursive=False)
  lessonType = children[0].text
  lessonName = children[1].text
  return Lesson(lessonType, lessonName) 


class Lesson:
  def __init__(self, type, name):
    self.type = type
    self.name = name

  def __str__(self):
    return f"[{self.type}] {self.name}"

class TimeBlock:
  def __init__(self, dayIndex) -> None:
    self.dayIndex = dayIndex
    self.events = []

  def addEvent(self, event):
    self.events.append(event)

  def __str__(self):
    day = DAY[self.dayIndex]
    events = "\n".join([str(event) for event in self.events])
    return f"{day}\n{events}"


class CalendarRow:
  def __init__(self, blocks, timeIndex) -> None:
    self.blocks = blocks
    self.timeIndex = timeIndex
    self.events = []

  def parseChildren(self):
    for i in range(len(self.blocks)):
      block = self.blocks[i]
      children = block.findChildren("div", recursive=False)
      timeBlock = TimeBlock(i)
      if (len(children) == 1):
        timeBlock.addEvent(parseBlock(children[0]))
      else:
        for block in children:
          children = block.findChildren("div", recursive=False)
          if (len(children) == 1):
            timeBlock.addEvent(parseBlock(children[0]))
      
      self.events.append(timeBlock)

rows = []

for timeIndex in range(0, len(children), DAYS + 1):
    row = CalendarRow(children[timeIndex: timeIndex + DAYS], timeIndex=timeIndex)
    row.parseChildren()
    rows.append(row)

for row in rows:
  t = TIME[row.timeIndex // 7]
  print(f"{t['hour']}:{t['minute']}")
  for event in row.events:
    print(str(event))
  print()


class ContentLine:
  def __init__(self, name, params) -> None:
    self.name = name
    self.params = params
  
  def __str__(self):
    values = [f'{key}={",".join(value)}' for key, value in self.params.items()]
    return f"{self.name}:{';'.join(values)}"
  
  def clone(self):
    return ContentLine(self.name, self.params)
    

c = Calendar()

localTz = datetime.now(timezone(timedelta(0))).astimezone().tzinfo

for timeIndex in range(len(rows)):
  row = rows[timeIndex]
  t = TIME[row.timeIndex // 7]
  for event in row.events:
    for lesson in event.events:
      e = Event(name=str(lesson), 
                begin=datetime(2023, 9, START_DAY + event.dayIndex, t["hour"], t["minute"], tzinfo=localTz), 
                duration=timedelta(hours=1, minutes=30))
      e.extra.append(ContentLine('RRULE', {'FREQ': ['WEEKLY'], 'INTERVAL': ["2"], }))
      c.events.add(e)
    

with open('output.ics', 'w') as my_file:
    my_file.writelines(c)

