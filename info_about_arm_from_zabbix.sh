cd "$1"
echo "Имя;Материнка;Процессор;Видеокарта;Принтер;IP-адрес; ;Пользователи;" > ~/info.csv
for archive in $(ls); do
	name="$(echo ${archive: : length -4})"
	tar -xf $archive opt/$name.print
	tar -xf $archive opt/$name.hard
	tar -xf $archive opt/$name.ip
	tar -xf $archive opt/$name.user
	printer=$(cat opt/$name.print | awk "(NR == 1)" | awk '{print $2}')
	start_number_mother=$(cat -n opt/$name.hard | grep "*-core" | awk '{print $1}')
	start_number_processor=$(cat -n opt/$name.hard | grep "*-cpu" | awk '{print $1}')
	start_number_video=$(cat -n opt/$name.hard | grep "*-display" | awk '{print $1}')
	mother_vendor=$(cat opt/$name.hard | awk "(NR == $(( start_number_mother + 3 )))" | awk '{print $2}')
	mother_model=$(cat opt/$name.hard | awk "(NR == $(( start_number_mother + 2 )))" | awk '{for (i=2; i<NF; i++) printf $i " "; print $NF}')
	mother=$(echo "$mother_vendor $mother_model")
	procesor_vendor=$(cat opt/$name.hard | awk "(NR == $(( start_number_processor + 3 )))" | awk '{print $2}')
	processor_model=$(cat opt/$name.hard | awk "(NR == $(( start_number_processor + 2 )))" | awk '{for (i=2; i<NF; i++) printf $i " "; print $NF}')
	processor=$(echo "$processor_vendor $processor_model")
	video_vendor=$(cat opt/$name.hard | awk "(NR == $(( start_number_video + 3 )))" | awk '{print $2}')
	video_model=$(cat opt/$name.hard | awk "(NR == $(( start_number_video + 2 )))" | awk '{for (i=2; i<NF; i++) printf $i " "; print $NF}')
	video=$(echo "$video_vendor $video_model")
	string="$(cat opt/$name.ip)"
	massive=($string)
	ip_adress="${massive[1]}"
	count_of_users=$(wc opt/$name.user | awk '{ptint $2}')
	string="$(cat opt/$name.user)"
	massive=($string)
	count=0
	all="$name;$mother;$processor;$video;$printer;$ip_adress;"
	for user in "${massive[@]}"; do
		all="$all;$user;"
	done
	#all="$name;$mother;$processor;$video;$printer;$ip_adress;" 
	#for ((i=1; i < "$count_of_users"; i++)); do
	#	all="$all;user_$i;"
	#done
	echo $all >> ~/info.csv
	rm -r opt/$name.hard opt/$name.print opt/$name.ip opt/$name.user
done


#string=" Intel(R) Celeron(R) 2957U @ 1.40GHz"
#massive=($string)
#count=0
#for word in "${massive[@]}"; do
#        count=$(( count + 1 )) 
#        if [ "$word" = "Core(TM)" ] || [ "$word" = "Celeron(R)" ]; then
#                family=$word
#                number_family=$count
#        fi
#done 
#echo ${massive[$number_family]}

