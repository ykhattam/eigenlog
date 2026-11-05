#!/usr/bin/env bash
# reflect.sh: the same log, asked in the shell, then kept in git.
# The pipe | sends one command's output into the next command's input.
# Limit: cut and grep read plain commas, so they break on a CSV field that
# contains a comma inside quotes. Keep observations free of commas here, or use
# the Python or SQL versions, which parse CSV properly.

# Columns of log.csv: 1 id, 2 when, 3 subject, 4 observation, 5 measure, 6 doubt ...
cut -d, -f3 log.csv | tail -n +2 | sort | uniq -c   # group: entries per subject
grep "example mood" log.csv                          # select: one subject
tail -n +2 log.csv | sort -t, -k2                    # order: by date, header skipped
wc -l < log.csv                                      # count lines (header included)
tail -n 2 log.csv                                    # the latest entries

# git: memory with a timestamp. Run once, in a scratch folder.
if [ "$1" = "--git" ]; then
  git init -q reflections && cp log.csv reflections/ && cd reflections
  git add log.csv
  git -c user.name=me -c user.email=me@example.com commit -q -m "first entries"
  git log --oneline                                  # the history of your thinking
fi
