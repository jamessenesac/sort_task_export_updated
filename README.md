# sort_task_export

i like to save the script sort_task_export.bash into my shell path.  then i extract the task export, i cd into it, and then i run these commands to sort each task by category:

\# ln -s tmp/task* task-export; cd task-export; sort_task_export.bash

then i cd down into one of the categories (typically one of the task failure types).  if i'm looking at failures, i less the last task and search for this:

/\.rb

then i arrow up several lines to see the error message, and i use that error message to run this command (replacing  to sort tasks by that error into a subdirectory:

\# mkdir DIRECTORY_NAME;for i in `egrep 'SEARCH PHRASE' * | awk -F":" '{print $1}' | sort -u | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g`; do mv $i DIRECTORY_NAME/; done

i repeat until all of the tasks in that category have been sorted.



