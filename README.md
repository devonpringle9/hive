# to save all the test files, run pytest, then change all the outputs into the test files
 for f in *; do  variable=$(echo "$f" | gawk -F.actual '{print $1}');  mv $f $variable; done