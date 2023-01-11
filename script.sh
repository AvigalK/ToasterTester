#!/usr/bin/expect -f
spawn nrfjprog --reset

set prompt "#"
set address [lindex $argv 0]
spawn bluetoothctl
#expect -re $prompt
send "scan on\r"
sleep 7
send "scan off\r"

send "remove $address\r"
send "pair $address\r"
#expect -re $prompt
sleep 2
send "disconnect $address\r"
#send "remove $address\r"
#expect -re $prompt
#send "connect $address\r"
#expect -re $prompt
sleep 2
send "quit\r"
#expect eof
