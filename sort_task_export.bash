#!/bin/bash

# move the extraneous files out of the way

mkdir blah; 

mv application* blah/; 

mv index.html blah/; 

mv jquery.js blah/; 

mv bootstrap* blah/



# move the successful jobs out of the way

mkdir failure

#for i in `egrep -A 1 Result: * 2>/dev/null | egrep "warning|error" | awk '{print $1}' | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g | sort -u`; do mv $i failure/; done
for i in `for j in $(ls); do egrep -A 1 Result: $j 2>/dev/null -H | egrep "warning|error" | awk '{print $1}' | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g | sort -u; done`; do mv $i failure/; done

mkdir success

#for i in `egrep -A 1 Result: * 2>/dev/null | grep success | awk '{print $1}' | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g | sort -u`; do mv $i success/; done
for i in `for j in $(ls); do egrep -A 1 Result: $j 2>/dev/null -H | egrep "success|pending" | awk '{print $1}' | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g | sort -u; done`; do mv $i success/; done

mv *.html success/ 2>/dev/null



# sort the failed tasks by type

cd failure/

#SORTLIST=`egrep -A 1 Label * 2>/dev/null | egrep -v "Label:|\-\-" | awk '{print $2}' | sort -u | grep ':'`
SORTLIST=$(egrep -A 1 Label * 2>/dev/null | awk '{print $2}' | egrep -v Label: | sort -u | egrep . | sed 's/^[ \t]*//;s/[ \t]*$//')

for j in $SORTLIST; do 

	MYDIR=`echo $j | tr -d ':'`;
	mkdir $MYDIR;

	IFS=$'\n';for i in `egrep -A 1 Label: * 2>/dev/null | egrep $j | awk '{print $1}' | sort -u | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g`; do 
		mv $i $MYDIR/; 
	done;

done

# sort the successful tasks by type

cd ../success

#SORTLIST=`egrep -A 1 Label * 2>/dev/null | egrep -v "Label:|\-\-" | awk '{print $2}' | sort -u | grep ':'`
SORTLIST=$(egrep -A 1 Label * 2>/dev/null | awk '{print $2}' | egrep -v Label: | sort -u | egrep . | sed 's/^[ \t]*//;s/[ \t]*$//')

for j in $SORTLIST; do

        MYDIR=`echo $j | tr -d ':'`;
        mkdir $MYDIR;

        IFS=$'\n';for i in `egrep -A 1 Label: * 2>/dev/null | egrep $j | awk '{print $1}' | sort -u | sed s'/.html-/.html/'g | sed s'/.html:/.html/'g`; do
                mv $i $MYDIR/;
        done;

done
