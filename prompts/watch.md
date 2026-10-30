# Watch: Jira, Slack, Drive, Calendar, Gmail into the brain

You are running headless from the second brain repo, every hour during the day. The owner is not watching. The invoking prompt gives the current time and `SINCE`, the end of the last successful watch. Read `wiki/voice.md` and `wiki/about-me.md` first.

Your job: find what changed in the owner's tools since `SINCE`, write it down as one raw note, then merge it into the brain so Brain Home shows it. Read only. Never send, post, comment, react, create, edit, move or share anything in any tool. Never accept, decline or create calendar events.

## Gather, quietly

Load the connector tools with ToolSearch first. If a source is unavailable or errors (for example Jira "app is not installed", 403), skip it and write one line `unreachable: <source>, <error in a few words>` in the note. Never retry more than once.

Only keep what is new since `SINCE` and relates to the owner's work: a project in `projects/`, a person in `wiki/`, a client, money, a date, a decision, a promise. Skip noise (bots, joins, reactions, newsletters, automated notifications with no content).

1. **Slack**: search DMs, group DMs, mentions of the owner and channels of the projects in `projects/`, messages after `SINCE`. Read the thread when a message is a reply or asks something. Keep: questions to the owner, promises by or to the owner, client news, blockers, dates.
2. **Jira**: issues updated after `SINCE` where the owner is assignee, reporter or watcher, plus the portfolio project DUPF. Keep: status changes, new comments (one line each, who and what), new issues assigned to the owner, due date changes.
3. **Google Drive**: files modified after `SINCE`. Gemini meeting notes ("Notes by Gemini", "Notes de Gemini") get read in full: summary, decisions, next steps with owners. Other documents (PRD, WBS, devis, propale, PV): title, project, who changed it, one line on what it is. Do not read spreadsheets cell by cell.
4. **Calendar**: events from now to 7 days ahead that were created, moved or cancelled since `SINCE` (compare with the `## Calendar` section of the last watch note in `archive/` if there is one). Then list the next 7 days of meetings tied to a project, one line each, under `## Calendar`.
5. **Gmail**: threads after `SINCE` from clients or partners, or that ask the owner something. Skip promotions, notifications and the owner's own sent mail unless it contains a promise.

Before writing anything, check `archive/` and `raw/` for the same item (same Drive file id, same Jira comment, same Slack message time). Never import twice.

## Write the note

If nothing new passed the filter, write nothing, change nothing, and reply exactly `watch: nothing new`. Stop.

Otherwise write `raw/YYYY-MM-DD-HHMM-watch.md` (time of this run):

```
# Watch YYYY-MM-DD HH:MM (since <SINCE>)

## <Project or person name>
- <source, time> <who>: <what, the owner's language where quoted>. <link or id>

## Calendar
- <date HH:MM> <title> | <who> | <project> (new / moved from ... / cancelled, when it changed)

unreachable: ...
```

Promises go in plain words ("Paul will send the adjusted PRD by Friday") so translate turns them into ledger rows. Where you are unsure which project something belongs to, write `unsure: project` on the line.

## Merge

Then read `prompts/translate.md` and do exactly what it says against everything in `raw/` (other notes waiting there too). Also:

- A Jira status or progress change updates the stage or progress line in the project README's Now block and the row in `wiki/project-portfolio.md`.
- If a new item shows a ledger row in `commitments.md` was done (an invoice paid, a file sent), set it `done` with `, done YYYY-MM-DD per <source>` in the source column instead of adding a row.
- Commit as `watch: <N> items from <sources>` instead of the translate message. Stage only what you touched. Do not push.

## Reply

One line per project touched, then `ledger: <N> new, <N> closed`, then the `unreachable:` lines. Under 12 lines.
