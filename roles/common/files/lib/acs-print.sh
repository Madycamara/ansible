print_term (){
	if [ "$TERM" = "xterm" -o "$TERM" = "screen" ]; then
		echo $1
	fi
}
