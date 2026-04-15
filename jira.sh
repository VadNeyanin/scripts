n=$(cat "$1" | wc -l)
current=$(date -d '-1 day' '+%Y-%m-%d')
current_s=$(date -d "$current" +%s)
start=$current
start_s=$current_s
author[1]=""
author[2]=""
author[3]=""
author[4]=""
author[5]=""
author_ru[1]=""
author_ru[2]=""
author_ru[3]=""
author_ru[4]=""
author_ru[5]=""
echo ";;${author_ru[1]};${author_ru[2]};${author_ru[3]};${author_ru[4]};${author_ru[5]};Другие;" > jira_$(date +%Y-%m-%d).csv
n_author=5
n_weeks=4
for (( i=1; i <= $n_weeks; i++ ))
do
	k=0
	sum[1]=0
        sum[2]=0
        sum[3]=0
        sum[4]=0
        sum[5]=0
	finish=$(date +%Y-%m-%d -d "$start -6 days")
	finish_s=$(date -d "$finish" +%s)
	for (( j=2; j <= $n; j++ ))
	do
		now_table=$(awk -F ';' '{print $10}' "$1" | head -n $j | tail -n 1 | awk -F " " '{print $1}')
		now=$(date -d "$(echo $now_table | awk -F'-' '{print $3"-"$2"-"$1}')" +%s)
		if [ $now -le $start_s ] && [ $now -ge $finish_s ]
		then
			status=$(awk -F ';' '{print $8}' "$1" | head -n $j | tail -n 1 )
			if [[ "$status" == 'Выполнено' ]] || [[ "$status" == 'Закрыта' ]]
			then
				k=$(( k + 1 ))
				author_table=$(awk -F ';' '{print $5}' "$1" | head -n $j | tail -n 1 )
				for (( m=1; m <= $n_author; m++ ))
	        		do
					if [[ "$author_table" == "${author[m]}" ]]
					then
						sum[m]=$(( ${sum[m]} + 1 ))
						sum_all[m]=$(( ${sum_all[m]} + 1 ))
					fi
				done
			else
				n_not_completed=$(( n_not_completed + 1 ))
			fi
		fi
	done
	others_week=$k
	for (( m=1; m <= $n_author; m++ ))
	do
		others_week=$(( others_week - ${sum[m]} ))
	done
	others=$(( others + others_week ))
	echo "Неделя с $finish по $start;$k;${sum[1]};${sum[2]};${sum[3]};${sum[4]};${sum[5]};$others_week;" >> jira_$(date +%Y-%m-%d).csv
	finish=$(date +%Y-%m-%d -d "$finish -1 days")
	start=$finish
	start_s=$(date -d "$start" +%s)
done
echo "Всего;;${sum_all[1]};${sum_all[2]};${sum_all[3]};${sum_all[4]};${sum_all[5]};$others" >> jira_$(date +%Y-%m-%d).csv
echo "Не выполнено;$n_not_completed" >> jira_$(date +%Y-%m-%d).csv
