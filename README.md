# Filler

Filler is a small Python helper for Active Directory labs, CTFs, and other assessments. Give it the target basics once, and it writes an `output.txt` file with common first-pass enumeration commands already filled in for that domain.

Made by [CanYouHackMe](https://canyouhack.me).

Filler also pairs well with the [CYHM Official Notebook](https://github.com/timothyericsson/CYHM-Official-Notebook): generate a target-specific command sheet with Filler, then track results, credentials, paths, and next steps with the notebook.

## What it does

- Creates a target-specific AD enumeration checklist in `output.txt`.
- Supports both unauthenticated and authenticated workflows.
- Prompts for target IP, hostname, domain, and optional credentials.
- Adds extra authenticated checks when a username and password are provided.
- Includes commands for DNS, RID brute forcing, user and group cleanup, Kerbrute, RPC, LDAP, SMB, AS-REP roasting, Kerberoasting, BloodHound CE ingestion, ADCS checks, MSSQL, WinRM, delegation, GPP password checks, coercion checks, and secretsdump.

Filler is intentionally a syntax filler, not a one-click runner. Review the generated commands and run only what applies to your situation. 
## LFI Helper

`lfi_filler.py` prints common files worth checking when you have an LFI primitive and know a Linux username.

```bash
python3 lfi_filler.py alice
```

Example output includes paths under `/home/alice/`, such as SSH keys, shell history files, shell profiles, database client history, and local environment files.

I hope you find this tool useful. 
