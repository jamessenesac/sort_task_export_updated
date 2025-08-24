#!/bin/bash

# move the extraneous files out of the way
mkdir -p blah
mv application* blah/
mv index.html blah/
mv jquery.js blah/
mv bootstrap* blah/

# move the successful/failed jobs out of the way
mkdir -p failure

# For each *.html file, find failures (warning|error) and move them to failure/
for i in $(for j in $(ls); do grep -E -A 1 'Result:' "$j" 2>/dev/null -H | grep -E 'warning|error' | awk '{print $1}' | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g | sort -u; done); do
  mv "$i" failure/
done

mkdir -p success

# For each *.html file, find successes (success|pending) and move them to success/
for i in $(for j in $(ls); do grep -E -A 1 'Result:' "$j" 2>/dev/null -H | grep -E 'success|pending' | awk '{print $1}' | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g | sort -u; done); do
  mv "$i" success/
done

mv *.html success/ 2>/dev/null

# sort the failed tasks by type
cd failure/ || exit 1

# Build list of unique labels (2nd field after 'Label')
SORTLIST=$(grep -E -A 1 'Label' * 2>/dev/null | awk '{print $2}' | grep -Ev 'Label:' | sort -u | grep -E . | sed 's/^[ 	]*//;s/[ 	]*$//')

for j in $SORTLIST; do
  MYDIR=$(echo "$j" | tr -d ':')
  mkdir -p "$MYDIR"

  IFS=$'\n'
  for i in $(grep -E -A 1 'Label:' * 2>/dev/null | grep -E "$j" | awk '{print $1}' | sort -u | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g); do
    mv "$i" "$MYDIR"/
  done
done

# sort the successful tasks by type
cd ../success || exit 1

SORTLIST=$(grep -E -A 1 'Label' * 2>/dev/null | awk '{print $2}' | grep -Ev 'Label:' | sort -u | grep -E . | sed 's/^[ 	]*//;s/[ 	]*$//')

for j in $SORTLIST; do
  MYDIR=$(echo "$j" | tr -d ':')
  mkdir -p "$MYDIR"

  IFS=$'\n'
  for i in $(grep -E -A 1 'Label:' * 2>/dev/null | grep -E "$j" | awk '{print $1}' | sort -u | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g); do
    mv "$i" "$MYDIR"/
  done
done
