
import inspect
import os.path
# Contains logger for the toto example.
from typing import List
from dataclasses import dataclass

_log_content: List[str] = []

@dataclass
class LogEvent:
  line: int
  fpath: str
  text: str

class Logger(object):
  _log_content: List[str] = []

  @classmethod
  def log(cls, text: str = 'hi', frame_info = None):
    if frame_info is None:
      frame_info = inspect.stack()[1]
  
    file_path = frame_info.filename 
    lineno = frame_info.lineno
  
    # Try to remove unecessary path from the
    commonprefix = os.path.commonprefix([__file__, file_path])
    fpath = file_path[len(commonprefix):]
  
    cls._log_content.append(LogEvent(lineno, fpath, text))

  @classmethod
  def pull_logs(cls) -> List[str]:
    res, cls._log_content[:] = list(cls._log_content), []
    return res
