Run the watch loop now, from this session.

1. `SINCE` is the content of `~/.second-brain/watch-since`, or one day ago if the file is missing.
2. Read `prompts/watch.md` and follow it exactly.
3. Obey the hard rules in `CLAUDE.md`.
4. When done, write the current time (`date '+%Y-%m-%dT%H:%M:%S%z'`) to `~/.second-brain/watch-since` and run `python3 home/collect.py` so Brain Home shows it.
