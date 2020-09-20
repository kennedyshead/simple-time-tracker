from pathlib import Path

from kivy import platform
from kivy.storage.dictstore import DictStore

file_path = Path('.')

if platform == 'macosx':
    file_path = Path(
        '~/Library/Application Support/%s' % 'simple-time-tracker'
    ).expanduser()
    file_path.mkdir(parents=True, exist_ok=True)

store = DictStore(file_path.joinpath('settings.json'))
