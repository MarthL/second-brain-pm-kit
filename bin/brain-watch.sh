#!/bin/bash
# Every 2 hours on weekdays, 08:10 to 20:10: what changed in Jira, Slack, Drive, Calendar and Gmail since the last watch
# (prompts/watch.md) into raw/, merged into the wiki, projects and ledger, then Brain Home's data.
# Read only in every tool. By hand: bin/brain-watch.sh (FORCE=1 ignores the 45 minute gap)
. "$(dirname "$(readlink -f "$0")")/brain-lib.sh" watch
cd "$SB" || exit 1
brain_paused && { brain_log "watch: paused for a usage limit"; exit 0; }
SINCE_F="$HOME/.second-brain/watch-since"
LOCK="$HOME/.second-brain/watch.lock"
# one watch at a time; a lock older than an hour is a crashed run
if ! mkdir "$LOCK" 2>/dev/null; then
  [ -n "$(find "$LOCK" -maxdepth 0 -mmin +60)" ] || { brain_log "watch: already running"; exit 0; }
  rmdir "$LOCK"; mkdir "$LOCK"
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
# after sleep launchd fires missed hours at once; one run is enough
if [ -z "$FORCE" ] && [ -f "$SINCE_F" ] && [ -n "$(find "$SINCE_F" -mmin -45)" ]; then exit 0; fi
brain_pull
START=$(date '+%Y-%m-%dT%H:%M:%S%z')
# first run: the last day
SINCE=$(cat "$SINCE_F" 2>/dev/null || date -v-1d '+%Y-%m-%dT%H:%M:%S%z')
CONNECTORS="mcp__claude_ai_Slack__slack_search_public_and_private,mcp__claude_ai_Slack__slack_read_channel,mcp__claude_ai_Slack__slack_read_thread,mcp__claude_ai_Slack__slack_search_channels,mcp__claude_ai_Slack__slack_read_user_profile"
CONNECTORS="$CONNECTORS,mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql,mcp__claude_ai_Atlassian__getJiraIssue,mcp__claude_ai_Atlassian__atlassianUserInfo,mcp__claude_ai_Atlassian__getAccessibleAtlassianResources"
CONNECTORS="$CONNECTORS,mcp__claude_ai_Google_Drive__search_files,mcp__claude_ai_Google_Drive__list_recent_files,mcp__claude_ai_Google_Drive__read_file_content,mcp__claude_ai_Google_Drive__get_file_metadata"
CONNECTORS="$CONNECTORS,mcp__claude_ai_Google_Calendar__list_events,mcp__claude_ai_Google_Calendar__list_calendars,mcp__claude_ai_Gmail__search_threads,mcp__claude_ai_Gmail__get_thread"
for n in $SLACK_WORKSPACES; do CONNECTORS="$CONNECTORS,mcp__slack-$n"; done
TOOLS="Read,Write,Edit,Glob,Grep,ToolSearch,$CONNECTORS,Bash(git add:*),Bash(git commit:*),Bash(git mv:*),Bash(git status:*),Bash(mv:*),Bash(mkdir:*),Bash(ls:*),Bash(python3 -c:*)"
OUT=$("$CLAUDE" -p "Now is $(date '+%Y-%m-%d %H:%M %z'). SINCE=$SINCE. Read prompts/watch.md and do exactly what it says." \
  --output-format text --allowedTools "$TOOLS" < /dev/null 2>&1)
RC=$?; echo "$OUT" | tail -15 | sed 's/^/  /' >> "$LOG"
if [ $RC -ne 0 ]; then brain_check_limit "$OUT" || brain_fail "watch failed, exit $RC"; exit 1; fi
echo "$START" > "$SINCE_F"
brain_ok
python3 home/collect.py >/dev/null 2>>"$LOG"
if echo "$OUT" | grep -q "watch: nothing new"; then brain_log "watch: nothing new since $SINCE"; exit 0; fi
brain_log "watch: done"
brain_notify "watch" "$(echo "$OUT" | grep -m1 . | cut -c1-120)"
brain_push
