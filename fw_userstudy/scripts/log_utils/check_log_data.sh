username="jhe"
username="mbron"
username="tttest"
username="manos"
#username="dyaaa"
#username="fabrizio"
username="schaer"
. test_get_log_data.sh $username | sed 's/null/"null"/g' | sed "s/false/False/g" | sed "s/true/True/g" | sed "s/^{/data={/g" > tmp2.py

python parse.py
