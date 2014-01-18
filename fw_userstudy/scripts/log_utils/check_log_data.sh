username="jhe"
. test_get_log_data.sh $username | sed 's/null/"null"/g' | sed "s/false/False/g" | sed "s/true/True/g" | sed "s/^{/data={/g" > tmp2.py

python parse.py
